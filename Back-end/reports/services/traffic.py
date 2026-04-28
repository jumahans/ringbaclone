import re
import os
import sys
import json
import logging
import subprocess
import tempfile
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

TIMEOUT_PLAYWRIGHT = 120

EMPTY = {
    "traffic_source": "",
    "ad_platform": "",
    "click_id": "",
    "campaign_id": "",
    "utm_source": "",
    "utm_medium": "",
    "utm_campaign": "",
    "utm_content": "",
    "utm_term": "",
    "publisher_id": "",
    "sub_id": "",
    "referrer": "",
}


def _resolve_platform(src: str, cid: str, ref: str) -> tuple:
    src = src.lower()
    cid = cid.lower()
    ref = ref.lower()
    if "fb" in src or "facebook" in src or "fbclid" in cid or "facebook" in ref:
        return "Facebook Ads", "Meta"
    if "google" in src or "gclid" in cid or "google" in ref:
        return "Google Ads", "Google"
    if "bing" in src or "microsoft" in src or "msclkid" in cid or "bing" in ref:
        return "Microsoft Bing Ads", "Microsoft"
    if "tiktok" in src or "ttclid" in cid or "tiktok" in ref:
        return "TikTok Ads", "TikTok"
    if "twitter" in src or "twclid" in cid or "twitter" in ref or "x.com" in ref:
        return "Twitter/X Ads", "Twitter/X"
    if "pinterest" in src or "epik" in cid or "pinterest" in ref:
        return "Pinterest Ads", "Pinterest"
    if "reddit" in src or "rdclid" in cid or "reddit" in ref:
        return "Reddit Ads", "Reddit"
    if "snapchat" in src or "snap" in src or "snapchat" in ref:
        return "Snapchat Ads", "Snapchat"
    if "youtube" in src or "yt" in src:
        return "YouTube Ads", "Google"
    if "taboola" in src or "taboola" in ref:
        return "Taboola", "Taboola"
    if "outbrain" in src or "outbrain" in ref:
        return "Outbrain", "Outbrain"
    if "email" in src or "newsletter" in src:
        return "Email Campaign", "Email"
    if "sms" in src:
        return "SMS Campaign", "SMS"
    if "whatsapp" in src or "whatsapp" in ref:
        return "WhatsApp", "Meta"
    if src:
        return src.title(), src.title()
    return "", ""


def _resolve_from_params(params: dict) -> dict:
    result = dict(EMPTY)

    result["utm_source"]   = params.get("utm_source",   [""])[0]
    result["utm_medium"]   = params.get("utm_medium",   [""])[0]
    result["utm_campaign"] = params.get("utm_campaign", [""])[0]
    result["utm_content"]  = params.get("utm_content",  [""])[0]
    result["utm_term"]     = params.get("utm_term",     [""])[0]

    for key in ["gclid", "fbclid", "msclkid", "ttclid", "twclid", "li_fat_id", "epik", "rdclid", "sclid", "dclid"]:
        if params.get(key):
            result["click_id"] = params[key][0]
            break

    for key in ["gad_campaignid", "utm_id", "campaign_id", "campaignid", "bcid", "cid"]:
        if params.get(key):
            result["campaign_id"] = params[key][0]
            break

    for key in ["pub_id", "publisher_id", "aff_id", "affiliate_id", "partner_id", "pubid"]:
        if params.get(key):
            result["publisher_id"] = params[key][0]
            break

    for key in ["subid", "sub_id", "s1", "s2", "sub1", "sub2"]:
        if params.get(key):
            result["sub_id"] = params[key][0]
            break

    result["traffic_source"], result["ad_platform"] = _resolve_platform(
        result["utm_source"], result["click_id"], ""
    )

    return result


TRAFFIC_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
    "gclid", "fbclid", "msclkid", "ttclid", "twclid", "li_fat_id",
    "epik", "rdclid", "sclid", "dclid", "gad_campaignid", "gad_source",
    "utm_id", "campaign_id", "campaignid", "bcid", "cid",
    "pub_id", "publisher_id", "aff_id", "affiliate_id",
    "subid", "sub_id", "s1", "s2",
}


