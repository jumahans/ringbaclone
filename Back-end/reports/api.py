import os
from typing import Optional
from uuid import UUID
from datetime import timedelta

from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from authentication.api import AuthBearer

from reports.models import ScamReport, RespOrg, ReportLog
from reports.schemas import (
    ScamReportIn,
    ScamReportOut,
    ScamReportDetail,
    StatsOut,
    ReportActionOut,
    PaginatedReports,
    LookupIn,
)
from reports.tasks import process_resporg_lookup, process_report_complaint, submit_to_authorities
from reports.services.resporg import lookup_resporg, extract_phone_from_url, normalize_phone, extract_campaign_data

router = Router()
auth = AuthBearer()

@router.get("/stats", response=StatsOut, auth=auth, tags=["Dashboard"])
def get_stats(request):
    qs = ScamReport.objects.all()
    week_ago = timezone.now() - timedelta(days=7)
    return {
        "total": qs.count(),
        "pending": qs.filter(status="pending").count(),
        "reported": qs.filter(status="reported").count(),
        "killed": qs.filter(status="killed").count(),
        "failed": qs.filter(status="failed").count(),
        "this_week": qs.filter(created_at__gte=week_ago).count(),
    }


@router.get("/reports", response=PaginatedReports, auth=auth, tags=["Reports"])
def list_reports(
    request,
    page: int = 1,
    page_size: int = 25,
    status: Optional[str] = None,
    search: Optional[str] = None,
):
    qs = ScamReport.objects.select_related("resporg").all()

    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(
            Q(phone_number__icontains=search)
            | Q(brand__icontains=search)
            | Q(landing_url__icontains=search)
        )

    total = qs.count()
    start = (page - 1) * page_size
    results = list(qs[start: start + page_size])

    return {"total": total, "page": page, "page_size": page_size, "results": results}


@router.post("/reports", response=ScamReportOut, auth=auth, tags=["Reports"])
def create_report(request, payload: ScamReportIn):
    import re
    from reports.services.resporg import extract_phone_from_url

    digits = re.sub(r"\D", "", payload.phone_number) if payload.phone_number else ""

    if not digits and payload.landing_url:
        digits = extract_phone_from_url(payload.landing_url)

    if not digits:
        from ninja.errors import HttpError
        raise HttpError(400, "Could not find a toll-free number. Please enter it manually.")

    report = ScamReport.objects.create(
        brand=payload.brand,
        phone_number=digits,
        landing_url=payload.landing_url or "",
        notes=payload.notes or "",
        submitted_by=payload.submitted_by or "api",
        status=ScamReport.Status.PENDING,
    )

    ReportLog.objects.create(
        report=report,
        action=ReportLog.Action.CREATED,
        detail=f"Submitted by {payload.submitted_by}",
    )

    process_resporg_lookup.delay(str(report.id))

    report.refresh_from_db()
    return report

@router.get("/reports/{report_id}", response=ScamReportDetail, auth=auth, tags=["Reports"])
def get_report(request, report_id: UUID):
    report = get_object_or_404(ScamReport.objects.select_related("resporg"), id=report_id)
    logs = report.logs.all()[:20]
    return {
        "id": report.id,
        "brand": report.brand,
        "phone_number": report.phone_number,
        "landing_url": report.landing_url,
        "resporg_raw": report.resporg_raw,
        "resporg": report.resporg,
        "status": report.status,
        "report_sent_at": report.report_sent_at,
        "screenshot_path": report.screenshot_path,
        "notes": report.notes,
        "submitted_by": report.submitted_by,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
        "logs": list(logs),
    }


@router.post("/reports/{report_id}/report", response=ReportActionOut, auth=auth, tags=["Actions"])
def trigger_report(request, report_id: UUID):
    """Trigger all reports: carrier + authorities (Phase 3)."""
    report = get_object_or_404(ScamReport, id=report_id)

    if report.status == ScamReport.Status.KILLED:
        return {
            "success": False,
            "message": "Report already killed.",
            "report_id": report.id,
            "new_status": report.status,
        }

    # Phase 1 & 2: Carrier abuse email
    process_report_complaint.delay(str(report.id))
    
    # Phase 3: Authorities (FTC, IC3, brand teams, Google)
    submit_to_authorities.delay(str(report.id))

    return {
        "success": True,
        "message": "Report queued for carrier and authority submission.",
        "report_id": report.id,
        "new_status": report.status,
    }


@router.post("/reports/{report_id}/kill", response=ReportActionOut, auth=auth, tags=["Actions"])
def kill_report(request, report_id: UUID):
    report = get_object_or_404(ScamReport, id=report_id)
    report.status = ScamReport.Status.KILLED
    report.save()

    ReportLog.objects.create(
        report=report,
        action=ReportLog.Action.STATUS_CHANGED,
        detail="Marked as KILLED by operator",
    )

    return {
        "success": True,
        "message": f"Report marked as killed.",
        "report_id": report.id,
        "new_status": report.status,
    }


@router.patch("/reports/{report_id}/status", response=ReportActionOut, auth=auth, tags=["Actions"])
def update_status(request, report_id: UUID, status: str):
    valid = [s.value for s in ScamReport.Status]
    if status not in valid:
        from ninja.errors import HttpError
        raise HttpError(400, f"Invalid status. Must be one of: {valid}")

    report = get_object_or_404(ScamReport, id=report_id)
    old_status = report.status
    report.status = status
    report.save()

    ReportLog.objects.create(
        report=report,
        action=ReportLog.Action.STATUS_CHANGED,
        detail=f"Status changed from {old_status} to {status}",
    )

    return {
        "success": True,
        "message": f"Status updated to {status}",
        "report_id": report.id,
        "new_status": status,
    }

@router.post("/lookup", auth=auth, tags=["Lookup"])
def lookup(request, payload: LookupIn):
    import uuid

    user_input = payload.input.strip()
    is_url = payload.is_url

    # PHONE NUMBER: Direct Twilio lookup, NO CELERY
    if not is_url:
        phone = normalize_phone(user_input)
        result = lookup_resporg(phone)  # Direct call, instant response
        
        return {
            "lookup_id": "",
            "phone_number": phone,
            "carrier_name": result.carrier_name,
            "resporg_code": result.resporg_code,
            "abuse_email": result.abuse_email,
            "landing_url": "",
            "is_toll_free": result.is_toll_free,
            "campaign_id": "",
            "domain": "",
            "scraping": False,  # No scraping needed for phone
        }
    
    # URL: Campaign data direct, phone scraping via CELERY
    else:
        campaign_data = extract_campaign_data(user_input)  # Direct, no Celery
        lookup_id = str(uuid.uuid4())
        
        # Fire Playwright scraping in background via Celery ONLY
        from reports.tasks import scrape_phone_from_url
        scrape_phone_from_url.delay(user_input, lookup_id)
        
        return {
            "lookup_id": lookup_id,
            "phone_number": "",
            "carrier_name": "",
            "resporg_code": "",
            "abuse_email": "",
            "landing_url": user_input,
            "is_toll_free": False,
            "campaign_id": campaign_data.get("campaign_id", ""),
            "domain": campaign_data.get("domain", ""),
            "scraping": True,  # Frontend waits for WebSocket
        }