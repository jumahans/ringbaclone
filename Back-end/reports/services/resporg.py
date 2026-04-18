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
    is_disposable: bool =  False
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
    """Lookup carrier using IPQualityScore phone validation."""
    digits = normalize_phone(phone)
    e164 = f"+1{digits}"
    logger.debug(f"lookup_resporg: normalized E.164 = {e164}")

    api_key = os.getenv("IPQS_API_KEY")
    logger.error(f"IPQS API KEY LOADED : {repr(api_key)}")
    if not api_key:
        logger.error("IPQS_API_KEY is not set in environment.")
        return RespOrgResult("", "Unknown Carrier", "", "", False)

    url = f"https://www.ipqualityscore.com/api/json/phone/{api_key}/{e164}"
    params = {
        "strictness": 0,
        "allow_prepaid": True,
    }

    try:
        response = req.get(url, params=params, timeout=TIMEOUT_ABSTRACT)
        logger.debug(f"HTTP Status: {response.status_code}")

        if response.status_code == 401:
            logger.error("IPQS returned 401 — check your IPQS_API_KEY.")
            return RespOrgResult("", "Auth Failed", "", "", False)

        response.raise_for_status()
        data = response.json()
        logger.error(f"FULL API RESPONSE: {response.text}")

        carrier = data.get("carrier", "Unknown Carrier")
        line_type = data.get("line_type", "")
        is_valid = data.get("valid", False)
        is_voip = data.get("VOIP", False)
        is_toll_free = line_type.lower() in ("toll_free", "tollfree") if line_type else False
        country = data.get("country", "")
        region = data.get("region", "")
        city = data.get("city", "")
        timezone = data.get("timezone", "")
        international_format = data.get("formatted", "")
        national_format = data.get("local_format", "")
        risk_level = "high" if data.get("fraud_score", 0) >= 75 else "medium" if data.get("fraud_score", 0) >= 50 else "low"
        is_disposable = data.get("prepaid", False)
        is_abuse_detected = data.get("recent_abuse", False)
        line_status = "active" if data.get("active", False) else "inactive"

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
            sms_email="",
            sms_domain="",
            mcc="",
            mnc="",
        )

    except req.exceptions.Timeout:
        logger.error(f"IPQS request timed out for {e164}")
        return RespOrgResult("", "Timeout", "", "", False)

    except req.exceptions.ConnectionError as e:
        logger.error(f"Network connection error: {e}")
        return RespOrgResult("", "Connection Error", "", "", False)

    except req.exceptions.HTTPError as e:
        logger.error(f"IPQS HTTP error: {e}")
        return RespOrgResult("", "HTTP Error", "", "", False)

    except Exception as e:
        logger.exception(f"Unexpected error during IPQS lookup for {e164}: {e}")
        return RespOrgResult("", "Unknown Carrier", "", "", False)

def extract_phone_from_url(url: str) -> str:
    """Extract toll-free number from URL using Playwright."""
    
    script_content = r"""
import sys, json, re
from playwright.sync_api import sync_playwright

with open(sys.argv[1]) as f:
    url = json.load(f)["url"]

TOLL_FREE_PATTERN = re.compile(r'1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}')

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

    # Block images, fonts, CSS — speeds up load significantly
    page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,eot}", lambda route: route.abort())

    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    phone = ""
    
    try:
        # commit fires on first byte — much faster than domcontentloaded
        page.goto(url, timeout=15000, wait_until="commit")

        # 1. Check tel: links immediately — no wait
        tel_links = page.eval_on_selector_all(
            "a[href^='tel:']",
            "els => els.map(e => e.href)"
        )
        for tel in tel_links:
            digits = re.sub(r'\D', '', tel.replace("tel:", ""))
            if len(digits) >= 10:
                prefix = digits[-10:][:3]
                if prefix in ("800", "833", "844", "855", "866", "877", "888"):
                    phone = digits
                    break

        # Only wait if tel: links found nothing
        if not phone:
            page.wait_for_timeout(1500)

        # 2. Check page HTML for tel: patterns
        if not phone:
            html = page.content()
            tel_matches = re.findall(r'tel:[+]?(1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4})', html)
            if tel_matches:
                phone = re.sub(r'\D', '', tel_matches[0][0])

        # 3. Check JavaScript variables
        if not phone:
            js_phone = page.evaluate(
                "() => {"
                "const pattern = /(1?(800|833|844|855|866|877|888)[\\s.-]?\\d{3}[\\s.-]?\\d{4})/;"
                "const text = document.documentElement.innerHTML;"
                "const match = pattern.exec(text);"
                "return match ? match[0] : null;"
                "}"
            )
            if js_phone:
                phone = re.sub(r'\D', '', js_phone)

        # 4. Check body text
        if not phone:
            text = page.inner_text("body")
            full = TOLL_FREE_PATTERN.search(text)
            if full:
                phone = re.sub(r'\D', '', full.group())

        # 5. Check meta tags
        if not phone:
            meta_content = page.evaluate(
                "() => {"
                "const metas = document.querySelectorAll('meta');"
                "return Array.from(metas).map(m => m.getAttribute('content') || '').join(' ');"
                "}"
            )
            full = TOLL_FREE_PATTERN.search(meta_content or "")
            if full:
                phone = re.sub(r'\D', '', full.group())

    except Exception as e:
            import sys
            print(f"DEBUG ERROR: {e}", file=sys.stderr)
    
    import sys
    print(f"DEBUG body text sample: {repr(page.inner_text('body')[:300]) if phone == '' else 'phone found'}", file=sys.stderr)
    browser.close()
    print(phone)
"""

    script_file = None
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
            sf.write(script_content)
            script_file = sf.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"url": url}, f)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, script_file, tmp_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_PLAYWRIGHT,
        )

        phone = result.stdout.strip()
        if phone:
            return phone
        if result.stderr:
            logger.error(f"Playwright subprocess error: {result.stderr}")
        return ""

    except subprocess.TimeoutExpired:
        logger.error(f"Playwright extraction timed out for {url}")
        return ""
    except Exception as e:
        logger.error(f"Playwright extraction failed for {url}: {e}")
        return ""
    finally:
        if script_file and os.path.exists(script_file):
            os.unlink(script_file)
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

