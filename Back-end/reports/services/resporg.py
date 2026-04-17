import re
import os
import sys
import subprocess
import logging
import tempfile
import json
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs

import requests as req

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

TIMEOUT_ABSTRACT = 10
TIMEOUT_PLAYWRIGHT = 60


@dataclass
class RespOrgResult:
    resporg_code: str
    carrier_name: str
    abuse_email: str
    website: str
    is_toll_free: bool
    line_type: str = ""
    is_valid: bool = False
    is_voip: bool = False
    country: str = ""
    region: str = ""
    city: str = ""
    timezone: str = ""
    international_format: str = ""
    national_format: str = ""
    risk_level: str = ""
    is_disposable: bool = False
    is_abuse_detected: bool = False
    line_status: str = ""
    sms_email: str = ""
    sms_domain: str = ""
    mcc: str = ""
    mnc: str = ""


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    logger.debug(f"normalize_phone: input={repr(phone)} → digits={repr(digits)}")
    return digits


def lookup_resporg(phone: str) -> RespOrgResult:
    """Lookup carrier using Abstract API phone validation."""
    digits = normalize_phone(phone)
    e164 = f"1{digits}"
    logger.debug(f"lookup_resporg: normalized E.164 = {e164}")

    api_key = os.getenv("ABSTRACT_API_KEY")
    logger.error(f"ABSTRACT API KEY LOADED : {repr(api_key)}")
    if not api_key:
        logger.error("ABSTRACT_API_KEY is not set in environment.")
        return RespOrgResult("", "Unknown Carrier", "", "", False)

    url = "https://phoneintelligence.abstractapi.com/v1/"
    params = {
        "api_key": api_key,
        "phone": e164,
    }

    try:
        response = req.get(url, params=params, timeout=TIMEOUT_ABSTRACT)
        logger.debug(f"HTTP Status: {response.status_code}")

        if response.status_code == 401:
            logger.error("Abstract API returned 401 — check your ABSTRACT_API_KEY.")
            return RespOrgResult("", "Auth Failed", "", "", False)

        if response.status_code == 422:
            logger.error(f"Abstract API returned 422 — invalid phone number: {e164}")
            return RespOrgResult("", "Invalid Number", "", "", False)

        response.raise_for_status()
        data = response.json()
        logger.error(f"FULL API RESPONSE: {response.text}")

        phone_carrier = data.get("phone_carrier", {})
        phone_validation = data.get("phone_validation", {})
        phone_location = data.get("phone_location", {})
        phone_format = data.get("phone_format", {})
        phone_risk = data.get("phone_risk", {})
        phone_messaging = data.get("phone_messaging", {})

        carrier = phone_carrier.get("name", "Unknown Carrier")
        line_type = phone_carrier.get("line_type", "")
        mcc = str(phone_carrier.get("mcc", ""))
        mnc = str(phone_carrier.get("mnc", ""))

        is_valid = phone_validation.get("is_valid", False)
        line_status = phone_validation.get("line_status", "")
        is_voip = phone_validation.get("is_voip", False)

        country = phone_location.get("country_name", "")
        region = phone_location.get("region", "")
        city = phone_location.get("city", "")
        timezone = phone_location.get("timezone", "")

        international_format = phone_format.get("international", "")
        national_format = phone_format.get("national", "")

        risk_level = phone_risk.get("risk_level", "")
        is_disposable = phone_risk.get("is_disposable", False)
        is_abuse_detected = phone_risk.get("is_abuse_detected", False)

        sms_domain = phone_messaging.get("sms_domain", "")
        sms_email = phone_messaging.get("sms_email", "")

        is_toll_free = line_type.lower() in ("toll_free", "tollfree") if line_type else False

        logger.info(
            f"Result for {e164}: carrier={carrier!r}, "
            f"type={line_type!r}, valid={is_valid}, is_toll_free={is_toll_free}"
        )

        return RespOrgResult(
            resporg_code="",
            carrier_name=carrier,
            abuse_email="",
            website="",
            is_toll_free=is_toll_free,
            line_type=line_type,
            is_valid=is_valid,
            is_voip=is_voip,
            country=country,
            region=region,
            city=city,
            timezone=timezone,
            international_format=international_format,
            national_format=national_format,
            risk_level=risk_level,
            is_disposable=is_disposable,
            is_abuse_detected=is_abuse_detected,
            line_status=line_status,
            sms_email=sms_email,
            sms_domain=sms_domain,
            mcc=mcc,
            mnc=mnc,
        )

    except req.exceptions.Timeout:
        logger.error(f"Abstract API request timed out after {TIMEOUT_ABSTRACT}s for {e164}")
        return RespOrgResult("", "Timeout", "", "", False)

    except req.exceptions.ConnectionError as e:
        logger.error(f"Network connection error: {e}")
        return RespOrgResult("", "Connection Error", "", "", False)

    except req.exceptions.HTTPError as e:
        logger.error(f"Abstract API HTTP error: {e}")
        return RespOrgResult("", "HTTP Error", "", "", False)

    except Exception as e:
        logger.exception(f"Unexpected error during Abstract API lookup for {e164}: {e}")
        return RespOrgResult("", "Unknown Carrier", "", "", False)


