import re
import os
import sys
import subprocess
import logging
import tempfile
import json
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

import requests as req

# --- Change this to DEBUG to see full logs ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

TIMEOUT_TWILIO = 10
TIMEOUT_PLAYWRIGHT = 60


@dataclass
class RespOrgResult:
    resporg_code: str
    carrier_name: str
    abuse_email: str
    website: str
    is_toll_free: bool


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    logger.debug(f"normalize_phone: input={repr(phone)} → digits={repr(digits)}")
    return digits


def lookup_resporg(phone: str) -> RespOrgResult:
    """Lookup carrier using Twilio Lookup v2 API with full debug logging."""
    digits = normalize_phone(phone)
    e164 = f"+1{digits}"
    logger.debug(f"lookup_resporg: normalized E.164 = {e164}")

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid:
        logger.error("TWILIO_ACCOUNT_SID is not set in environment.")
        return RespOrgResult("", "Unknown Carrier", "", "", False)
    if not auth_token:
        logger.error("TWILIO_AUTH_TOKEN is not set in environment.")
        return RespOrgResult("", "Unknown Carrier", "", "", False)

    logger.debug(f"Using Account SID: {account_sid[:8]}... (truncated for security)")

    url = f"https://lookups.twilio.com/v2/PhoneNumbers/{e164}?Fields=line_type_intelligence"
    logger.debug(f"Request URL: {url}")

    try:
        response = req.get(
            url,
            auth=(account_sid, auth_token),
            timeout=TIMEOUT_TWILIO
        )
        logger.debug(f"HTTP Status: {response.status_code}")
        logger.debug(f"Raw response body: {response.text}")

        if response.status_code == 401:
            logger.error("Twilio returned 401 Unauthorized — check your ACCOUNT_SID and AUTH_TOKEN.")
            return RespOrgResult("", "Auth Failed", "", "", False)

        if response.status_code == 404:
            logger.error(f"Twilio returned 404 — phone number {e164} may be invalid or not found.")
            return RespOrgResult("", "Invalid Number", "", "", False)

        response.raise_for_status()
        data = response.json()
        logger.debug(f"Parsed JSON: {json.dumps(data, indent=2)}")

        line_intel = data.get("line_type_intelligence")
        logger.debug(f"line_type_intelligence block: {line_intel}")

        if not line_intel:
            line_type_raw = "unknown"
            carrier_name = "N/A (toll-free or unsupported type)"
            logger.warning(
                f"line_type_intelligence is null/empty for {e164}. "
                "This is expected for toll-free numbers — Twilio does not provide "
                "carrier data for toll-free, personal, premium, sharedCost, uan, voicemail, or pager numbers."
            )
        else:
            line_type_raw = line_intel.get("type", "unknown")
            carrier_name = line_intel.get("carrier_name") or "Unknown Carrier"
            error_code = line_intel.get("error_code")

            logger.debug(f"line type: {line_type_raw}")
            logger.debug(f"carrier_name: {carrier_name}")
            logger.debug(f"error_code in line_intel: {error_code}")

            if error_code:
                logger.warning(
                    f"Twilio returned error_code={error_code} inside line_type_intelligence. "
                    "Carrier data may be unavailable for this number type."
                )

        is_toll_free = line_type_raw in ("tollFree", "toll_free")
        logger.info(
            f"Result for {e164}: carrier={carrier_name!r}, "
            f"type={line_type_raw!r}, is_toll_free={is_toll_free}"
        )

        return RespOrgResult("", carrier_name, "", "", is_toll_free)

    except req.exceptions.Timeout:
        logger.error(f"Twilio request timed out after {TIMEOUT_TWILIO}s for {e164}")
        return RespOrgResult("", "Timeout", "", "", False)

    except req.exceptions.ConnectionError as e:
        logger.error(f"Network connection error during Twilio lookup: {e}")
        return RespOrgResult("", "Connection Error", "", "", False)

    except req.exceptions.HTTPError as e:
        logger.error(f"Twilio HTTP error: {e} — Response: {response.text}")
        return RespOrgResult("", "HTTP Error", "", "", False)

    except Exception as e:
        logger.exception(f"Unexpected error during Twilio lookup for {e164}: {e}")
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
    """Extract campaign ID and other tracking params from URL - handles ANY parameter names."""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Common campaign ID parameter names across different platforms
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
        
        # Find first matching campaign ID parameter
        campaign_id = ""
        for key in campaign_id_keys:
            if key in params:
                campaign_id = params[key][0]
                break
        
        # If no standard key found, look for any parameter that looks like an ID
        # (contains numbers and is reasonably long)
        if not campaign_id:
            for key, values in params.items():
                value = values[0]
                # Check if value looks like an ID (has numbers, not too short)
                if len(value) > 8 and any(c.isdigit() for c in value):
                    campaign_id = value
                    break
        
        # Extract phone number from URL if present
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
            "all_params": {k: v[0] for k, v in params.items()},  # Debug: all params
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