def extract_campaign_data(url: str) -> dict:
    """Extract campaign ID and other tracking params from URL."""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        campaign_id_keys = [
            # Campaign IDs
            "bcid", "cid", "campaign_id", "gad_campaignid", "campaignid",
            "utm_id", "utm_campaign", "campaign", "camp", "camp_id",
            
            # Click IDs
            "click_id", "clickid", "click", "clid", "cclid",
            
            # Affiliate / Partner IDs
            "aff_id", "affid", "affiliate_id", "affiliateid", "aff",
            "partner_id", "partnerid", "partner", "pub_id", "pubid",
            
            # Sub IDs
            "subid", "sub_id", "subid1", "subid2", "subid3",
            "sub1", "sub2", "sub3", "s1", "s2", "s3",
            
            # Tracking
            "ref", "source", "track", "tracking", "tracker",
            "trk", "trck", "trkid", "trk_id", "tracking_id",
            
            # Event / Session
            "event", "_event", "session", "session_id", "visitor",
            "visitor_id", "visit_id", "visit",
            
            # Generic IDs
            "pid", "aid", "oid", "tid", "sid", "mid", "gid", "rid", "uid",
            "id", "lid", "bid", "did", "fid", "kid", "nid", "qid", "vid",
            
            # Ad IDs
            "adid", "ad_id", "ad", "adset_id", "adsetid", "adset",
            "creative", "creative_id", "creativeid",
            "placement", "placement_id", "placementid",
            
            # Search / keyword
            "keyword", "kw", "kwd", "matchtype", "match_type",
            "network", "target", "audience", "audience_id",
            
            # Platform click IDs
            "fbclid", "gclid", "wbraid", "gbraid", "msclkid",
            "ttclid", "twclid", "li_fat_id", "mc_cid", "mc_eid",
            "igshid", "yclid", "vclid", "dclid", "sclid",
            "pin_unauth_id", "epik", "qclid", "rdclid",
            
            # UTM
            "utm_source", "utm_medium", "utm_content", "utm_term",
            "utm_creative", "utm_placement", "utm_network",
            "utm_adgroup", "utm_adgroupid", "utm_adid",
            "utm_banner", "utm_device", "utm_keyword",
            "utm_matchtype", "utm_position", "utm_target",
            
            # Order / transaction
            "order_id", "orderid", "order", "transaction_id",
            "transactionid", "txid", "tx_id",
            
            # Lead / form
            "lead_id", "leadid", "form_id", "formid",
            "survey_id", "surveyid", "response_id",
            
            # Referral
            "referral", "referral_id", "referralid", "referrer",
            "ref_id", "refid", "invite", "invite_code",
            "promo", "promo_code", "promocode", "coupon",
            
            # Landing page
            "lpkey", "lp_key", "lp", "lp_id", "lpid",
            "page_id", "pageid", "landing_id",
            
            # Azure / Microsoft
            "msclkid", "mspid", "mspclid",
            
            # Google
            "gad_source", "gad_campaignid", "gbraid", "wbraid",
            
            # Facebook / Meta
            "fbid", "fb_id", "fb_click_id", "fb_campaign_id",
            "fb_adset_id", "fb_ad_id", "fb_placement",
            
            # TikTok
            "ttid", "tt_id", "tiktok_id",
            
            # Snapchat
            "scid", "snap_id", "snapchat_id",
            
            # Email
            "email_id", "emailid", "newsletter_id",
            "list_id", "listid", "broadcast_id",
            
            # Misc
            "token", "hash", "code", "key", "tag", "label",
            "channel", "channel_id", "channelid",
            "device", "device_id", "deviceid",
            "segment", "segment_id", "segmentid",
            "variation", "variation_id", "variationid",
            "experiment", "experiment_id", "experimentid",
            "test", "test_id", "testid", "ab", "ab_id",
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


        non_phone_keys = {
            "utm_id", "utm_campaign", "utm_source", "utm_medium", "utm_content",
            "utm_term", "gad_campaignid", "gad_source", "gclid", "fbclid",
            "msclkid", "ttclid", "campaign_id", "campaignid", "cid", "bcid",
            "adid", "ad_id", "wbraid", "gbraid", "twclid", "li_fat_id",
            "epik", "qclid", "_event", "event", "session_id", "visitor_id",
            "tracking_id", "click_id", "clickid", "subid", "sub_id",
        }

        phone_in_url = ""

        # First check param values for toll-free numbers
        for key, values in params.items():
            if key.lower() in non_phone_keys:
                continue
            value = values[0]
            digits = re.sub(r'\D', '', value)
            if 10 <= len(digits) <= 11:
                prefix = digits[-10:][:3]
                if prefix in ("800", "833", "844", "855", "866", "877", "888"):
                    phone_in_url = digits
                    break

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