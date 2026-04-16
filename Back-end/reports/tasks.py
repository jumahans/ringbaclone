import logging
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

logger = logging.getLogger(__name__)


def broadcast_update(report_data: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "scam_reports",
        {
            "type": "scam_update",
            "data": report_data,
        }
    )


@shared_task
def process_resporg_lookup(report_id: str):
    from reports.models import ScamReport, RespOrg, ReportLog
    from reports.services.resporg import lookup_resporg

    try:
        report = ScamReport.objects.get(id=report_id)
        result = lookup_resporg(report.phone_number)

        report.resporg_raw = result.resporg_code

        if result.resporg_code not in ("UNKNWN", "N/A"):
            resporg_obj, _ = RespOrg.objects.get_or_create(
                code=result.resporg_code,
                defaults={
                    "carrier_name": result.carrier_name,
                    "abuse_email": result.abuse_email,
                    "website": result.website,
                },
            )
            report.resporg = resporg_obj

        report.save()

        ReportLog.objects.create(
            report=report,
            action=ReportLog.Action.RESPORG_LOOKUP,
            detail=f"RespOrg: {result.resporg_code} ({result.carrier_name})",
            success=result.resporg_code != "UNKNWN",
        )

        broadcast_update({
            "id": str(report.id),
            "status": report.status,
            "resporg_raw": report.resporg_raw,
            "carrier_name": result.carrier_name,
        })

    except Exception as e:
        logger.error(f"RespOrg lookup failed for report {report_id}: {e}")


@shared_task
def process_report_complaint(report_id: str):

    from reports.models import ScamReport, ReportLog
    from reports.services.mailer import send_resporg_complaint

    try:
        report = ScamReport.objects.select_related("resporg").get(id=report_id)

        abuse_email = report.resporg.abuse_email if report.resporg else ""
        carrier_name = report.resporg.carrier_name if report.resporg else "Unknown"

        success, message = send_resporg_complaint(
            report_id=str(report.id),
            phone_number=report.phone_number,
            brand=report.brand,
            landing_url=report.landing_url,
            resporg_code=report.resporg_raw,
            carrier_name=carrier_name,
            abuse_email=abuse_email,
        )

        if success:
            report.status = ScamReport.Status.REPORTED
            report.report_sent_at = timezone.now()
        else:
            report.status = ScamReport.Status.FAILED

        report.save()

        ReportLog.objects.create(
            report=report,
            action=ReportLog.Action.EMAIL_SENT,
            detail=message,
            success=success,
        )

        broadcast_update({
            "id": str(report.id),
            "status": report.status,
            "message": message,
        })

    except Exception as e:
        logger.error(f"Complaint failed for report {report_id}: {e}")


@shared_task(time_limit=65, soft_time_limit=60)
def scrape_phone_from_url(url: str, lookup_id: str):
    from reports.services.resporg import extract_phone_from_url, lookup_resporg
    
    phone = extract_phone_from_url(url)
    
    if phone:
        result = lookup_resporg(phone)
        broadcast_update({
            "type": "lookup_result",
            "lookup_id": lookup_id,
            "phone_number": phone,
            "carrier_name": result.carrier_name,
            "resporg_code": result.resporg_code,
            "abuse_email": result.abuse_email,
            "is_toll_free": result.is_toll_free,
        })
    else:
        broadcast_update({
            "type": "lookup_result",
            "lookup_id": lookup_id,
            "phone_number": "",
            "carrier_name": "",
            "resporg_code": "",
            "abuse_email": "",
            "is_toll_free": False,
        })


# Phase 3: Authority Reporting Tasks

@shared_task(time_limit=120, soft_time_limit=90)
def submit_ftc_complaint_task(report_id: str):
    """Submit complaint to FTC via Playwright automation."""
    from reports.models import ScamReport, ReportLog
    from reports.services.automation import submit_ftc_complaint
    
    try:
        report = ScamReport.objects.get(id=report_id)
        
        success, message, screenshot = submit_ftc_complaint(
            phone_number=report.phone_number,
            brand=report.brand or "Unknown",
            landing_url=report.landing_url or "",
        )
        
        if screenshot:
            report.ftc_screenshot = screenshot
            report.save()
        
        ReportLog.objects.create(
            report=report,
            action="FTC_SUBMISSION",
            detail=message,
            success=success,
        )
        
        return {"success": success, "target": "ftc", "message": message}
        
    except Exception as e:
        logger.error(f"FTC submission failed for {report_id}: {e}")
        return {"success": False, "target": "ftc", "message": str(e)}