def extract_phone_from_url(url: str) -> str:
    """Extract toll-free number from URL using Playwright."""
    script = '''
import sys, json, re
from playwright.sync_api import sync_playwright

with open(sys.argv[1]) as f:
    url = json.load(f)["url"]

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-gpu",
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
        locale="en-US",
    )
    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    try:
        page.goto(url, timeout=20000, wait_until="networkidle")
        page.wait_for_timeout(2000)

        try:
            proceed = page.locator("text=Ignore & Proceed")
            if proceed.count() > 0:
                proceed.click()
                page.wait_for_timeout(3000)
        except:
            pass

        text = page.inner_text("body")
    except Exception as e:
        text = ""
    browser.close()

matches = re.findall(
    r'1?[-.\\s]?\\(?(800|833|844|855|866|877|888)\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}',
    text
)
if matches:
    full = re.search(
        r'1?[-.\\s]?\\(?(800|833|844|855|866|877|888)\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}',
        text
    )
    print(re.sub(r'\\D', '', full.group()) if full else "")
else:
    print("")
'''

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"url": url}, f)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, "-c", script, tmp_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_PLAYWRIGHT,
        )
        os.unlink(tmp_path)

        phone = result.stdout.strip()
        if phone:
            return phone
        if result.stderr:
            logger.error(f"Playwright subprocess error: {result.stderr}")
        return ""
    except Exception as e:
        logger.error(f"Playwright extraction failed for {url}: {e}")
        return ""


def extract_campaign_data(url: str) -> dict:
    """Extract campaign ID and other tracking params from URL."""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        campaign_id_keys = [
            "bcid", "cid", "campaign_id", "gad_campaignid", "campaignid",
            "utm_campaign", "campaign", "click_id", "clickid", "aff_id",
            "subid", "sub_id", "ref", "source", "track", "tracking",
            "event", "_event", "session", "session_id", "visitor",
            "pid", "aid", "oid", "tid", "sid", "mid", "gid",
            "adid", "ad_id", "creative", "keyword", "matchtype",
            "device", "placement", "network", "target", "audience",
            "fbclid", "gclid", "wbraid", "gbraid", "msclkid",
            "utm_source", "utm_medium", "utm_content", "utm_term",
        ]

        campaign_id = ""
        for key in campaign_id_keys:
            if key in params:
                campaign_id = params[key][0]
                break

        if not campaign_id:
            for key, values in params.items():
                value = values[0]
                if len(value) > 8 and any(c.isdigit() for c in value):
                    campaign_id = value
                    break

        phone_in_url = ""
        url_text = url.replace("-", "").replace(" ", "")
        phone_match = re.search(r'(1?)([2-9]\d{2})(\d{3})(\d{4})', url_text)
        if phone_match:
            phone_in_url = phone_match.group(0)

        return {
            "campaign_id": campaign_id,
            "lp_key": params.get("lpkey", [""])[0],
            "full_url": url,
            "domain": parsed.netloc,
            "path": parsed.path,
            "phone_in_url": phone_in_url,
            "all_params": {k: v[0] for k, v in params.items()},
        }
    except Exception as e:
        logger.error(f"Campaign data extraction failed: {e}")
        return {
            "campaign_id": "",
            "lp_key": "",
            "full_url": url,
            "domain": "",
            "path": "",
            "phone_in_url": "",
            "all_params": {},
        }