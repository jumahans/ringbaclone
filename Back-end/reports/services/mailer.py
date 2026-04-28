import logging
import base64
from datetime import datetime
from django.core.mail import EmailMessage, get_connection
from django.conf import settings

logger = logging.getLogger(__name__)

COMPLAINT_TEMPLATE = """
Dear {carrier_name} Trust & Safety Team,

We are reporting the following toll-free number for fraudulent activity
impersonating {brand}. We request immediate investigation and termination
of service.

REPORTED NUMBER:    {phone_number}
IMPERSONATED BRAND: {brand}
RespOrg ID:         {resporg_code}
LANDING PAGE:       {landing_url}
DATE DETECTED:      {date_detected}
REPORT ID:          {report_id}

Evidence:
This number has been used in active social engineering attacks against
consumers. The landing page (if applicable) has been documented with
screenshot evidence available upon request.

Applicable Law:
- 47 U.S.C. § 228 (Prohibition on Provision of Certain Operator Services)
- FTC Act § 5 (Unfair or Deceptive Acts or Practices)
- TRACED Act (2019) — carrier obligations to combat robocall fraud

We request:
1. Immediate suspension of the number {phone_number}
2. Preservation of all subscriber records for law enforcement
3. Confirmation of action to: {reply_to}

Sincerely,
FraudHunter Portal
Automated Abuse Reporting System
""".strip()


CARRIER_ABUSE_EMAILS = {
    "somosgov": "abuse@somos.com",
    "somosco": "abuse@somos.com",
    "at&t": "abuse@att.net",
    "verizon": "abuse@verizon.com",
    "t-mobile": "abuse@t-mobile.com",
    "tmobile": "abuse@t-mobile.com",
    "lumen": "abuse@lumen.com",
    "bandwidth": "abuse@bandwidth.com",
    "twilio": "abuse@twilio.com",
    "vonage": "abuse@vonage.com",
    "google": "abuse@google.com",
    "telnyx": "abuse@telnyx.com",
    "fractel": "abuse@fractel.net",
    "cx support": "abuse@cxsupport.com",
    "cxsupport": "abuse@cxsupport.com",
}

ALWAYS_CC = [
    "spam@uce.gov",
    "ic3@ic3.gov",
]

BRAND_CC_EMAILS = {
    "amazon": "stop-spoofing@amazon.com",
    "aws": "stop-spoofing@amazon.com",
    "microsoft": "reportphishing@microsoft.com",
    "windows": "reportphishing@microsoft.com",
    "google": "phishing-report@google.com",
    "apple": "reportphishing@apple.com",
    "paypal": "phishing@paypal.com",
    "irs": "phishing@irs.gov",
    "social security": "oig.hotline@ssa.gov",
    "ssa": "oig.hotline@ssa.gov",
    "medicare": "HHSTips@oig.hhs.gov",
    "bank of america": "abuse@bankofamerica.com",
    "chase": "phishing@chase.com",
    "wells fargo": "reportphish@wellsfargo.com",
}

URL_DOMAIN_CC_EMAILS = {
    "amazon.com": "stop-spoofing@amazon.com",
    "microsoft.com": "reportphishing@microsoft.com",
    "google.com": "phishing-report@google.com",
    "apple.com": "reportphishing@apple.com",
    "paypal.com": "phishing@paypal.com",
    "irs.gov": "phishing@irs.gov",
    "chase.com": "phishing@chase.com",
    "wellsfargo.com": "reportphish@wellsfargo.com",
    "bankofamerica.com": "abuse@bankofamerica.com",
}


def get_cc_emails(brand: str, landing_url: str) -> list:
    cc = list(ALWAYS_CC)

    brand_lower = (brand or "").lower()
    for key, email in BRAND_CC_EMAILS.items():
        if key in brand_lower:
            if email not in cc:
                cc.append(email)
            break

    url_lower = (landing_url or "").lower()
    for domain, email in URL_DOMAIN_CC_EMAILS.items():
        if domain in url_lower:
            if email not in cc:
                cc.append(email)
            break

    return cc


def send_resporg_complaint(
    report_id: str,
    phone_number: str,
    brand: str,
    landing_url: str,
    resporg_code: str,
    carrier_name: str,
    abuse_email: str = "",
    to_override: str = "",
    cc_override: list | None = None,
    subject_override: str = "",
    body_override: str = "",
    bcc_override: list | None = None,
    attachments: list | None = None,
) -> tuple[bool, str]:

    # Resolve To address
    recipient = to_override.strip() if to_override else abuse_email.strip()

    if not recipient:
        carrier_lower = carrier_name.lower()
        for key, email in CARRIER_ABUSE_EMAILS.items():
            if key in carrier_lower:
                recipient = email
                logger.info(f"Using known abuse email for {carrier_name}: {recipient}")
                break

    if not recipient:
        return False, "No recipient email address provided or found for this carrier."

    if not settings.EMAIL_HOST_USER:
        return False, "Email not configured in settings."

    reply_to = getattr(settings, 'SCAM_SLAYER_REPLY_EMAIL', None) or settings.DEFAULT_FROM_EMAIL

    # Resolve CC
    if cc_override is not None:
        cc_emails = [e.strip() for e in cc_override if e.strip()]
    else:
        cc_emails = get_cc_emails(brand, landing_url)

    logger.info(f"CC emails for report {report_id}: {cc_emails}")

    # Resolve Subject
    subject = (
        subject_override.strip()
        if subject_override
        else f"[URGENT] Toll-Free Number Abuse — {phone_number}"
    )

    # Resolve Body
    body = (
        body_override.strip()
        if body_override
        else COMPLAINT_TEMPLATE.format(
            abuse_email=recipient,
            phone_number=phone_number,
            brand=brand,
            resporg_code=resporg_code,
            carrier_name=carrier_name,
            landing_url=landing_url or "N/A",
            date_detected=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            reply_to=reply_to,
            report_id=report_id,
        )
    )

    # Send
    try:
        connection = get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_ssl=True,
            use_tls=False,
        )
        bcc_emails = [e.strip() for e in (bcc_override or []) if e.strip()]

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            cc=cc_emails,
            bcc=bcc_emails,
            reply_to=[reply_to],
        )
        email.connection = connection

        for att in (attachments or []):
            try:
                raw = base64.b64decode(att["data"])
                email.attach(att["name"], raw, att["type"])
            except Exception as att_err:
                logger.warning(f"Could not attach {att.get('name')}: {att_err}")

        email.send(fail_silently=False)
        logger.info(
            f"Complaint sent for {phone_number} to {recipient} CC: {cc_emails}"
        )
        return True, f"Complaint sent to {recipient}" + (
            f" with CC to {', '.join(cc_emails)}" if cc_emails else ""
        )
    except Exception as e:
        logger.error(f"Failed to send complaint for {phone_number}: {e}")
        return False, str(e)