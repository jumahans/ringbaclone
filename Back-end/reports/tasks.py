import logging
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


def process_resporg_lookup(report_id: str):
    from reports.models import ScamReport, RespOrg, ReportLog
    from reports.services.resporg import lookup_resporg

    try:
        report = ScamReport.objects.get(id=report_id)
        result = lookup_resporg(report.phone_number)

        report.resporg_raw = result.carrier_name

        if result.carrier_name and result.carrier_name not in ("Unknown Carrier", "N/A", "Auth Failed", "Timeout", "Connection Error"):
            resporg_obj, _ = RespOrg.objects.get_or_create(
                code=result.carrier_name,
                defaults={
                    "carrier_name": result.carrier_name,
                    "abuse_email": "",
                    "website": "",
                },
            )
            report.resporg = resporg_obj

        report.save()

        ReportLog.objects.create(
            report=report,
            action=ReportLog.Action.RESPORG_LOOKUP,
            detail=f"Carrier: {result.carrier_name}",
            success=True,
        )

        broadcast_update({
            "id": str(report.id),
            "status": report.status,
            "resporg_raw": report.resporg_raw,
            "carrier_name": result.carrier_name,
        })

    except Exception as e:
        logger.error(f"RespOrg lookup failed for report {report_id}: {e}", exc_info=True)



def process_report_complaint(report_id: str):
    import time
    from reports.models import ScamReport, ReportLog
    from reports.services.mailer import send_resporg_complaint, CARRIER_ABUSE_EMAILS

    time.sleep(5)
    try:
        report = ScamReport.objects.select_related("resporg").get(id=report_id)

        abuse_email = report.resporg.abuse_email if report.resporg else ""
        carrier_name = report.resporg.carrier_name if report.resporg else ""
        logger.error(f"COMPLAINT DEBUG — resporg={report.resporg}, carrier={carrier_name}, resporg_raw={report.resporg_raw}")

        if not carrier_name:
            carrier_name = report.resporg_raw or "Unknown"

        # If no abuse email, try to find from carrier name
        if not abuse_email and carrier_name:
            carrier_lower = carrier_name.lower()
            for key, email in CARRIER_ABUSE_EMAILS.items():
                if key in carrier_lower:
                    abuse_email = email
                    logger.info(f"Found abuse email for {carrier_name}: {abuse_email}")
                    break

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


# (time_limit=120, soft_time_limit=110)
# def scrape_phone_from_url(url: str, lookup_id: str):
#     from reports.services.resporg import extract_phone_from_url, lookup_resporg
    
#     phone = extract_phone_from_url(url)
    
#     if phone:
#         result = lookup_resporg(phone)
#         broadcast_update({
#             "type": "lookup_result",
#             "lookup_id": lookup_id,
#             "phone_number": phone,
#             "carrier_name": result.carrier_name,
#             "resporg_code": result.resporg_code,
#             "abuse_email": result.abuse_email,
#             "is_toll_free": result.is_toll_free,
#         })
#     else:
#         broadcast_update({
#             "type": "lookup_result",
#             "lookup_id": lookup_id,
#             "phone_number": "",
#             "carrier_name": "",
#             "resporg_code": "",
#             "abuse_email": "",
#             "is_toll_free": False,
#         })

import threading

def run_scrape_in_background(url: str, lookup_id: str):
    def scrape():
        from reports.services.resporg import extract_phone_from_url, lookup_resporg
        from django.core.cache import cache

        logger.info(f"[SCRAPE] Starting scrape for URL: {url}")

        phone = extract_phone_from_url(url)
        if phone == "__PAGE_DOWN__":
            logger.warning(f"[SCRAPE] Ad brought down: {url}")
            cache.set(f"lookup_{lookup_id}", {
                "done": True,
                "page_status": "down",
                "phone_number": "",
                "carrier_name": "", "resporg_code": "", "abuse_email": "",
                "is_toll_free": False, "line_type": "", "is_valid": False,
                "is_voip": False, "country": "", "region": "", "city": "",
                "timezone": "", "international_format": "", "national_format": "",
                "risk_level": "", "is_disposable": False, "is_abuse_detected": False,
                "line_status": "", "sms_email": "", "sms_domain": "", "mcc": "", "mnc": "",
            }, timeout=300)
            return

        if phone:
            logger.info(f"[SCRAPE] Phone found: {phone} — running IPQS lookup")
            result = lookup_resporg(phone)
            logger.info(f"[SCRAPE] Lookup complete: carrier={result.carrier_name}")
            cache.set(f"lookup_{lookup_id}", {
                "done": True,
                "phone_number": phone,
                "carrier_name": result.carrier_name,
                "resporg_code": result.resporg_code,
                "abuse_email": result.abuse_email,
                "is_toll_free": result.is_toll_free,
                "line_type": result.line_type,
                "is_valid": result.is_valid,
                "is_voip": result.is_voip or False,
                "country": result.country,
                "region": result.region,
                "city": result.city,
                "timezone": result.timezone,
                "international_format": result.international_format or "",
                "national_format": result.national_format or "",
                "risk_level": result.risk_level,
                "is_disposable": result.is_disposable or False,
                "is_abuse_detected": result.is_abuse_detected or False,
                "line_status": result.line_status,
                "sms_email": result.sms_email,
                "sms_domain": result.sms_domain,
                "mcc": result.mcc,
                "mnc": result.mnc,
                "page_status": "active",
                
            }, timeout=300)
        else:
            logger.warning(f"[SCRAPE] No phone number found on page: {url}")
            cache.set(f"lookup_{lookup_id}", {
                "done": True,
                "phone_number": "",
                "carrier_name": "",
                "resporg_code": "",
                "abuse_email": "",
                "is_toll_free": False,
                "line_type": "",
                "is_valid": False,
                "is_voip": False,
                "country": "",
                "region": "",
                "city": "",
                "timezone": "",
                "international_format": "",
                "national_format": "",
                "risk_level": "",
                "is_disposable": False,
                "is_abuse_detected": False,
                "line_status": "",
                "sms_email": "",
                "sms_domain": "",
                "mcc": "",
                "mnc": "",
                "page_status" : "active",
            }, timeout=300)

    thread = threading.Thread(target=scrape, daemon=True)
    thread.start()
