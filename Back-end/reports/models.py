from django.db import models
import uuid

from authentication.models import User

class RespOrg(models.Model):
    code = models.CharField(max_length=10, unique=True)
    carrier_name = models.CharField(max_length=200)
    abuse_email = models.EmailField()
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.carrier_name}"

    class Meta:
        db_table = "resporg"


class ScamReport(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REPORTED = "reported", "Reported"
        KILLED = "killed", "Killed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign_id = models.CharField(max_length=200, blank=True)
    brand = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    landing_url = models.URLField(blank=True)
    resporg = models.ForeignKey(
        RespOrg, null=True, blank=True, on_delete=models.SET_NULL, related_name="reports"
    )
    resporg_raw = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    screenshot_path = models.CharField(max_length=500, blank=True)
    report_sent_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    ftc_screenshot = models.CharField(max_length=500, blank=True, null=True, default="")
    ic3_screenshot = models.CharField(max_length=500, blank=True, null=True, default="")
    ic3_screenshot_b64 = models.TextField(blank=True, null=True, default="")
    submitted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="reports")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    reporter_first_name = models.CharField(max_length=100, blank=True)
    reporter_last_name = models.CharField(max_length=100, blank=True)
    reporter_address = models.CharField(max_length=200, blank=True)
    reporter_address2 = models.CharField(max_length=200, blank=True)
    reporter_city = models.CharField(max_length=100, blank=True)
    reporter_state = models.CharField(max_length=100, blank=True)
    reporter_zip = models.CharField(max_length=20, blank=True)
    reporter_phone = models.CharField(max_length=20, blank=True)
    reporter_email = models.EmailField(blank=True)
    


    class Meta:
        db_table = "scam_report"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} | {self.phone_number} | {self.status}"


class ReportLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        RESPORG_LOOKUP = "resporg_lookup", "RespOrg Lookup"
        EMAIL_SENT = "email_sent", "Email Sent"
        STATUS_CHANGED = "status_changed", "Status Changed"
        SCREENSHOT_SAVED = "screenshot_saved", "Screenshot Saved"

    report = models.ForeignKey(ScamReport, on_delete=models.CASCADE, related_name="logs")
    action = models.CharField(max_length=50, choices=Action.choices)
    detail = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_log"
        ordering = ["-created_at"]



class SentEmail(models.Model):
    class EmailType(models.TextChoices):
        ABUSE_COMPLAINT = "abuse_complaint", "Abuse Complaint"
        FTC_REPORT = "ftc_report", "FTC Report"
        IC3_REPORT = "ic3_report", "IC3 Report"
        CARRIER_ABUSE = "carrier_abuse", "Carrier Abuse"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(ScamReport, on_delete=models.CASCADE, related_name="sent_emails")
    email_type = models.CharField(max_length=50, choices=EmailType.choices)
    recipient = models.EmailField()
    cc_recipients = models.TextField(blank=True, help_text="Comma-separated email addresses")
    subject = models.CharField(max_length=500)
    body_preview = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default="sent", choices=[("sent", "Sent"), ("failed", "Failed")])
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sent_email"
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.email_type} to {self.recipient} at {self.sent_at}"