def _scrape_traffic_from_page(url: str) -> dict:
    """Scrape traffic source data from inside the page using Playwright."""

    script_content = r"""
import sys, json, re
from playwright.sync_api import sync_playwright

with open(sys.argv[1]) as f:
    url = json.load(f)["url"]

def find_value(patterns, text):
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip().strip('"').strip("'")
    return ""

def resolve_platform(src, cid, ref):
    src = src.lower()
    cid = cid.lower()
    ref = ref.lower()
    if "fb" in src or "facebook" in src or "fbclid" in cid or "facebook" in ref:
        return "Facebook Ads", "Meta"
    if "google" in src or "gclid" in cid or "google" in ref:
        return "Google Ads", "Google"
    if "bing" in src or "microsoft" in src or "msclkid" in cid or "bing" in ref:
        return "Microsoft Bing Ads", "Microsoft"
    if "tiktok" in src or "ttclid" in cid or "tiktok" in ref:
        return "TikTok Ads", "TikTok"
    if "twitter" in src or "twclid" in cid or "twitter" in ref or "x.com" in ref:
        return "Twitter/X Ads", "Twitter/X"
    if "pinterest" in src or "epik" in cid or "pinterest" in ref:
        return "Pinterest Ads", "Pinterest"
    if "reddit" in src or "rdclid" in cid or "reddit" in ref:
        return "Reddit Ads", "Reddit"
    if "snapchat" in src or "snap" in src or "snapchat" in ref:
        return "Snapchat Ads", "Snapchat"
    if "youtube" in src or "yt" in src:
        return "YouTube Ads", "Google"
    if "taboola" in src or "taboola" in ref:
        return "Taboola", "Taboola"
    if "outbrain" in src or "outbrain" in ref:
        return "Outbrain", "Outbrain"
    if "email" in src or "newsletter" in src:
        return "Email Campaign", "Email"
    if "sms" in src:
        return "SMS Campaign", "SMS"
    if src:
        return src.title(), src.title()
    return "", ""

result = {
    "traffic_source": "", "ad_platform": "", "click_id": "",
    "campaign_id": "", "utm_source": "", "utm_medium": "",
    "utm_campaign": "", "utm_content": "", "utm_term": "",
    "publisher_id": "", "sub_id": "", "referrer": "",
}

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-gpu"]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
        locale="en-US",
    )

    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Network request interception — capture campaign data from outgoing requests
    intercepted = {}

    def handle_request(request):
        try:
            from urllib.parse import urlparse, parse_qs
            req_url = request.url
            if any(k in req_url for k in ['utm_source', 'fbclid', 'gclid', 'msclkid', 'ttclid', 'campaign', 'utm_id']):
                params = parse_qs(urlparse(req_url).query)
                for k, v in params.items():
                    intercepted[k] = v[0]
        except: pass

    page.on("request", handle_request)

    try:
        # page.goto(url, timeout=30000, wait_until="commit")
        # page.wait_for_timeout(4000)

        # html = page.content()
        # result["referrer"] = page.evaluate("() => document.referrer") or ""
        

        page.goto(url, timeout=30000, wait_until="commit")
        page.wait_for_timeout(6000)

        # Click Accept/OK if popup present
        try:
            page.evaluate('''
                () => {
                    var btns = Array.from(document.querySelectorAll('button'));
                    var accept = btns.find(b => ['Accept','OK','Continue','Allow'].includes(b.textContent.trim()));
                    if (accept) accept.click();
                }
            ''')
            page.wait_for_timeout(2000)
        except: pass

        html = page.content()
        result["referrer"] = page.evaluate("() => document.referrer") or ""

        # Check localStorage and sessionStorage
        storage_data = page.evaluate('''
            () => {
                const data = {};
                try {
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        data['local_' + key] = localStorage.getItem(key);
                    }
                    for (let i = 0; i < sessionStorage.length; i++) {
                        const key = sessionStorage.key(i);
                        data['session_' + key] = sessionStorage.getItem(key);
                    }
                } catch(e) {}
                return data;
            }
        ''')

        # Extract traffic keys from storage
        storage_traffic_keys = {
            'utm_source': ['local_utm_source', 'session_utm_source', 'local_source', 'session_source'],
            'utm_medium': ['local_utm_medium', 'session_utm_medium'],
            'utm_campaign': ['local_utm_campaign', 'session_utm_campaign'],
            'campaign_id': ['local_campaign_id', 'session_campaign_id', 'local_campaignId', 'session_campaignId'],
            'click_id': ['local_gclid', 'local_fbclid', 'local_msclkid', 'local_ttclid', 'session_gclid', 'session_fbclid'],
        }

        for field, keys in storage_traffic_keys.items():
            if not result[field]:
                for key in keys:
                    if storage_data.get(key):
                        result[field] = storage_data[key]
                        break

        # Check cookies
        cookies = context.cookies()
        for cookie in cookies:
            name = cookie['name'].lower()
            value = cookie['value']
            if not result['utm_source'] and 'utm_source' in name:
                result['utm_source'] = value
            if not result['click_id'] and any(k in name for k in ['gclid', 'fbclid', 'msclkid', 'ttclid']):
                result['click_id'] = value
            if not result['campaign_id'] and 'campaign' in name:
                result['campaign_id'] = value
        # JS patterns in HTML source
        field_patterns = {
            "utm_source":   [r'utm_source["\':\s=]+([a-zA-Z0-9_\-]+)', r'["\']source["\']\s*:\s*["\']([^"\']+)["\']', r'trafficSource["\':\s=]+["\']([^"\']+)["\']'],
            "utm_medium":   [r'utm_medium["\':\s=]+([a-zA-Z0-9_\-]+)', r'["\']medium["\']\s*:\s*["\']([^"\']+)["\']'],
            "utm_campaign": [r'utm_campaign["\':\s=]+([a-zA-Z0-9_\-]+)', r'["\']campaign["\']\s*:\s*["\']([^"\']+)["\']'],
            "campaign_id":  [r'campaign_?id["\':\s=]+["\']?([a-zA-Z0-9_\-]+)', r'campaignId["\':\s=]+["\']?([a-zA-Z0-9_\-]+)'],
            "click_id":     [r'(?:gclid|fbclid|msclkid|ttclid|click_?id)["\':\s=]+["\']?([a-zA-Z0-9_\-]+)'],
            "publisher_id": [r'(?:pub(?:lisher)?_?id|aff(?:iliate)?_?id)["\':\s=]+["\']?([a-zA-Z0-9_\-]+)'],
            "sub_id":       [r'sub_?id["\':\s=]+["\']?([a-zA-Z0-9_\-]+)'],
        }

        for field, patterns in field_patterns.items():
            if not result[field]:
                result[field] = find_value(patterns, html)

        # Window object
        window_data = page.evaluate('''
            () => {
                const keys = ['utm_source','utmSource','traffic_source','trafficSource',
                    'utm_campaign','utmCampaign','campaign_id','campaignId',
                    'utm_medium','utmMedium','publisher_id','publisherId',
                    'affiliate_id','affiliateId','sub_id','subId',
                    'click_id','clickId','gclid','fbclid','msclkid','ttclid'];
                const data = {};
                keys.forEach(k => { if (window[k]) data[k] = String(window[k]); });
                return data;
            }
        ''')

        if not result["utm_source"]:
            result["utm_source"] = (
                window_data.get("utm_source") or
                window_data.get("utmSource") or
                window_data.get("traffic_source") or
                window_data.get("trafficSource") or ""
            )
        if not result["campaign_id"]:
            result["campaign_id"] = window_data.get("campaign_id") or window_data.get("campaignId") or ""
        if not result["click_id"]:
            for key in ["gclid", "fbclid", "msclkid", "ttclid", "click_id", "clickId"]:
                if window_data.get(key):
                    result["click_id"] = window_data[key]
                    break

        # Meta tags
        meta_data = page.evaluate('''
            () => {
                const data = {};
                document.querySelectorAll('meta').forEach(m => {
                    const name = (m.getAttribute('name') || m.getAttribute('property') || '').toLowerCase();
                    const content = m.getAttribute('content') || '';
                    if (name && content) data[name] = content;
                });
                return data;
            }
        ''')

        if not result["utm_source"]:
            result["utm_source"] = (
                meta_data.get("utm_source") or
                meta_data.get("source") or
                meta_data.get("traffic-source") or ""
            )

        # Data attributes
        data_attrs = page.evaluate('''
            () => {
                const data = {};
                document.querySelectorAll('[data-source],[data-campaign],[data-utm-source],[data-publisher],[data-affiliate],[data-click-id],[data-campaign-id],[data-sub-id],[data-traffic]').forEach(el => {
                    Array.from(el.attributes).forEach(a => {
                        if (a.name.startsWith('data-')) data[a.name] = a.value;
                    });
                });
                return data;
            }
        ''')

        if not result["utm_source"]:
            result["utm_source"] = data_attrs.get("data-source") or data_attrs.get("data-utm-source") or data_attrs.get("data-traffic") or ""
        if not result["campaign_id"]:
            result["campaign_id"] = data_attrs.get("data-campaign-id") or data_attrs.get("data-campaign") or ""
        if not result["publisher_id"]:
            result["publisher_id"] = data_attrs.get("data-publisher") or data_attrs.get("data-affiliate") or ""


        # Apply intercepted network request data
        intercept_map = {
            'utm_source':   ['utm_source'],
            'utm_medium':   ['utm_medium'],
            'utm_campaign': ['utm_campaign'],
            'campaign_id':  ['utm_id', 'campaign_id', 'campaignid'],
            'click_id':     ['gclid', 'fbclid', 'msclkid', 'ttclid'],
        }
        for field, keys in intercept_map.items():
            if not result[field]:
                for key in keys:
                    if intercepted.get(key):
                        result[field] = intercepted[key]
                        break

        # Resolve platform
        result["traffic_source"], result["ad_platform"] = resolve_platform(
            result["utm_source"], result["click_id"], result["referrer"]
        )


    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)

    browser.close()
    print(json.dumps(result))
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

        proc = subprocess.run(
            [sys.executable, script_file, tmp_path],
            capture_output=True, text=True,
            timeout=TIMEOUT_PLAYWRIGHT,
        )

        if proc.stderr:
            logger.debug(f"[TRAFFIC] Page scrape stderr:\n{proc.stderr}")

        output = proc.stdout.strip()
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                logger.warning(f"[TRAFFIC] Bad JSON: {output}")

    except subprocess.TimeoutExpired:
        logger.error(f"[TRAFFIC] Page scrape timed out for {url}")
    except Exception as e:
        logger.error(f"[TRAFFIC] Page scrape failed: {e}")
    finally:
        if script_file and os.path.exists(script_file):
            os.unlink(script_file)
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

    return dict(EMPTY)


def extract_traffic_source(url: str) -> dict:
    """
    Universal traffic source extractor.
    Step 1 — check URL params.
    Step 2 — if not found, scrape inside the page.
    """
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        has_traffic = any(k in params for k in TRAFFIC_KEYS)

        if has_traffic:
            result = _resolve_from_params(params)
            if result["traffic_source"]:
                logger.info(f"[TRAFFIC] Found in URL: {result['traffic_source']}")
                return result

    except Exception as e:
        logger.warning(f"[TRAFFIC] URL param check failed: {e}")

    logger.info(f"[TRAFFIC] Not in URL — scraping page")
    return _scrape_traffic_from_page(url)