# Phase 3: Authority Reporting Tasks

# (time_limit=120, soft_time_limit=90)
# def submit_ftc_complaint_task(report_id: str):
#     """Submit complaint to FTC via Playwright automation."""
#     from reports.models import ScamReport, ReportLog
#     from reports.services.automation import submit_ftc_complaint
    
#     try:
#         report = ScamReport.objects.get(id=report_id)
        
#         success, message, screenshot = submit_ftc_complaint(
#             phone_number=report.phone_number,
#             brand=report.brand or "Unknown",
#             landing_url=report.landing_url or "",
#         )
        
#         if screenshot:
#             report.ftc_screenshot = screenshot
#             report.save()
        
#         ReportLog.objects.create(
#             report=report,
#             action="FTC_SUBMISSION",
#             detail=message,
#             success=success,
#         )
        
#         return {"success": success, "target": "ftc", "message": message}
        
#     except Exception as e:
#         logger.error(f"FTC submission failed for {report_id}: {e}")
#         return {"success": False, "target": "ftc", "message": str(e)}


# (time_limit=120, soft_time_limit=90)
# def submit_ic3_complaint_task(report_id: str):
#     """Submit complaint to FBI IC3 via Playwright automation."""
#     from reports.models import ScamReport, ReportLog
#     from reports.services.automation import submit_ic3_complaint
    
#     try:
#         report = ScamReport.objects.get(id=report_id)
        
#         success, message, screenshot = submit_ic3_complaint(
#             phone_number=report.phone_number,
#             brand=report.brand or "Unknown",
#             landing_url=report.landing_url or "",
#         )
        
#         if screenshot:
#             report.ic3_screenshot = screenshot
#             report.save()
        
#         ReportLog.objects.create(
#             report=report,
#             action="IC3_SUBMISSION",
#             detail=message,
#             success=success,
#         )
        
#         return {"success": success, "target": "ic3", "message": message}
        
#     except Exception as e:
#         logger.error(f"IC3 submission failed for {report_id}: {e}")
#         return {"success": False, "target": "ic3", "message": str(e)}


# 
# def submit_brand_fraud_task(report_id: str):
#     """Submit to brand fraud teams (Microsoft, Amazon, etc.)."""
#     from reports.models import ScamReport, ReportLog
#     from reports.services.automation import submit_microsoft_fraud, submit_amazon_fraud
    
#     try:
#         report = ScamReport.objects.get(id=report_id)
#         brand_lower = (report.brand or "").lower()
#         results = []
        
#         if "microsoft" in brand_lower or "windows" in brand_lower:
#             success, message = submit_microsoft_fraud(
#                 phone_number=report.phone_number,
#                 landing_url=report.landing_url or "",
#             )
#             ReportLog.objects.create(
#                 report=report,
#                 action="MICROSOFT_FRAUD_REPORT",
#                 detail=message,
#                 success=success,
#             )
#             results.append({"target": "microsoft", "success": success, "message": message})
            
#         elif "amazon" in brand_lower or "aws" in brand_lower:
#             success, message = submit_amazon_fraud(
#                 phone_number=report.phone_number,
#                 landing_url=report.landing_url or "",
#             )
#             ReportLog.objects.create(
#                 report=report,
#                 action="AMAZON_FRAUD_REPORT",
#                 detail=message,
#                 success=success,
#             )
#             results.append({"target": "amazon", "success": success, "message": message})
        
#         return {"results": results}
        