@shared_task(time_limit=120, soft_time_limit=90)
def submit_ic3_complaint_task(report_id: str):
    """Submit complaint to FBI IC3 via Playwright automation."""
    from reports.models import ScamReport, ReportLog
    from reports.services.automation import submit_ic3_complaint
    
    try:
        report = ScamReport.objects.get(id=report_id)
        
        success, message, screenshot = submit_ic3_complaint(
            phone_number=report.phone_number,
            brand=report.brand or "Unknown",
            landing_url=report.landing_url or "",
        )
        
        if screenshot:
            report.ic3_screenshot = screenshot
            report.save()
        
        ReportLog.objects.create(
            report=report,
            action="IC3_SUBMISSION",
            detail=message,
            success=success,
        )
        
        return {"success": success, "target": "ic3", "message": message}
        
    except Exception as e:
        logger.error(f"IC3 submission failed for {report_id}: {e}")
        return {"success": False, "target": "ic3", "message": str(e)}


@shared_task
def submit_brand_fraud_task(report_id: str):
    """Submit to brand fraud teams (Microsoft, Amazon, etc.)."""
    from reports.models import ScamReport, ReportLog
    from reports.services.automation import submit_microsoft_fraud, submit_amazon_fraud
    
    try:
        report = ScamReport.objects.get(id=report_id)
        brand_lower = (report.brand or "").lower()
        results = []
        
        if "microsoft" in brand_lower or "windows" in brand_lower:
            success, message = submit_microsoft_fraud(
                phone_number=report.phone_number,
                landing_url=report.landing_url or "",
            )
            ReportLog.objects.create(
                report=report,
                action="MICROSOFT_FRAUD_REPORT",
                detail=message,
                success=success,
            )
            results.append({"target": "microsoft", "success": success, "message": message})
            
        elif "amazon" in brand_lower or "aws" in brand_lower:
            success, message = submit_amazon_fraud(
                phone_number=report.phone_number,
                landing_url=report.landing_url or "",
            )
            ReportLog.objects.create(
                report=report,
                action="AMAZON_FRAUD_REPORT",
                detail=message,
                success=success,
            )
            results.append({"target": "amazon", "success": success, "message": message})
        
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Brand fraud submission failed for {report_id}: {e}")
        return {"results": [], "error": str(e)}


@shared_task
def submit_google_safebrowsing_task(report_id: str):
    """Submit phishing URL to Google Safe Browsing."""
    from reports.models import ScamReport, ReportLog
    from reports.services.automation import submit_google_safebrowsing
    
    try:
        report = ScamReport.objects.get(id=report_id)
        
        if not report.landing_url:
            return {"success": False, "target": "google", "message": "No URL provided"}
        
        success, message = submit_google_safebrowsing(report.landing_url)
        
        ReportLog.objects.create(
            report=report,
            action="GOOGLE_SAFEBROWSING",
            detail=message,
            success=success,
        )
        
        return {"success": success, "target": "google", "message": message}
        
    except Exception as e:
        logger.error(f"Google Safe Browsing submission failed for {report_id}: {e}")
        return {"success": False, "target": "google", "message": str(e)}


@shared_task
def submit_to_authorities(report_id: str):
    """
    Phase 3: Submit to all authorities in parallel.
    Dispatches individual tasks for FTC, IC3, brand teams, and Google.
    """
    from reports.models import ScamReport, ReportLog
    
    try:
        report = ScamReport.objects.get(id=report_id)
        
        # Dispatch all authority submissions in parallel
        ftc_task = submit_ftc_complaint_task.delay(report_id)
        ic3_task = submit_ic3_complaint_task.delay(report_id)
        brand_task = submit_brand_fraud_task.delay(report_id)
        google_task = submit_google_safebrowsing_task.delay(report_id)
        
        # Log that submissions were initiated
        ReportLog.objects.create(
            report=report,
            action="AUTHORITY_SUBMISSIONS_INITIATED",
            detail=f"Tasks dispatched: FTC({ftc_task.id}), IC3({ic3_task.id}), Brand({brand_task.id}), Google({google_task.id})",
            success=True,
        )
        
        broadcast_update({
            "id": str(report.id),
            "status": report.status,
            "message": "Authority submissions initiated",
        })
        
    except Exception as e:
        logger.error(f"Authority submissions failed for {report_id}: {e}")