#     except Exception as e:
#         logger.error(f"Brand fraud submission failed for {report_id}: {e}")
#         return {"results": [], "error": str(e)}


# 
# def submit_google_safebrowsing_task(report_id: str):
#     """Submit phishing URL to Google Safe Browsing."""
#     from reports.models import ScamReport, ReportLog
#     from reports.services.automation import submit_google_safebrowsing
    
#     try:
#         report = ScamReport.objects.get(id=report_id)
        
#         if not report.landing_url:
#             return {"success": False, "target": "google", "message": "No URL provided"}
        
#         success, message = submit_google_safebrowsing(report.landing_url)
        
#         ReportLog.objects.create(
#             report=report,
#             action="GOOGLE_SAFEBROWSING",
#             detail=message,
#             success=success,
#         )
        
#         return {"success": success, "target": "google", "message": message}
        
#     except Exception as e:
#         logger.error(f"Google Safe Browsing submission failed for {report_id}: {e}")
#         return {"success": False, "target": "google", "message": str(e)}

def submit_to_authorities(report_id: str):
    from reports.models import ScamReport, ReportLog
    from reports.services.automation import (
        submit_ftc_complaint,
        submit_ic3_complaint,
        submit_microsoft_fraud,
        submit_amazon_fraud,
        submit_google_safebrowsing,
    )

    try:
        report = ScamReport.objects.get(id=report_id)
        brand_lower = (report.brand or "").lower()

        def run_ftc():
            try:
                success, message, screenshot = submit_ftc_complaint(
                    phone_number=report.phone_number,
                    brand=report.brand or "Unknown",
                    landing_url=report.landing_url or "",
                    description=report.description or "",
                    reporter_first_name=report.reporter_first_name,
                    reporter_last_name=report.reporter_last_name,
                    reporter_address=report.reporter_address,
                    reporter_address2=getattr(report, 'reporter_address2', None),
                    reporter_city=report.reporter_city,
                    reporter_state=report.reporter_state,
                    reporter_zip=report.reporter_zip,
                    reporter_phone=report.reporter_phone,
                    reporter_email=report.reporter_email,
                )
                if screenshot:
                    report.ftc_screenshot = screenshot
                    report.save()
                ReportLog.objects.create(report=report, action="FTC_SUBMISSION", detail=message, success=success)
            except Exception as e:
                logger.error(f"FTC failed: {e}", exc_info=True)

        def run_ic3():
            try:
                success, message, screenshot = submit_ic3_complaint(
                    phone_number=report.phone_number,
                    brand=report.brand or "Unknown",
                    landing_url=report.landing_url or "",
                    reporter_first_name=report.reporter_first_name,
                    reporter_last_name=report.reporter_last_name,
                    reporter_address=report.reporter_address,
                    reporter_city=report.reporter_city,
                    reporter_state=report.reporter_state,
                    reporter_zip=report.reporter_zip,
                    reporter_phone=report.reporter_phone,
                    reporter_email=report.reporter_email,
                )
                if screenshot:
                    report.ic3_screenshot = screenshot
                    report.save()
                ReportLog.objects.create(report=report, action="IC3_SUBMISSION", detail=message, success=success)
            except Exception as e:
                logger.error(f"IC3 failed: {e}", exc_info=True)

        def run_brand():
            try:
                if "microsoft" in brand_lower or "windows" in brand_lower:
                    success, message = submit_microsoft_fraud(report.phone_number, report.landing_url or "")
                    ReportLog.objects.create(report=report, action="MICROSOFT_FRAUD_REPORT", detail=message, success=success)
                elif "amazon" in brand_lower or "aws" in brand_lower:
                    success, message = submit_amazon_fraud(report.phone_number, report.landing_url or "")
                    ReportLog.objects.create(report=report, action="AMAZON_FRAUD_REPORT", detail=message, success=success)
            except Exception as e:
                logger.error(f"Brand fraud failed: {e}", exc_info=True)

        def run_google():
            try:
                if report.landing_url:
                    success, message = submit_google_safebrowsing(report.landing_url)
                    ReportLog.objects.create(report=report, action="GOOGLE_SAFEBROWSING", detail=message, success=success)
            except Exception as e:
                logger.error(f"Google failed: {e}", exc_info=True)

        for t in [
            threading.Thread(target=run_ftc, daemon=True),
            threading.Thread(target=run_ic3, daemon=True),
            threading.Thread(target=run_brand, daemon=True),
            threading.Thread(target=run_google, daemon=True),
        ]:
            t.start()

        ReportLog.objects.create(
            report=report,
            action="AUTHORITY_SUBMISSIONS_INITIATED",
            detail="FTC, IC3, Brand, Google submissions initiated",
            success=True,
        )

        broadcast_update({
            "id": str(report.id),
            "status": report.status,
            "message": "Authority submissions initiated",
        })

    except Exception as e:
        logger.error(f"Authority submissions failed for {report_id}: {e}", exc_info=True)