# import re
# import os
# import sys
# import subprocess
# import logging
# import tempfile
# import json
# from dataclasses import dataclass, field
# from urllib.parse import urlparse, parse_qs

# import requests as req

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
# )
# logger = logging.getLogger(__name__)

# TIMEOUT_ABSTRACT = 10
# TIMEOUT_PLAYWRIGHT = 120


# @dataclass
# class RespOrgResult:
#     resporg_code: str
#     carrier_name: str
#     abuse_email: str
#     website: str
#     is_toll_free: bool
#     company_name: str = ""
#     line_type: str = ""
#     is_valid: bool = False
#     is_voip: bool = False
#     country: str = ""
#     region: str = ""
#     city: str = ""
#     timezone: str = ""
#     international_format: str = ""
#     national_format: str = ""
#     risk_level: str = ""
#     is_disposable: bool =  False
#     is_abuse_detected: bool = False
#     line_status: str = ""
#     sms_email: str = ""
#     sms_domain: str = ""
#     mcc: str = ""
#     mnc: str = ""


# def normalize_phone(phone: str) -> str:
#     digits = re.sub(r"\D", "", phone)
#     if digits.startswith("1") and len(digits) == 11:
#         digits = digits[1:]
#     logger.debug(f"normalize_phone: input={repr(phone)} → digits={repr(digits)}")
#     return digits


# def lookup_resporg(phone: str) -> RespOrgResult:
#     """Lookup carrier using IPQualityScore + Twilio caller name."""
#     digits = normalize_phone(phone)
#     e164 = f"+1{digits}"
#     logger.debug(f"lookup_resporg: normalized E.164 = {e164}")

#     api_key = os.getenv("IPQS_API_KEY")
#     if not api_key:
#         logger.error("IPQS_API_KEY is not set in environment.")
#         return RespOrgResult("", "Unknown Carrier", "", "", False)

#     url = f"https://www.ipqualityscore.com/api/json/phone/{api_key}/{e164}"
#     params = {
#         "strictness": 0,
#         "allow_prepaid": True,
#     }

#     try:
#         response = req.get(url, params=params, timeout=TIMEOUT_ABSTRACT)
#         logger.debug(f"HTTP Status: {response.status_code}")

#         if response.status_code == 401:
#             logger.error("IPQS returned 401 — check your IPQS_API_KEY.")
#             return RespOrgResult("", "Auth Failed", "", "", False)

#         response.raise_for_status()
#         data = response.json()
#         logger.error(f"FULL API RESPONSE: {response.text}")
#         logger.info(f"IPQS company_name field: {data.get('name', 'NOT FOUND')}")

#         carrier = data.get("carrier", "Unknown Carrier")
#         line_type = data.get("line_type", "")
#         is_valid = data.get("valid", False)
#         is_voip = data.get("VOIP", False)
#         is_toll_free = line_type.lower() in ("toll free", "toll_free", "tollfree") if line_type else False
#         country = data.get("country", "")
#         region = data.get("region", "")
#         city = data.get("city", "")
#         timezone = data.get("timezone", "")
#         international_format = data.get("formatted", "")
#         national_format = data.get("local_format", "")
#         risk_level = "high" if data.get("fraud_score", 0) >= 75 else "medium" if data.get("fraud_score", 0) >= 50 else "low"
#         is_disposable = data.get("prepaid", False)
#         is_abuse_detected = data.get("recent_abuse", False)
#         line_status = "active" if data.get("active", False) else "inactive"

#     except req.exceptions.Timeout:
#         logger.error(f"IPQS request timed out for {e164}")
#         return RespOrgResult("", "Timeout", "", "", False)

#     except req.exceptions.ConnectionError as e:
#         logger.error(f"Network connection error: {e}")
#         return RespOrgResult("", "Connection Error", "", "", False)

#     except req.exceptions.HTTPError as e:
#         logger.error(f"IPQS HTTP error: {e}")
#         return RespOrgResult("", "HTTP Error", "", "", False)

#     except Exception as e:
#         logger.exception(f"Unexpected error during IPQS lookup for {e164}: {e}")
#         return RespOrgResult("", "Unknown Carrier", "", "", False)

#     # --- Twilio Caller Name ---
#     company_name = ""
#     try:
#         account_sid = os.getenv("TWILIO_ACCOUNT_SID")
#         auth_token = os.getenv("TWILIO_AUTH_TOKEN")
#         if account_sid and auth_token:
#             twilio_url = f"https://lookups.twilio.com/v2/PhoneNumbers/{e164}"
#             twilio_resp = req.get(
#                 twilio_url,
#                 params={"Fields": "caller_name"},
#                 auth=(account_sid, auth_token),
#                 timeout=TIMEOUT_ABSTRACT,
#             )
#             if twilio_resp.status_code == 200:
#                 twilio_data = twilio_resp.json()
#                 caller_name_data = twilio_data.get("caller_name", {})
#                 company_name = caller_name_data.get("caller_name") or ""
#                 logger.info(f"Twilio caller name for {e164}: {company_name!r}")
#             else:
#                 logger.warning(f"Twilio lookup returned {twilio_resp.status_code} for {e164}: {twilio_resp.text}")
#     except Exception as e:
#         logger.warning(f"Twilio caller name lookup failed for {e164}: {e}")
    
#     logger.info(
#         f"Result for {e164}: carrier={carrier!r}, company={company_name!r}, "
#         f"type={line_type!r}, valid={is_valid}, is_toll_free={is_toll_free}"
#     )

#     return RespOrgResult(
#         resporg_code="",
#         carrier_name=carrier,
#         company_name=company_name,
#         abuse_email="",
#         website="",
#         is_toll_free=is_toll_free,
#         line_type=line_type,
#         is_valid=is_valid,
#         is_voip=is_voip,
#         country=country,
#         region=region,
#         city=city,
#         timezone=timezone,
#         international_format=international_format,
#         national_format=national_format,
#         risk_level=risk_level,
#         is_disposable=is_disposable,
#         is_abuse_detected=is_abuse_detected,
#         line_status=line_status,
#         sms_email="",
#         sms_domain="",
#         mcc="",
#         mnc="",
#     )




# # def lookup_resporg(phone: str) -> RespOrgResult:
# #     """Lookup carrier using IPQualityScore phone validation."""
# #     digits = normalize_phone(phone)
# #     e164 = f"+1{digits}"
# #     logger.debug(f"lookup_resporg: normalized E.164 = {e164}")

# #     api_key = os.getenv("IPQS_API_KEY")
# #     logger.error(f"IPQS API KEY LOADED : {repr(api_key)}")
# #     if not api_key:
# #         logger.error("IPQS_API_KEY is not set in environment.")
# #         return RespOrgResult("", "Unknown Carrier", "", "", False)

# #     url = f"https://www.ipqualityscore.com/api/json/phone/{api_key}/{e164}"
# #     params = {
# #         "strictness": 0,
# #         "allow_prepaid": True,
# #     }

# #     try:
# #         response = req.get(url, params=params, timeout=TIMEOUT_ABSTRACT)
# #         logger.debug(f"HTTP Status: {response.status_code}")

# #         if response.status_code == 401:
# #             logger.error("IPQS returned 401 — check your IPQS_API_KEY.")
# #             return RespOrgResult("", "Auth Failed", "", "", False)

# #         response.raise_for_status()
# #         data = response.json()
# #         logger.error(f"FULL API RESPONSE: {response.text}")

# #         carrier = data.get("carrier", "Unknown Carrier")
# #         line_type = data.get("line_type", "")
# #         is_valid = data.get("valid", False)
# #         is_voip = data.get("VOIP", False)
# #         is_toll_free = line_type.lower() in ("toll free", "toll_free", "tollfree") if line_type else False
# #         country = data.get("country", "")
# #         region = data.get("region", "")
# #         city = data.get("city", "")
# #         timezone = data.get("timezone", "")
# #         international_format = data.get("formatted", "")
# #         national_format = data.get("local_format", "")
# #         risk_level = "high" if data.get("fraud_score", 0) >= 75 else "medium" if data.get("fraud_score", 0) >= 50 else "low"
# #         is_disposable = data.get("prepaid", False)
# #         is_abuse_detected = data.get("recent_abuse", False)
# #         line_status = "active" if data.get("active", False) else "inactive"

# #         logger.info(
# #             f"Result for {e164}: carrier={carrier!r}, "
# #             f"type={line_type!r}, valid={is_valid}, is_toll_free={is_toll_free}"
# #         )

# #         return RespOrgResult(
# #             resporg_code="",
# #             carrier_name=carrier,
# #             abuse_email="",
# #             website="",
# #             is_toll_free=is_toll_free,
# #             line_type=line_type,
# #             is_valid=is_valid,
# #             is_voip=is_voip,
# #             country=country,
# #             region=region,
# #             city=city,
# #             timezone=timezone,
# #             international_format=international_format,
# #             national_format=national_format,
# #             risk_level=risk_level,
# #             is_disposable=is_disposable,
# #             is_abuse_detected=is_abuse_detected,
# #             line_status=line_status,
# #             sms_email="",
# #             sms_domain="",
# #             mcc="",
# #             mnc="",
# #         )

# #     except req.exceptions.Timeout:
# #         logger.error(f"IPQS request timed out for {e164}")
# #         return RespOrgResult("", "Timeout", "", "", False)

# #     except req.exceptions.ConnectionError as e:
# #         logger.error(f"Network connection error: {e}")
# #         return RespOrgResult("", "Connection Error", "", "", False)

# #     except req.exceptions.HTTPError as e:
# #         logger.error(f"IPQS HTTP error: {e}")
# #         return RespOrgResult("", "HTTP Error", "", "", False)

# #     except Exception as e:
# #         logger.exception(f"Unexpected error during IPQS lookup for {e164}: {e}")
# #         return RespOrgResult("", "Unknown Carrier", "", "", False)



# # def extract_phone_from_url(url: str) -> str:
# #     """Extract toll-free number from URL."""

# #     def find_phone(text):
# #         if not text:
# #             return ""
# #         # +1(877) 513-7794
# #         m = re.search(r'\+1\((\d{3})\)\s*(\d{3})-(\d{4})', text)
# #         if m:
# #             return f"1{m.group(1)}{m.group(2)}{m.group(3)}"
# #         # +1-855-404-5252
# #         m = re.search(r'\+1-(\d{3})-(\d{3})-(\d{4})', text)
# #         if m:
# #             return f"1{m.group(1)}{m.group(2)}{m.group(3)}"
# #         # 1-855-404-5252 or (855) 404-5252 or 8554045252
# #         m = re.search(
# #             r'1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}',
# #             text
# #         )
# #         if m:
# #             return re.sub(r'\D', '', m.group())
# #         return ""

# #     # Step 1 — check URL params
# #     try:
# #         parsed = urlparse(url)
# #         params = parse_qs(parsed.query)
# #         for key, values in params.items():
# #             value = values[0]
# #             digits = re.sub(r'\D', '', value)
# #             if len(digits) >= 10:
# #                 prefix = digits[-10:][:3]
# #                 if prefix in ("800", "833", "844", "855", "866", "877", "888"):
# #                     logger.info(f"Phone found in URL param '{key}': {digits}")
# #                     return digits
# #     except Exception as e:
# #         logger.warning(f"URL param check failed: {e}")

# #     # Step 2 — curl (fast, static pages)
# #     try:
# #         curl_result = subprocess.run(
# #             [
# #                 "curl", "-sL", "--max-time", "10", "--compressed",
# #                 "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #                 "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
# #                 "-H", "Accept-Language: en-US,en;q=0.5",
# #                 url
# #             ],
# #             capture_output=True, text=True, timeout=15,
# #         )
# #         phone = find_phone(curl_result.stdout)
# #         if phone:
# #             logger.info(f"[SCRAPE] Phone found via curl: {phone}")
# #             return phone
# #     except Exception as e:
# #         logger.warning(f"curl failed: {e}")

# #     # Step 3 — Playwright (JavaScript pages)
# #     script_content = r"""
# # import sys, json, re
# # from playwright.sync_api import sync_playwright

# # with open(sys.argv[1]) as f:
# #     url = json.load(f)["url"]

# # def find_phone(text):
# #     if not text:
# #         return ""
# #     m = re.search(r'\+1\((\d{3})\)\s*(\d{3})-(\d{4})', text)
# #     if m:
# #         return f"1{m.group(1)}{m.group(2)}{m.group(3)}"
# #     m = re.search(r'\+1-(\d{3})-(\d{3})-(\d{4})', text)
# #     if m:
# #         return f"1{m.group(1)}{m.group(2)}{m.group(3)}"
# #     m = re.search(r'1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
# #     if m:
# #         return re.sub(r'\D', '', m.group())
# #     return ""

# # with sync_playwright() as p:
# #     browser = p.chromium.launch(
# #         headless=True,
# #         args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-gpu"]
# #     )
# #     context = browser.new_context(
# #         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #         viewport={"width": 1366, "height": 768},
# #         locale="en-US",
# #     )
# #     page = context.new_page()
# #     page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,eot}", lambda route: route.abort())
# #     page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# #     phone = ""

# #     try:
# #         response = page.goto(url, timeout=30000, wait_until="commit")
# #         status = response.status if response else 0

# #         if status in (403, 404):
# #             browser.close()
# #             sys.exit(0)

# #         # Wait for JS to render
# #         page.wait_for_timeout(5000)

# #         # Click Accept button if present — phone appears after click
# #         try:
# #             page.evaluate(
# #                 "() => {"
# #                 "  var btns = Array.from(document.querySelectorAll('button'));"
# #                 "  var accept = btns.find(function(b) { return b.textContent.trim() === 'Accept'; });"
# #                 "  if (accept) accept.click();"
# #                 "}"
# #             )
# #             page.wait_for_timeout(3000)
# #         except:
# #             pass

# #         # Check tel: links
# #         tel_links = page.eval_on_selector_all("a[href^='tel:']", "els => els.map(e => e.href)")
# #         for tel in tel_links:
# #             digits = re.sub(r'\D', '', tel.replace("tel:", ""))
# #             if len(digits) >= 10:
# #                 prefix = digits[-10:][:3]
# #                 if prefix in ("800", "833", "844", "855", "866", "877", "888"):
# #                     phone = digits
# #                     break

# #         # Check full page source
# #         if not phone:
# #             phone = find_phone(page.content())

# #         # Check body text
# #         if not phone:
# #             phone = find_phone(page.inner_text("body"))

# #     except Exception as e:
# #         print(f"ERROR: {e}", file=sys.stderr)

# #     browser.close()
# #     print(phone)
# # """

# #     script_file = None
# #     tmp_path = None
# #     try:
# #         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
# #             sf.write(script_content)
# #             script_file = sf.name

# #         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
# #             json.dump({"url": url}, f)
# #             tmp_path = f.name

# #         result = subprocess.run(
# #             [sys.executable, script_file, tmp_path],
# #             capture_output=True, text=True,
# #             timeout=TIMEOUT_PLAYWRIGHT,
# #         )

# #         phone = result.stdout.strip()
# #         if result.stderr:
# #             logger.debug(f"Playwright stderr:\n{result.stderr}")
# #         if phone:
# #             logger.info(f"[SCRAPE] Phone found via Playwright: {phone}")
# #             return phone
# #         return ""

# #     except subprocess.TimeoutExpired:
# #         logger.error(f"Playwright timed out for {url}")
# #         return ""
# #     except Exception as e:
# #         logger.error(f"Playwright failed for {url}: {e}")
# #         return ""
# #     finally:
# #         if script_file and os.path.exists(script_file):
# #             os.unlink(script_file)
# #         if tmp_path and os.path.exists(tmp_path):
# #             try:
# #                 os.unlink(tmp_path)
# #             except:
# #                 pass


            
# def extract_campaign_data(url: str) -> dict: 
#     """Extract campaign ID and other tracking params from URL."""
#     try:
#         parsed = urlparse(url)
#         params = parse_qs(parsed.query)

#         campaign_id_keys = [
#             # Campaign IDs
#             "bcid", "cid", "campaign_id", "gad_campaignid", "campaignid",
#             "utm_id", "utm_campaign", "campaign", "camp", "camp_id",
            
#             # Click IDs
#             "click_id", "clickid", "click", "clid", "cclid",
            
#             # Affiliate / Partner IDs
#             "aff_id", "affid", "affiliate_id", "affiliateid", "aff",
#             "partner_id", "partnerid", "partner", "pub_id", "pubid",
            
#             # Sub IDs
#             "subid", "sub_id", "subid1", "subid2", "subid3",
#             "sub1", "sub2", "sub3", "s1", "s2", "s3",
            
#             # Tracking
#             "ref", "source", "track", "tracking", "tracker",
#             "trk", "trck", "trkid", "trk_id", "tracking_id",
            
#             # Event / Session
#             "event", "_event", "session", "session_id", "visitor",
#             "visitor_id", "visit_id", "visit",
            
#             # Generic IDs
#             "pid", "aid", "oid", "tid", "sid", "mid", "gid", "rid", "uid",
#             "id", "lid", "bid", "did", "fid", "kid", "nid", "qid", "vid",
            
#             # Ad IDs
#             "adid", "ad_id", "ad", "adset_id", "adsetid", "adset",
#             "creative", "creative_id", "creativeid",
#             "placement", "placement_id", "placementid",
            
#             # Search / keyword
#             "keyword", "kw", "kwd", "matchtype", "match_type",
#             "network", "target", "audience", "audience_id",
            
#             # Platform click IDs
#             "fbclid", "gclid", "wbraid", "gbraid", "msclkid",
#             "ttclid", "twclid", "li_fat_id", "mc_cid", "mc_eid",
#             "igshid", "yclid", "vclid", "dclid", "sclid",
#             "pin_unauth_id", "epik", "qclid", "rdclid",
            
#             # UTM
#             "utm_source", "utm_medium", "utm_content", "utm_term",
#             "utm_creative", "utm_placement", "utm_network",
#             "utm_adgroup", "utm_adgroupid", "utm_adid",
#             "utm_banner", "utm_device", "utm_keyword",
#             "utm_matchtype", "utm_position", "utm_target",
            
#             # Order / transaction
#             "order_id", "orderid", "order", "transaction_id",
#             "transactionid", "txid", "tx_id",
            
#             # Lead / form
#             "lead_id", "leadid", "form_id", "formid",
#             "survey_id", "surveyid", "response_id",
            
#             # Referral
#             "referral", "referral_id", "referralid", "referrer",
#             "ref_id", "refid", "invite", "invite_code",
#             "promo", "promo_code", "promocode", "coupon",
            
#             # Landing page
#             "lpkey", "lp_key", "lp", "lp_id", "lpid",
#             "page_id", "pageid", "landing_id",
            
#             # Azure / Microsoft
#             "msclkid", "mspid", "mspclid",
            
#             # Google
#             "gad_source", "gad_campaignid", "gbraid", "wbraid",
            
#             # Facebook / Meta
#             "fbid", "fb_id", "fb_click_id", "fb_campaign_id",
#             "fb_adset_id", "fb_ad_id", "fb_placement",
            
#             # TikTok
#             "ttid", "tt_id", "tiktok_id",
            
#             # Snapchat
#             "scid", "snap_id", "snapchat_id",
            
#             # Email
#             "email_id", "emailid", "newsletter_id",
#             "list_id", "listid", "broadcast_id",
            
#             # Misc
#             "token", "hash", "code", "key", "tag", "label",
#             "channel", "channel_id", "channelid",
#             "device", "device_id", "deviceid",
#             "segment", "segment_id", "segmentid",
#             "variation", "variation_id", "variationid",
#             "experiment", "experiment_id", "experimentid",
#             "test", "test_id", "testid", "ab", "ab_id",
#         ]

#         campaign_id = ""
#         for key in campaign_id_keys:
#             if key in params:
#                 campaign_id = params[key][0]
#                 break

#         if not campaign_id:
#             for key, values in params.items():
#                 value = values[0]
#                 if len(value) > 8 and any(c.isdigit() for c in value):
#                     campaign_id = value
#                     break


#         non_phone_keys = {
#             "utm_id", "utm_campaign", "utm_source", "utm_medium", "utm_content",
#             "utm_term", "gad_campaignid", "gad_source", "gclid", "fbclid",
#             "msclkid", "ttclid", "campaign_id", "campaignid", "cid", "bcid",
#             "adid", "ad_id", "wbraid", "gbraid", "twclid", "li_fat_id",
#             "epik", "qclid", "_event", "event", "session_id", "visitor_id",
#             "tracking_id", "click_id", "clickid", "subid", "sub_id",
#         }

#         phone_in_url = ""

#         # First check param values for toll-free numbers
#         for key, values in params.items():
#             if key.lower() in non_phone_keys:
#                 continue
#             value = values[0]
#             digits = re.sub(r'\D', '', value)
#             if 10 <= len(digits) <= 11:
#                 prefix = digits[-10:][:3]
#                 if prefix in ("800", "833", "844", "855", "866", "877", "888"):
#                     phone_in_url = digits
#                     break

#         return {
#             "campaign_id": campaign_id,
#             "lp_key": params.get("lpkey", [""])[0],
#             "full_url": url,
#             "domain": parsed.netloc,
#             "path": parsed.path,
#             "phone_in_url": phone_in_url,
#             "all_params": {k: v[0] for k, v in params.items()},
#         }
#     except Exception as e:
#         logger.error(f"Campaign data extraction failed: {e}")
#         return {
#             "campaign_id": "",
#             "lp_key": "",
#             "full_url": url,
#             "domain": "",
#             "path": "",
#             "phone_in_url": "",
#             "all_params": {},
#         }
 
 




# # TIMEOUT_PLAYWRIGHT = 60


# # def extract_phone_from_url(url: str) -> str:
# #     """Extract toll-free number from URL using Playwright."""
    
# #     script_content = r"""
# # import sys, json, re
# # from playwright.sync_api import sync_playwright

# # TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
# # TOLL_FREE_PATTERN = re.compile(r'1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}')

# # def clean_phone(raw):
# #     digits = re.sub(r'\D', '', raw)
# #     if len(digits) == 11 and digits.startswith('1'):
# #         digits = digits[1:]
# #     if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
# #         return digits
# #     return None

# # def find_phone(text):
# #     if not text:
# #         return ""
# #     for match in TOLL_FREE_PATTERN.finditer(text):
# #         cleaned = clean_phone(match.group())
# #         if cleaned:
# #             return cleaned
# #     return ""

# # with open(sys.argv[1]) as f:
# #     url = json.load(f)["url"]

# # with sync_playwright() as p:
# #     browser = p.chromium.launch(
# #         headless=True,
# #         args=[
# #             "--disable-blink-features=AutomationControlled",
# #             "--no-sandbox",
# #             "--disable-gpu",
# #             "--disable-dev-shm-usage",
# #         ]
# #     )
# #     context = browser.new_context(
# #         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #         viewport={"width": 1366, "height": 768},
# #         locale="en-US",
# #     )
# #     page = context.new_page()

# #     page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,eot}", lambda route: route.abort())
# #     page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
# #     phone = ""
    
# #     try:
# #         page.goto(url, timeout=25000, wait_until="networkidle")
# #         page.wait_for_timeout(2000)
        
# #         # === CLICK ANY BLOCKER BUTTON ===
# #         clicked = False
# #         for text in ['Accept', 'Agree', 'Continue', 'OK', 'Yes', 'Confirm', 'Got it', 'Allow', 'Proceed', 'Ignore']:
# #             try:
# #                 # Try multiple selector strategies
# #                 selectors = [
# #                     f"button:has-text('{text}')",
# #                     f"[role='button']:has-text('{text}')",
# #                     f"a:has-text('{text}')",
# #                     f"div:has-text('{text}')",
# #                 ]
# #                 for sel in selectors:
# #                     loc = page.locator(sel).first
# #                     if loc.count() > 0:
# #                         loc.click()
# #                         clicked = True
# #                         print(f"DEBUG: Clicked '{text}'", file=sys.stderr)
# #                         break
# #                 if clicked:
# #                     break
# #             except:
# #                 pass
        
# #         # === KEY: Wait 8 seconds AFTER click for JS to inject phone ===
# #         page.wait_for_timeout(8000)
        
# #         # === SCAN EVERYTHING ===
# #         # 1. tel: links
# #         try:
# #             tel_links = page.eval_on_selector_all("a[href^='tel:']", "els => els.map(e => e.getAttribute('href'))")
# #             for tel in tel_links:
# #                 phone = find_phone(tel)
# #                 if phone:
# #                     break
# #         except:
# #             pass

# #         # 2. Full HTML source
# #         if not phone:
# #             try:
# #                 phone = find_phone(page.content())
# #             except:
# #                 pass

# #         # 3. Body text
# #         if not phone:
# #             try:
# #                 phone = find_phone(page.inner_text("body"))
# #             except:
# #                 pass

# #         # 4. All text including hidden
# #         if not phone:
# #             try:
# #                 all_text = page.evaluate("() => document.documentElement.innerText || document.documentElement.textContent || ''")
# #                 phone = find_phone(all_text)
# #             except:
# #                 pass

# #         # 5. All element attributes
# #         if not phone:
# #             try:
# #                 all_attrs = page.evaluate('''
# #                     () => {
# #                         const els = document.querySelectorAll('*');
# #                         let text = '';
# #                         for (const el of els) {
# #                             for (const attr of el.attributes) {
# #                                 text += ' ' + attr.value;
# #                             }
# #                         }
# #                         return text;
# #                     }
# #                 ''')
# #                 phone = find_phone(all_attrs)
# #             except:
# #                 pass

# #         # 6. Iframes
# #         if not phone:
# #             try:
# #                 for frame in page.frames:
# #                     try:
# #                         frame_text = frame.evaluate("() => document.body ? document.body.innerText : ''")
# #                         phone = find_phone(frame_text)
# #                         if phone:
# #                             break
# #                     except:
# #                         pass
# #             except:
# #                 pass

# #     except Exception as e:
# #         print(f"DEBUG ERROR: {e}", file=sys.stderr)
    
# #     # Debug output
# #     try:
# #         body = page.inner_text("body")
# #         print(f"DEBUG: phone={phone}, body_sample={repr(body[:500])}", file=sys.stderr)
# #     except:
# #         print(f"DEBUG: phone={phone}, no_body", file=sys.stderr)
    
# #     browser.close()
# #     print(phone)
# # """

# #     script_file = None
# #     tmp_path = None
# #     try:
# #         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
# #             sf.write(script_content)
# #             script_file = sf.name

# #         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
# #             json.dump({"url": url}, f)
# #             tmp_path = f.name

# #         result = subprocess.run(
# #             [sys.executable, script_file, tmp_path],
# #             capture_output=True,
# #             text=True,
# #             timeout=TIMEOUT_PLAYWRIGHT,
# #         )

# #         phone = result.stdout.strip()
# #         if result.stderr:
# #             logger.error(f"Playwright debug: {result.stderr.strip()}")
# #         if phone:
# #             return phone
# #         return ""

# #     except subprocess.TimeoutExpired:
# #         logger.error(f"Playwright extraction timed out for {url}")
# #         return ""
# #     except Exception as e:
# #         logger.error(f"Playwright extraction failed for {url}: {e}")
# #         return ""
# #     finally:
# #         if script_file and os.path.exists(script_file):
# #             os.unlink(script_file)
# #         if tmp_path and os.path.exists(tmp_path):
# #             try:
# #                 os.unlink(tmp_path)
# #             except:
# #                 pass





# # TIMEOUT_PLAYWRIGHT = 60


# # def extract_phone_from_url(url: str) -> str:
# #     """Extract toll-free number from URL using Playwright."""
    
# #     script_content = r"""
# # import sys, json, re
# # from playwright.sync_api import sync_playwright

# # TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
# # TOLL_FREE_PATTERN = re.compile(r'1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}')

# # def clean_phone(raw):
# #     digits = re.sub(r'\D', '', raw)
# #     if len(digits) == 11 and digits.startswith('1'):
# #         digits = digits[1:]
# #     if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
# #         return digits
# #     return None

# # def find_phone(text):
# #     if not text:
# #         return ""
# #     for match in TOLL_FREE_PATTERN.finditer(text):
# #         cleaned = clean_phone(match.group())
# #         if cleaned:
# #             return cleaned
# #     return ""

# # with open(sys.argv[1]) as f:
# #     url = json.load(f)["url"]

# # with sync_playwright() as p:
# #     browser = p.chromium.launch(
# #         headless=True,
# #         args=[
# #             "--disable-blink-features=AutomationControlled",
# #             "--no-sandbox",
# #             "--disable-gpu",
# #             "--disable-dev-shm-usage",
# #         ]
# #     )
# #     context = browser.new_context(
# #         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #         viewport={"width": 1366, "height": 768},
# #         locale="en-US",
# #     )
# #     page = context.new_page()

# #     page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,eot}", lambda route: route.abort())
# #     page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
# #     phone = ""
    
# #     try:
# #         page.goto(url, timeout=25000, wait_until="networkidle")
# #         page.wait_for_timeout(2000)
        
# #         # === CLICK ACCEPT OR ANY BLOCKER ===
# #         for text in ['Accept', 'Agree', 'Continue', 'OK', 'Yes', 'Confirm', 'Got it', 'Allow', 'Proceed', 'Ignore']:
# #             try:
# #                 loc = page.locator(f"button:has-text('{text}')").first
# #                 if loc.count() > 0:
# #                     loc.click()
# #                     print(f"DEBUG: Clicked '{text}'", file=sys.stderr)
# #                     break
# #             except:
# #                 pass
        
# #         # === CRITICAL: Wait 10 seconds for JS to fetch and inject phone ===
# #         page.wait_for_timeout(10000)
        
# #         # === SCAN ALL SOURCES ===
# #         sources = [
# #             ("tel_links", lambda: page.eval_on_selector_all("a[href^='tel:']", "els => els.map(e => e.getAttribute('href'))")),
# #             ("html", lambda: page.content()),
# #             ("body", lambda: page.inner_text("body")),
# #             ("all_text", lambda: page.evaluate("() => document.documentElement.innerText || document.documentElement.textContent || ''")),
# #             ("attrs", lambda: page.evaluate("() => { const els = document.querySelectorAll('*'); let t = ''; for (const e of els) { for (const a of e.attributes) { t += ' ' + a.value; } } return t; }")),
# #         ]
        
# #         for name, getter in sources:
# #             try:
# #                 data = getter()
# #                 if isinstance(data, list):
# #                     for item in data:
# #                         phone = find_phone(item)
# #                         if phone:
# #                             print(f"DEBUG: Found in {name}: {phone}", file=sys.stderr)
# #                             break
# #                 else:
# #                     phone = find_phone(data)
# #                     if phone:
# #                         print(f"DEBUG: Found in {name}: {phone}", file=sys.stderr)
# #                         break
# #             except Exception as e:
# #                 print(f"DEBUG: {name} error: {e}", file=sys.stderr)
# #             if phone:
# #                 break
        
# #         # === IFRAMES ===
# #         if not phone:
# #             try:
# #                 for frame in page.frames:
# #                     try:
# #                         ft = frame.evaluate("() => document.body ? document.body.innerText : ''")
# #                         phone = find_phone(ft)
# #                         if phone:
# #                             print(f"DEBUG: Found in iframe: {phone}", file=sys.stderr)
# #                             break
# #                     except:
# #                         pass
# #             except:
# #                 pass

# #     except Exception as e:
# #         print(f"DEBUG ERROR: {e}", file=sys.stderr)
    
# #     try:
# #         body = page.inner_text("body")
# #         print(f"DEBUG FINAL: phone={phone}, body={repr(body[:600])}", file=sys.stderr)
# #     except:
# #         print(f"DEBUG FINAL: phone={phone}, no body", file=sys.stderr)
    
# #     browser.close()
# #     print(phone)
# # """

# #     script_file = None
# #     tmp_path = None
# #     try:
# #         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
# #             sf.write(script_content)
# #             script_file = sf.name

# #         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
# #             json.dump({"url": url}, f)
# #             tmp_path = f.name

# #         result = subprocess.run(
# #             [sys.executable, script_file, tmp_path],
# #             capture_output=True,
# #             text=True,
# #             timeout=TIMEOUT_PLAYWRIGHT,
# #         )

# #         phone = result.stdout.strip()
# #         if result.stderr:
# #             logger.error(f"Playwright debug: {result.stderr.strip()}")
# #         if phone:
# #             return phone
# #         return ""

# #     except subprocess.TimeoutExpired:
# #         logger.error(f"Playwright extraction timed out for {url}")
# #         return ""
# #     except Exception as e:
# #         logger.error(f"Playwright extraction failed for {url}: {e}")
# #         return ""
# #     finally:
# #         if script_file and os.path.exists(script_file):
# #             os.unlink(script_file)
# #         if tmp_path and os.path.exists(tmp_path):
# #             try:
# #                 os.unlink(tmp_path)
# #             except:
# #                 pass



# # TIMEOUT_PLAYWRIGHT = 60

# # # FIXED: Added \+? to handle +1 prefix
# # TOLL_FREE_PATTERN = re.compile(r'\+?1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}')


# # def extract_phone_from_url(url: str) -> str:
# #     """Extract toll-free number from URL using Playwright."""
    
# #     TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
    
# #     def clean_phone(raw):
# #         if not raw or raw == "null":
# #             return None
# #         digits = re.sub(r'\D', '', raw)
# #         if len(digits) == 11 and digits.startswith('1'):
# #             digits = digits[1:]
# #         if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
# #             return digits
# #         return None
    
# #     # Check URL
# #     for match in TOLL_FREE_PATTERN.finditer(url):
# #         cleaned = clean_phone(match.group())
# #         if cleaned:
# #             return cleaned
    
# #     script_content = r"""
# # import sys, json, re
# # from playwright.sync_api import sync_playwright

# # TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
# # # FIXED: Added \+? to handle +1 prefix
# # TOLL_FREE_PATTERN = re.compile(r'\+?1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}')

# # def clean_phone(raw):
# #     if not raw or raw == "null":
# #         return None
# #     digits = re.sub(r'\D', '', raw)
# #     if len(digits) == 11 and digits.startswith('1'):
# #         digits = digits[1:]
# #     if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
# #         return digits
# #     return None

# # def find_phone(text):
# #     if not text:
# #         return ""
# #     for match in TOLL_FREE_PATTERN.finditer(text):
# #         cleaned = clean_phone(match.group())
# #         if cleaned:
# #             return cleaned
# #     return ""

# # with open(sys.argv[1]) as f:
# #     url = json.load(f)["url"]

# # # Check URL
# # for match in TOLL_FREE_PATTERN.finditer(url):
# #     cleaned = clean_phone(match.group())
# #     if cleaned:
# #         print(cleaned)
# #         sys.exit(0)

# # with sync_playwright() as p:
# #     browser = p.chromium.launch(
# #         headless=True,
# #         args=[
# #             "--disable-blink-features=AutomationControlled",
# #             "--no-sandbox",
# #             "--disable-gpu",
# #             "--disable-dev-shm-usage",
# #         ]
# #     )
# #     context = browser.new_context(
# #         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #         viewport={"width": 1366, "height": 768},
# #         locale="en-US",
# #     )
# #     page = context.new_page()

# #     page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,eot}", lambda route: route.abort())
# #     page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
# #     phone = ""
    
# #     try:
# #         page.goto(url, timeout=25000, wait_until="networkidle")
# #         page.wait_for_timeout(2000)
        
# #         # Click buttons
# #         for text in ['Accept', 'Agree', 'Continue', 'OK', 'Yes', 'Confirm', 'Got it', 'Allow', 'Proceed', 'Ignore']:
# #             try:
# #                 loc = page.locator(f"button:has-text('{text}')").first
# #                 if loc.count() > 0:
# #                     loc.click()
# #                     print(f"DEBUG: Clicked '{text}'", file=sys.stderr)
# #                     break
# #             except:
# #                 pass
        
# #         # Wait and poll
# #         for i in range(5):
# #             page.wait_for_timeout(3000)
            
# #             for name, getter in [
# #                 ("tel", lambda: page.eval_on_selector_all("a[href^='tel:']", "els => els.map(e => e.getAttribute('href'))")),
# #                 ("html", lambda: page.content()),
# #                 ("body", lambda: page.inner_text("body")),
# #                 ("all", lambda: page.evaluate("() => document.documentElement.innerText || ''")),
# #             ]:
# #                 try:
# #                     data = getter()
# #                     if isinstance(data, list):
# #                         for item in data:
# #                             phone = find_phone(item)
# #                             if phone:
# #                                 print(f"DEBUG: Found {phone} in {name}", file=sys.stderr)
# #                                 break
# #                     else:
# #                         phone = find_phone(data)
# #                         if phone:
# #                             print(f"DEBUG: Found {phone} in {name}", file=sys.stderr)
# #                             break
# #                 except:
# #                     pass
# #                 if phone:
# #                     break
            
# #             if phone:
# #                 break
        
# #         # Iframes
# #         if not phone:
# #             try:
# #                 for frame in page.frames:
# #                     try:
# #                         ft = frame.evaluate("() => document.body ? document.body.innerText : ''")
# #                         phone = find_phone(ft)
# #                         if phone:
# #                             print(f"DEBUG: Found {phone} in iframe", file=sys.stderr)
# #                             break
# #                     except:
# #                         pass
# #             except:
# #                 pass

# #     except Exception as e:
# #         print(f"DEBUG ERROR: {e}", file=sys.stderr)
    
# #     # Debug
# #     try:
# #         body = page.inner_text("body")
# #         print(f"DEBUG: phone={phone} body_len={len(body)} sample={repr(body[:800])}", file=sys.stderr)
# #     except Exception as e:
# #         print(f"DEBUG: phone={phone} body_error={e}", file=sys.stderr)
    
# #     browser.close()
# #     print(phone)
# # """

# #     script_file = None
# #     tmp_path = None
# #     try:
# #         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
# #             sf.write(script_content)
# #             script_file = sf.name

# #         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
# #             json.dump({"url": url}, f)
# #             tmp_path = f.name

# #         result = subprocess.run(
# #             [sys.executable, script_file, tmp_path],
# #             capture_output=True,
# #             text=True,
# #             timeout=TIMEOUT_PLAYWRIGHT,
# #         )

# #         # DEBUG: Always print raw output
# #         print(f"RAW STDOUT: {result.stdout!r}", file=sys.stderr)
# #         print(f"RAW STDERR: {result.stderr!r}", file=sys.stderr)

# #         phone = result.stdout.strip()
# #         if result.stderr:
# #             logger.error(f"Playwright debug: {result.stderr.strip()}")
# #         if phone:
# #             return phone
# #         return ""

# #     except subprocess.TimeoutExpired:
# #         logger.error(f"Playwright extraction timed out for {url}")
# #         return ""
# #     except Exception as e:
# #         logger.error(f"Playwright extraction failed for {url}: {e}")
# #         return ""
# #     finally:
# #         if script_file and os.path.exists(script_file):
# #             os.unlink(script_file)
# #         if tmp_path and os.path.exists(tmp_path):
# #             try:
# #                 os.unlink(tmp_path)
# #             except:
# #                 pass




# """
# phone_extractor.py
# ------------------
# Universal toll-free phone number extractor.
# Extracts from: URL, JSON-LD/schema.org, tel: links, page text, iframes.
# Handles: consent banners, lazy-load, SPAs, footer-hidden numbers, +1 prefix variants.
# """

# import json
# import logging
# import os
# import re
# import subprocess
# import sys
# import tempfile

# logger = logging.getLogger(__name__)

# TIMEOUT_PLAYWRIGHT = 90  # Increased: some sites are slow

# # ── Regex ─────────────────────────────────────────────────────────────────────
# # Covers:
# #   +1-800-123-4567  |  1 (800) 123-4567  |  800.123.4567  |  8001234567
# #   All separators: space, dash, dot, none
# TOLL_FREE_PATTERN = re.compile(
#     r'(?<!\d)'                                    # no leading digit
#     r'(?:\+?1[-.\s]?)?'                           # optional country code
#     r'\(?(800|833|844|855|866|877|888)\)?'        # area code
#     r'[-.\s]?\d{3}[-.\s]?\d{4}'                  # rest of number
#     r'(?!\d)'                                     # no trailing digit
# )

# TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}


# def clean_phone(raw: str) -> str | None:
#     """Normalize any matched string to a clean 10-digit string or None."""
#     if not raw or raw.strip().lower() == "null":
#         return None
#     digits = re.sub(r'\D', '', raw)
#     if len(digits) == 11 and digits.startswith('1'):
#         digits = digits[1:]
#     if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
#         return digits
#     return None


# def find_phone_in_text(text: str) -> str:
#     """Scan arbitrary text and return the first valid toll-free number found."""
#     if not text:
#         return ""
#     for match in TOLL_FREE_PATTERN.finditer(text):
#         cleaned = clean_phone(match.group())
#         if cleaned:
#             return cleaned
#     return ""


# # ── Playwright script (runs in subprocess) ────────────────────────────────────
# _PLAYWRIGHT_SCRIPT = r'''
# import sys, json, re, time
# from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
# TOLL_FREE_PATTERN = re.compile(
#     r'(?<!\d)(?:\+?1[-.\s]?)?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)'
# )

# def clean_phone(raw):
#     if not raw or raw.strip().lower() == "null":
#         return None
#     digits = re.sub(r'\D', '', raw)
#     if len(digits) == 11 and digits.startswith('1'):
#         digits = digits[1:]
#     if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
#         return digits
#     return None

# def find_phone(text):
#     if not text:
#         return ""
#     for match in TOLL_FREE_PATTERN.finditer(text):
#         c = clean_phone(match.group())
#         if c:
#             return c
#     return ""

# def debug(msg):
#     print(f"DEBUG: {msg}", file=sys.stderr)

# # ── JSON-LD / schema.org extraction ──────────────────────────────────────────
# def extract_jsonld(page):
#     try:
#         scripts = page.eval_on_selector_all(
#             'script[type="application/ld+json"]',
#             "els => els.map(e => e.textContent)"
#         )
#         for raw in scripts:
#             try:
#                 data = json.loads(raw)
#                 # Flatten nested structures
#                 stack = [data] if isinstance(data, dict) else data if isinstance(data, list) else []
#                 while stack:
#                     node = stack.pop()
#                     if isinstance(node, dict):
#                         for key in ("telephone", "phone", "contactPoint", "contactOption"):
#                             val = node.get(key)
#                             if isinstance(val, str):
#                                 p = find_phone(val)
#                                 if p:
#                                     debug(f"Found in JSON-LD key={key}: {p}")
#                                     return p
#                             elif isinstance(val, dict):
#                                 stack.append(val)
#                             elif isinstance(val, list):
#                                 stack.extend(val)
#                         stack.extend(v for v in node.values() if isinstance(v, (dict, list)))
#                     elif isinstance(node, list):
#                         stack.extend(node)
#             except Exception:
#                 pass
#     except Exception as e:
#         debug(f"JSON-LD error: {e}")
#     return ""

# # ── Consent banner dismissal ──────────────────────────────────────────────────
# CONSENT_TEXTS = [
#     'Accept', 'Accept All', 'Agree', 'Continue', 'OK', 'Okay',
#     'Yes', 'Confirm', 'Got it', 'Allow', 'Proceed', 'I Agree',
#     'Accept Cookies', 'Close', 'Dismiss', 'No Thanks'
# ]
# CONSENT_SELECTORS = [
#     "button", "a", "div[role='button']", "span[role='button']",
#     "[class*='accept']", "[class*='agree']", "[class*='consent']",
#     "[id*='accept']", "[id*='agree']", "[id*='cookie']",
# ]

# def dismiss_consent(page):
#     for text in CONSENT_TEXTS:
#         for sel in ["button", "a", "[role='button']"]:
#             try:
#                 loc = page.locator(f"{sel}:has-text('{text}')").first
#                 if loc.count() > 0 and loc.is_visible():
#                     loc.click(timeout=2000)
#                     debug(f"Dismissed consent: '{text}'")
#                     page.wait_for_timeout(500)
#                     return
#             except Exception:
#                 pass

# # ── tel: link extraction ──────────────────────────────────────────────────────
# def extract_tel_links(page):
#     try:
#         hrefs = page.eval_on_selector_all(
#             "a[href^='tel:']",
#             "els => els.map(e => e.getAttribute('href'))"
#         )
#         for href in hrefs:
#             p = find_phone(href.replace("tel:", ""))
#             if p:
#                 debug(f"Found in tel: link: {p}")
#                 return p
#     except Exception as e:
#         debug(f"tel link error: {e}")
#     return ""

# # ── Meta tag extraction ───────────────────────────────────────────────────────
# def extract_meta(page):
#     try:
#         metas = page.eval_on_selector_all(
#             "meta",
#             "els => els.map(e => e.getAttribute('content') || '')"
#         )
#         for content in metas:
#             p = find_phone(content)
#             if p:
#                 debug(f"Found in meta: {p}")
#                 return p
#     except Exception:
#         pass
#     return ""

# # ── Main ──────────────────────────────────────────────────────────────────────
# with open(sys.argv[1]) as f:
#     url = json.load(f)["url"]

# # Quick check: phone in the URL itself
# p = find_phone(url)
# if p:
#     debug(f"Found in URL: {p}")
#     print(p)
#     sys.exit(0)

# with sync_playwright() as pw:
#     browser = pw.chromium.launch(
#         headless=True,
#         args=[
#             "--disable-blink-features=AutomationControlled",
#             "--no-sandbox",
#             "--disable-gpu",
#             "--disable-dev-shm-usage",
#             "--disable-setuid-sandbox",
#         ]
#     )
#     context = browser.new_context(
#         user_agent=(
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/124.0.0.0 Safari/537.36"
#         ),
#         viewport={"width": 1366, "height": 768},
#         locale="en-US",
#         java_script_enabled=True,
#     )
#     page = context.new_page()

#     # Block heavy assets to speed up load — keep JS and HTML
#     page.route(
#         "**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,ttf,eot,mp4,mp3,pdf}",
#         lambda route: route.abort()
#     )
#     page.add_init_script(
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
#     )

#     phone = ""

#     try:
#         # Use domcontentloaded instead of networkidle — more reliable
#         try:
#             page.goto(url, timeout=30000, wait_until="domcontentloaded")
#         except PWTimeout:
#             debug("domcontentloaded timed out, proceeding anyway")

#         page.wait_for_timeout(2000)
#         dismiss_consent(page)
#         page.wait_for_timeout(1000)

#         # ── Strategy 0: Click any buttons that might reveal phone numbers ───
#         try:
#             button_texts = [
#                 'call', 'phone', 'contact', 'help', 'support', 'click', 
#                 'talk', 'speak', 'agent', 'now', 'free', 'get help',
#                 'call now', 'call us', 'speak to', 'contact us', 'accept',
#             ]
#             buttons = page.locator("button, a, [role='button'], input[type='button'], input[type='submit']")
#             count = buttons.count()
#             for i in range(min(count, 20)):
#                 try:
#                     btn = buttons.nth(i)
#                     btn_text = (btn.inner_text() or "").lower()
#                     if any(t in btn_text for t in button_texts):
#                         debug(f"Clicking button: {btn_text}")
#                         btn.click(timeout=3000)
#                         page.wait_for_timeout(2000)
#                         # Check for phone after each click
#                         phone = find_phone(page.content())
#                         if phone:
#                             debug(f"Found phone after clicking button '{btn_text}': {phone}")
#                             print(phone)
#                             sys.exit(0)
#                         phone = extract_tel_links(page)
#                         if phone:
#                             debug(f"Found tel link after clicking button '{btn_text}': {phone}")
#                             print(phone)
#                             sys.exit(0)
#                 except Exception as e:
#                     debug(f"Button click error: {e}")
#                     continue
#         except Exception as e:
#             debug(f"Button strategy error: {e}")

#         # ── Strategy 0b: Click ALL buttons regardless of text ────────────────
#         try:
#             all_buttons = page.locator("button, input[type='button'], input[type='submit']")
#             count = all_buttons.count()
#             for i in range(min(count, 10)):
#                 try:
#                     btn = all_buttons.nth(i)
#                     if btn.is_visible():
#                         btn.click(timeout=2000)
#                         page.wait_for_timeout(1500)
#                         phone = find_phone(page.content())
#                         if phone:
#                             debug(f"Found phone after clicking button #{i}: {phone}")
#                             print(phone)
#                             sys.exit(0)
#                 except Exception:
#                     continue
#         except Exception as e:
#             debug(f"All buttons strategy error: {e}")
#         # ── Strategy 1: JSON-LD ─────────────────────────────────────────────
#         phone = extract_jsonld(page)
#         if phone:
#             print(phone)
#             sys.exit(0)

#         # ── Strategy 2: tel: links ──────────────────────────────────────────
#         phone = extract_tel_links(page)
#         if phone:
#             print(phone)
#             sys.exit(0)

#         # ── Strategy 3: meta tags ───────────────────────────────────────────
#         phone = extract_meta(page)
#         if phone:
#             print(phone)
#             sys.exit(0)

#         # ── Strategy 4: visible text (with scroll for footer numbers) ───────
#         for scroll_y in [0, 0.25, 0.5, 0.75, 1.0]:
#             try:
#                 page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {scroll_y})")
#                 page.wait_for_timeout(800)
#             except Exception:
#                 pass

#             # Try waiting for any lazy-loaded content to appear
#             try:
#                 page.wait_for_load_state("networkidle", timeout=5000)
#             except Exception:
#                 pass

#             for label, getter in [
#                 ("body_text", lambda: page.inner_text("body")),
#                 ("full_html",  lambda: page.content()),
#                 ("inner_text", lambda: page.evaluate(
#                     "() => document.documentElement.innerText || ''"
#                 )),
#             ]:
#                 try:
#                     data = getter()
#                     phone = find_phone(data)
#                     if phone:
#                         debug(f"Found in {label} at scroll={scroll_y}: {phone}")
#                         break
#                 except Exception as e:
#                     debug(f"{label} error: {e}")

#             if phone:
#                 break

#         # ── Strategy 5: iframes ─────────────────────────────────────────────
#         if not phone:
#             for frame in page.frames:
#                 if frame == page.main_frame:
#                     continue
#                 try:
#                     ft = frame.evaluate(
#                         "() => document.body ? document.body.innerText : ''"
#                     )
#                     phone = find_phone(ft)
#                     if phone:
#                         debug(f"Found in iframe: {phone}")
#                         break
#                 except Exception:
#                     pass

#         # ── Strategy 6: shadow DOM ──────────────────────────────────────────
#         if not phone:
#             try:
#                 shadow_text = page.evaluate(r"""
#                     () => {
#                         const results = [];
#                         const walk = (root) => {
#                             root.querySelectorAll('*').forEach(el => {
#                                 if (el.shadowRoot) walk(el.shadowRoot);
#                                 const t = el.textContent || '';
#                                 if (t.match(/\b(800|833|844|855|866|877|888)\b/)) {
#                                     results.push(t.trim().substring(0, 200));
#                                 }
#                             });
#                         };
#                         walk(document);
#                         return results.join(' ');
#                     }
#                 """)
#                 phone = find_phone(shadow_text)
#                 if phone:
#                     debug(f"Found in shadow DOM: {phone}")
#             except Exception as e:
#                 debug(f"Shadow DOM error: {e}")

#     except Exception as e:
#         debug(f"Top-level error: {e}")
#     finally:
#         try:
#             body_sample = page.inner_text("body")[:500]
#             debug(f"Final phone={phone!r} body_sample={body_sample!r}")
#         except Exception:
#             debug(f"Final phone={phone!r} (body unreadable)")
#         browser.close()

# print(phone)
# '''


# # ── Public API ─────────────────────────────────────────────────────────────────
# def extract_phone_from_url(url: str) -> str:
#     """
#     Extract a toll-free phone number from any URL.

#     Strategies (in order):
#       1. Phone in the URL string itself
#       2. JSON-LD / schema.org structured data
#       3. <a href="tel:..."> links
#       4. <meta> tag content
#       5. Visible page text (with scroll to expose footer numbers)
#       6. iframes
#       7. Shadow DOM

#     Returns a clean 10-digit string (e.g. "8001234567") or "" if not found.
#     """
#     # Fast-path: check URL before spinning up Playwright
#     phone = find_phone_in_text(url)
#     if phone:
#         logger.debug(f"Phone found in URL directly: {phone}")
#         return phone

#     script_file: str | None = None
#     tmp_path: str | None = None

#     try:
#         # Write Playwright script to a temp file
#         with tempfile.NamedTemporaryFile(
#             mode='w', suffix='.py', delete=False, encoding='utf-8'
#         ) as sf:
#             sf.write(_PLAYWRIGHT_SCRIPT)
#             script_file = sf.name

#         # Write URL payload
#         with tempfile.NamedTemporaryFile(
#             mode='w', suffix='.json', delete=False, encoding='utf-8'
#         ) as f:
#             json.dump({"url": url}, f)
#             tmp_path = f.name

#         result = subprocess.run(
#             [sys.executable, script_file, tmp_path],
#             capture_output=True,
#             text=True,
#             timeout=TIMEOUT_PLAYWRIGHT,
#         )

#         # Log raw output for debugging
#         if result.stdout.strip():
#             logger.debug(f"STDOUT: {result.stdout.strip()!r}")
#         if result.stderr.strip():
#             logger.debug(f"STDERR (playwright):\n{result.stderr.strip()}")

#         phone = result.stdout.strip()

#         # Validate what came back — subprocess output could be garbage
#         if phone and clean_phone(phone):
#             return phone

#         logger.warning(f"No toll-free number found for: {url}")
#         return ""

#     except subprocess.TimeoutExpired:
#         logger.error(f"Playwright timed out ({TIMEOUT_PLAYWRIGHT}s) for: {url}")
#         return ""
#     except Exception as e:
#         logger.error(f"Playwright extraction failed for {url}: {e}")
#         return ""
#     finally:
#         for path in [script_file, tmp_path]:
#             if path and os.path.exists(path):
#                 try:
#                     os.unlink(path)
#                 except Exception:
#                     pass



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
TIMEOUT_PLAYWRIGHT = 120


@dataclass
class RespOrgResult:
    resporg_code: str
    carrier_name: str
    abuse_email: str
    website: str
    is_toll_free: bool
    company_name: str = ""
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
    """Lookup carrier using IPQualityScore + Twilio caller name."""
    digits = normalize_phone(phone)
    e164 = f"+1{digits}"
    logger.debug(f"lookup_resporg: normalized E.164 = {e164}")

    api_key = os.getenv("IPQS_API_KEY")
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
        logger.info(f"IPQS company_name field: {data.get('name', 'NOT FOUND')}")

        carrier = data.get("carrier", "Unknown Carrier")
        line_type = data.get("line_type", "")
        is_valid = data.get("valid", False)
        is_voip = data.get("VOIP", False)
        is_toll_free = line_type.lower() in ("toll free", "toll_free", "tollfree") if line_type else False
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

    # --- Twilio Caller Name ---
    company_name = ""
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        if account_sid and auth_token:
            twilio_url = f"https://lookups.twilio.com/v2/PhoneNumbers/{e164}"
            twilio_resp = req.get(
                twilio_url,
                params={"Fields": "caller_name"},
                auth=(account_sid, auth_token),
                timeout=TIMEOUT_ABSTRACT,
            )
            if twilio_resp.status_code == 200:
                twilio_data = twilio_resp.json()
                caller_name_data = twilio_data.get("caller_name", {})
                company_name = caller_name_data.get("caller_name") or ""
                logger.info(f"Twilio caller name for {e164}: {company_name!r}")
            else:
                logger.warning(f"Twilio lookup returned {twilio_resp.status_code} for {e164}: {twilio_resp.text}")
    except Exception as e:
        logger.warning(f"Twilio caller name lookup failed for {e164}: {e}")
    
    logger.info(
        f"Result for {e164}: carrier={carrier!r}, company={company_name!r}, "
        f"type={line_type!r}, valid={is_valid}, is_toll_free={is_toll_free}"
    )

    return RespOrgResult(
        resporg_code="",
        carrier_name=carrier,
        company_name=company_name,
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




# def lookup_resporg(phone: str) -> RespOrgResult:
#     """Lookup carrier using IPQualityScore phone validation."""
#     digits = normalize_phone(phone)
#     e164 = f"+1{digits}"
#     logger.debug(f"lookup_resporg: normalized E.164 = {e164}")

#     api_key = os.getenv("IPQS_API_KEY")
#     logger.error(f"IPQS API KEY LOADED : {repr(api_key)}")
#     if not api_key:
#         logger.error("IPQS_API_KEY is not set in environment.")
#         return RespOrgResult("", "Unknown Carrier", "", "", False)

#     url = f"https://www.ipqualityscore.com/api/json/phone/{api_key}/{e164}"
#     params = {
#         "strictness": 0,
#         "allow_prepaid": True,
#     }

#     try:
#         response = req.get(url, params=params, timeout=TIMEOUT_ABSTRACT)
#         logger.debug(f"HTTP Status: {response.status_code}")

#         if response.status_code == 401:
#             logger.error("IPQS returned 401 — check your IPQS_API_KEY.")
#             return RespOrgResult("", "Auth Failed", "", "", False)

#         response.raise_for_status()
#         data = response.json()
#         logger.error(f"FULL API RESPONSE: {response.text}")

#         carrier = data.get("carrier", "Unknown Carrier")
#         line_type = data.get("line_type", "")
#         is_valid = data.get("valid", False)
#         is_voip = data.get("VOIP", False)
#         is_toll_free = line_type.lower() in ("toll free", "toll_free", "tollfree") if line_type else False
#         country = data.get("country", "")
#         region = data.get("region", "")
#         city = data.get("city", "")
#         timezone = data.get("timezone", "")
#         international_format = data.get("formatted", "")
#         national_format = data.get("local_format", "")
#         risk_level = "high" if data.get("fraud_score", 0) >= 75 else "medium" if data.get("fraud_score", 0) >= 50 else "low"
#         is_disposable = data.get("prepaid", False)
#         is_abuse_detected = data.get("recent_abuse", False)
#         line_status = "active" if data.get("active", False) else "inactive"

#         logger.info(
#             f"Result for {e164}: carrier={carrier!r}, "
#             f"type={line_type!r}, valid={is_valid}, is_toll_free={is_toll_free}"
#         )

#         return RespOrgResult(
#             resporg_code="",
#             carrier_name=carrier,
#             abuse_email="",
#             website="",
#             is_toll_free=is_toll_free,
#             line_type=line_type,
#             is_valid=is_valid,
#             is_voip=is_voip,
#             country=country,
#             region=region,
#             city=city,
#             timezone=timezone,
#             international_format=international_format,
#             national_format=national_format,
#             risk_level=risk_level,
#             is_disposable=is_disposable,
#             is_abuse_detected=is_abuse_detected,
#             line_status=line_status,
#             sms_email="",
#             sms_domain="",
#             mcc="",
#             mnc="",
#         )

#     except req.exceptions.Timeout:
#         logger.error(f"IPQS request timed out for {e164}")
#         return RespOrgResult("", "Timeout", "", "", False)

#     except req.exceptions.ConnectionError as e:
#         logger.error(f"Network connection error: {e}")
#         return RespOrgResult("", "Connection Error", "", "", False)

#     except req.exceptions.HTTPError as e:
#         logger.error(f"IPQS HTTP error: {e}")
#         return RespOrgResult("", "HTTP Error", "", "", False)

#     except Exception as e:
#         logger.exception(f"Unexpected error during IPQS lookup for {e164}: {e}")
#         return RespOrgResult("", "Unknown Carrier", "", "", False)



# def extract_phone_from_url(url: str) -> str:
#     """Extract toll-free number from URL."""

#     def find_phone(text):
#         if not text:
#             return ""
#         # +1(877) 513-7794
#         m = re.search(r'\+1\((\d{3})\)\s*(\d{3})-(\d{4})', text)
#         if m:
#             return f"1{m.group(1)}{m.group(2)}{m.group(3)}"
#         # +1-855-404-5252
#         m = re.search(r'\+1-(\d{3})-(\d{3})-(\d{4})', text)
#         if m:
#             return f"1{m.group(1)}{m.group(2)}{m.group(3)}"
#         # 1-855-404-5252 or (855) 404-5252 or 8554045252
#         m = re.search(
#             r'1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}',
#             text
#         )
#         if m:
#             return re.sub(r'\D', '', m.group())
#         return ""

#     # Step 1 — check URL params
#     try:
#         parsed = urlparse(url)
#         params = parse_qs(parsed.query)
#         for key, values in params.items():
#             value = values[0]
#             digits = re.sub(r'\D', '', value)
#             if len(digits) >= 10:
#                 prefix = digits[-10:][:3]
#                 if prefix in ("800", "833", "844", "855", "866", "877", "888"):
#                     logger.info(f"Phone found in URL param '{key}': {digits}")
#                     return digits
#     except Exception as e:
#         logger.warning(f"URL param check failed: {e}")

#     # Step 2 — curl (fast, static pages)
#     try:
#         curl_result = subprocess.run(
#             [
#                 "curl", "-sL", "--max-time", "10", "--compressed",
#                 "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#                 "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                 "-H", "Accept-Language: en-US,en;q=0.5",
#                 url
#             ],
#             capture_output=True, text=True, timeout=15,
#         )
#         phone = find_phone(curl_result.stdout)
#         if phone:
#             logger.info(f"[SCRAPE] Phone found via curl: {phone}")
#             return phone
#     except Exception as e:
#         logger.warning(f"curl failed: {e}")

#     # Step 3 — Playwright (JavaScript pages)
#     script_content = r"""
# import sys, json, re
# from playwright.sync_api import sync_playwright

# with open(sys.argv[1]) as f:
#     url = json.load(f)["url"]

# def find_phone(text):
#     if not text:
#         return ""
#     m = re.search(r'\+1\((\d{3})\)\s*(\d{3})-(\d{4})', text)
#     if m:
#         return f"1{m.group(1)}{m.group(2)}{m.group(3)}"
#     m = re.search(r'\+1-(\d{3})-(\d{3})-(\d{4})', text)
#     if m:
#         return f"1{m.group(1)}{m.group(2)}{m.group(3)}"
#     m = re.search(r'1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
#     if m:
#         return re.sub(r'\D', '', m.group())
#     return ""

# with sync_playwright() as p:
#     browser = p.chromium.launch(
#         headless=True,
#         args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-gpu"]
#     )
#     context = browser.new_context(
#         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#         viewport={"width": 1366, "height": 768},
#         locale="en-US",
#     )
#     page = context.new_page()
#     page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,eot}", lambda route: route.abort())
#     page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

#     phone = ""

#     try:
#         response = page.goto(url, timeout=30000, wait_until="commit")
#         status = response.status if response else 0

#         if status in (403, 404):
#             browser.close()
#             sys.exit(0)

#         # Wait for JS to render
#         page.wait_for_timeout(5000)

#         # Click Accept button if present — phone appears after click
#         try:
#             page.evaluate(
#                 "() => {"
#                 "  var btns = Array.from(document.querySelectorAll('button'));"
#                 "  var accept = btns.find(function(b) { return b.textContent.trim() === 'Accept'; });"
#                 "  if (accept) accept.click();"
#                 "}"
#             )
#             page.wait_for_timeout(3000)
#         except:
#             pass

#         # Check tel: links
#         tel_links = page.eval_on_selector_all("a[href^='tel:']", "els => els.map(e => e.href)")
#         for tel in tel_links:
#             digits = re.sub(r'\D', '', tel.replace("tel:", ""))
#             if len(digits) >= 10:
#                 prefix = digits[-10:][:3]
#                 if prefix in ("800", "833", "844", "855", "866", "877", "888"):
#                     phone = digits
#                     break

#         # Check full page source
#         if not phone:
#             phone = find_phone(page.content())

#         # Check body text
#         if not phone:
#             phone = find_phone(page.inner_text("body"))

#     except Exception as e:
#         print(f"ERROR: {e}", file=sys.stderr)

#     browser.close()
#     print(phone)
# """

#     script_file = None
#     tmp_path = None
#     try:
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
#             sf.write(script_content)
#             script_file = sf.name

#         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
#             json.dump({"url": url}, f)
#             tmp_path = f.name

#         result = subprocess.run(
#             [sys.executable, script_file, tmp_path],
#             capture_output=True, text=True,
#             timeout=TIMEOUT_PLAYWRIGHT,
#         )

#         phone = result.stdout.strip()
#         if result.stderr:
#             logger.debug(f"Playwright stderr:\n{result.stderr}")
#         if phone:
#             logger.info(f"[SCRAPE] Phone found via Playwright: {phone}")
#             return phone
#         return ""

#     except subprocess.TimeoutExpired:
#         logger.error(f"Playwright timed out for {url}")
#         return ""
#     except Exception as e:
#         logger.error(f"Playwright failed for {url}: {e}")
#         return ""
#     finally:
#         if script_file and os.path.exists(script_file):
#             os.unlink(script_file)
#         if tmp_path and os.path.exists(tmp_path):
#             try:
#                 os.unlink(tmp_path)
#             except:
#                 pass


            
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
 
 




# TIMEOUT_PLAYWRIGHT = 60


# def extract_phone_from_url(url: str) -> str:
#     """Extract toll-free number from URL using Playwright."""
    
#     script_content = r"""
# import sys, json, re
# from playwright.sync_api import sync_playwright

# TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
# TOLL_FREE_PATTERN = re.compile(r'1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}')

# def clean_phone(raw):
#     digits = re.sub(r'\D', '', raw)
#     if len(digits) == 11 and digits.startswith('1'):
#         digits = digits[1:]
#     if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
#         return digits
#     return None

# def find_phone(text):
#     if not text:
#         return ""
#     for match in TOLL_FREE_PATTERN.finditer(text):
#         cleaned = clean_phone(match.group())
#         if cleaned:
#             return cleaned
#     return ""

# with open(sys.argv[1]) as f:
#     url = json.load(f)["url"]

# with sync_playwright() as p:
#     browser = p.chromium.launch(
#         headless=True,
#         args=[
#             "--disable-blink-features=AutomationControlled",
#             "--no-sandbox",
#             "--disable-gpu",
#             "--disable-dev-shm-usage",
#         ]
#     )
#     context = browser.new_context(
#         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#         viewport={"width": 1366, "height": 768},
#         locale="en-US",
#     )
#     page = context.new_page()

#     page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,eot}", lambda route: route.abort())
#     page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
#     phone = ""
    
#     try:
#         page.goto(url, timeout=25000, wait_until="networkidle")
#         page.wait_for_timeout(2000)
        
#         # === CLICK ANY BLOCKER BUTTON ===
#         clicked = False
#         for text in ['Accept', 'Agree', 'Continue', 'OK', 'Yes', 'Confirm', 'Got it', 'Allow', 'Proceed', 'Ignore']:
#             try:
#                 # Try multiple selector strategies
#                 selectors = [
#                     f"button:has-text('{text}')",
#                     f"[role='button']:has-text('{text}')",
#                     f"a:has-text('{text}')",
#                     f"div:has-text('{text}')",
#                 ]
#                 for sel in selectors:
#                     loc = page.locator(sel).first
#                     if loc.count() > 0:
#                         loc.click()
#                         clicked = True
#                         print(f"DEBUG: Clicked '{text}'", file=sys.stderr)
#                         break
#                 if clicked:
#                     break
#             except:
#                 pass
        
#         # === KEY: Wait 8 seconds AFTER click for JS to inject phone ===
#         page.wait_for_timeout(8000)
        
#         # === SCAN EVERYTHING ===
#         # 1. tel: links
#         try:
#             tel_links = page.eval_on_selector_all("a[href^='tel:']", "els => els.map(e => e.getAttribute('href'))")
#             for tel in tel_links:
#                 phone = find_phone(tel)
#                 if phone:
#                     break
#         except:
#             pass

#         # 2. Full HTML source
#         if not phone:
#             try:
#                 phone = find_phone(page.content())
#             except:
#                 pass

#         # 3. Body text
#         if not phone:
#             try:
#                 phone = find_phone(page.inner_text("body"))
#             except:
#                 pass

#         # 4. All text including hidden
#         if not phone:
#             try:
#                 all_text = page.evaluate("() => document.documentElement.innerText || document.documentElement.textContent || ''")
#                 phone = find_phone(all_text)
#             except:
#                 pass

#         # 5. All element attributes
#         if not phone:
#             try:
#                 all_attrs = page.evaluate('''
#                     () => {
#                         const els = document.querySelectorAll('*');
#                         let text = '';
#                         for (const el of els) {
#                             for (const attr of el.attributes) {
#                                 text += ' ' + attr.value;
#                             }
#                         }
#                         return text;
#                     }
#                 ''')
#                 phone = find_phone(all_attrs)
#             except:
#                 pass

#         # 6. Iframes
#         if not phone:
#             try:
#                 for frame in page.frames:
#                     try:
#                         frame_text = frame.evaluate("() => document.body ? document.body.innerText : ''")
#                         phone = find_phone(frame_text)
#                         if phone:
#                             break
#                     except:
#                         pass
#             except:
#                 pass

#     except Exception as e:
#         print(f"DEBUG ERROR: {e}", file=sys.stderr)
    
#     # Debug output
#     try:
#         body = page.inner_text("body")
#         print(f"DEBUG: phone={phone}, body_sample={repr(body[:500])}", file=sys.stderr)
#     except:
#         print(f"DEBUG: phone={phone}, no_body", file=sys.stderr)
    
#     browser.close()
#     print(phone)
# """

#     script_file = None
#     tmp_path = None
#     try:
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
#             sf.write(script_content)
#             script_file = sf.name

#         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
#             json.dump({"url": url}, f)
#             tmp_path = f.name

#         result = subprocess.run(
#             [sys.executable, script_file, tmp_path],
#             capture_output=True,
#             text=True,
#             timeout=TIMEOUT_PLAYWRIGHT,
#         )

#         phone = result.stdout.strip()
#         if result.stderr:
#             logger.error(f"Playwright debug: {result.stderr.strip()}")
#         if phone:
#             return phone
#         return ""

#     except subprocess.TimeoutExpired:
#         logger.error(f"Playwright extraction timed out for {url}")
#         return ""
#     except Exception as e:
#         logger.error(f"Playwright extraction failed for {url}: {e}")
#         return ""
#     finally:
#         if script_file and os.path.exists(script_file):
#             os.unlink(script_file)
#         if tmp_path and os.path.exists(tmp_path):
#             try:
#                 os.unlink(tmp_path)
#             except:
#                 pass





# TIMEOUT_PLAYWRIGHT = 60


# def extract_phone_from_url(url: str) -> str:
#     """Extract toll-free number from URL using Playwright."""
    
#     script_content = r"""
# import sys, json, re
# from playwright.sync_api import sync_playwright

# TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
# TOLL_FREE_PATTERN = re.compile(r'1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}')

# def clean_phone(raw):
#     digits = re.sub(r'\D', '', raw)
#     if len(digits) == 11 and digits.startswith('1'):
#         digits = digits[1:]
#     if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
#         return digits
#     return None

# def find_phone(text):
#     if not text:
#         return ""
#     for match in TOLL_FREE_PATTERN.finditer(text):
#         cleaned = clean_phone(match.group())
#         if cleaned:
#             return cleaned
#     return ""

# with open(sys.argv[1]) as f:
#     url = json.load(f)["url"]

# with sync_playwright() as p:
#     browser = p.chromium.launch(
#         headless=True,
#         args=[
#             "--disable-blink-features=AutomationControlled",
#             "--no-sandbox",
#             "--disable-gpu",
#             "--disable-dev-shm-usage",
#         ]
#     )
#     context = browser.new_context(
#         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#         viewport={"width": 1366, "height": 768},
#         locale="en-US",
#     )
#     page = context.new_page()

#     page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,eot}", lambda route: route.abort())
#     page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
#     phone = ""
    
#     try:
#         page.goto(url, timeout=25000, wait_until="networkidle")
#         page.wait_for_timeout(2000)
        
#         # === CLICK ACCEPT OR ANY BLOCKER ===
#         for text in ['Accept', 'Agree', 'Continue', 'OK', 'Yes', 'Confirm', 'Got it', 'Allow', 'Proceed', 'Ignore']:
#             try:
#                 loc = page.locator(f"button:has-text('{text}')").first
#                 if loc.count() > 0:
#                     loc.click()
#                     print(f"DEBUG: Clicked '{text}'", file=sys.stderr)
#                     break
#             except:
#                 pass
        
#         # === CRITICAL: Wait 10 seconds for JS to fetch and inject phone ===
#         page.wait_for_timeout(10000)
        
#         # === SCAN ALL SOURCES ===
#         sources = [
#             ("tel_links", lambda: page.eval_on_selector_all("a[href^='tel:']", "els => els.map(e => e.getAttribute('href'))")),
#             ("html", lambda: page.content()),
#             ("body", lambda: page.inner_text("body")),
#             ("all_text", lambda: page.evaluate("() => document.documentElement.innerText || document.documentElement.textContent || ''")),
#             ("attrs", lambda: page.evaluate("() => { const els = document.querySelectorAll('*'); let t = ''; for (const e of els) { for (const a of e.attributes) { t += ' ' + a.value; } } return t; }")),
#         ]
        
#         for name, getter in sources:
#             try:
#                 data = getter()
#                 if isinstance(data, list):
#                     for item in data:
#                         phone = find_phone(item)
#                         if phone:
#                             print(f"DEBUG: Found in {name}: {phone}", file=sys.stderr)
#                             break
#                 else:
#                     phone = find_phone(data)
#                     if phone:
#                         print(f"DEBUG: Found in {name}: {phone}", file=sys.stderr)
#                         break
#             except Exception as e:
#                 print(f"DEBUG: {name} error: {e}", file=sys.stderr)
#             if phone:
#                 break
        
#         # === IFRAMES ===
#         if not phone:
#             try:
#                 for frame in page.frames:
#                     try:
#                         ft = frame.evaluate("() => document.body ? document.body.innerText : ''")
#                         phone = find_phone(ft)
#                         if phone:
#                             print(f"DEBUG: Found in iframe: {phone}", file=sys.stderr)
#                             break
#                     except:
#                         pass
#             except:
#                 pass

#     except Exception as e:
#         print(f"DEBUG ERROR: {e}", file=sys.stderr)
    
#     try:
#         body = page.inner_text("body")
#         print(f"DEBUG FINAL: phone={phone}, body={repr(body[:600])}", file=sys.stderr)
#     except:
#         print(f"DEBUG FINAL: phone={phone}, no body", file=sys.stderr)
    
#     browser.close()
#     print(phone)
# """

#     script_file = None
#     tmp_path = None
#     try:
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
#             sf.write(script_content)
#             script_file = sf.name

#         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
#             json.dump({"url": url}, f)
#             tmp_path = f.name

#         result = subprocess.run(
#             [sys.executable, script_file, tmp_path],
#             capture_output=True,
#             text=True,
#             timeout=TIMEOUT_PLAYWRIGHT,
#         )

#         phone = result.stdout.strip()
#         if result.stderr:
#             logger.error(f"Playwright debug: {result.stderr.strip()}")
#         if phone:
#             return phone
#         return ""

#     except subprocess.TimeoutExpired:
#         logger.error(f"Playwright extraction timed out for {url}")
#         return ""
#     except Exception as e:
#         logger.error(f"Playwright extraction failed for {url}: {e}")
#         return ""
#     finally:
#         if script_file and os.path.exists(script_file):
#             os.unlink(script_file)
#         if tmp_path and os.path.exists(tmp_path):
#             try:
#                 os.unlink(tmp_path)
#             except:
#                 pass



# TIMEOUT_PLAYWRIGHT = 60

# # FIXED: Added \+? to handle +1 prefix
# TOLL_FREE_PATTERN = re.compile(r'\+?1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}')


# def extract_phone_from_url(url: str) -> str:
#     """Extract toll-free number from URL using Playwright."""
    
#     TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
    
#     def clean_phone(raw):
#         if not raw or raw == "null":
#             return None
#         digits = re.sub(r'\D', '', raw)
#         if len(digits) == 11 and digits.startswith('1'):
#             digits = digits[1:]
#         if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
#             return digits
#         return None
    
#     # Check URL
#     for match in TOLL_FREE_PATTERN.finditer(url):
#         cleaned = clean_phone(match.group())
#         if cleaned:
#             return cleaned
    
#     script_content = r"""
# import sys, json, re
# from playwright.sync_api import sync_playwright

# TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
# # FIXED: Added \+? to handle +1 prefix
# TOLL_FREE_PATTERN = re.compile(r'\+?1?[-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}')

# def clean_phone(raw):
#     if not raw or raw == "null":
#         return None
#     digits = re.sub(r'\D', '', raw)
#     if len(digits) == 11 and digits.startswith('1'):
#         digits = digits[1:]
#     if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
#         return digits
#     return None

# def find_phone(text):
#     if not text:
#         return ""
#     for match in TOLL_FREE_PATTERN.finditer(text):
#         cleaned = clean_phone(match.group())
#         if cleaned:
#             return cleaned
#     return ""

# with open(sys.argv[1]) as f:
#     url = json.load(f)["url"]

# # Check URL
# for match in TOLL_FREE_PATTERN.finditer(url):
#     cleaned = clean_phone(match.group())
#     if cleaned:
#         print(cleaned)
#         sys.exit(0)

# with sync_playwright() as p:
#     browser = p.chromium.launch(
#         headless=True,
#         args=[
#             "--disable-blink-features=AutomationControlled",
#             "--no-sandbox",
#             "--disable-gpu",
#             "--disable-dev-shm-usage",
#         ]
#     )
#     context = browser.new_context(
#         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#         viewport={"width": 1366, "height": 768},
#         locale="en-US",
#     )
#     page = context.new_page()

#     page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,eot}", lambda route: route.abort())
#     page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
#     phone = ""
    
#     try:
#         page.goto(url, timeout=25000, wait_until="networkidle")
#         page.wait_for_timeout(2000)
        
#         # Click buttons
#         for text in ['Accept', 'Agree', 'Continue', 'OK', 'Yes', 'Confirm', 'Got it', 'Allow', 'Proceed', 'Ignore']:
#             try:
#                 loc = page.locator(f"button:has-text('{text}')").first
#                 if loc.count() > 0:
#                     loc.click()
#                     print(f"DEBUG: Clicked '{text}'", file=sys.stderr)
#                     break
#             except:
#                 pass
        
#         # Wait and poll
#         for i in range(5):
#             page.wait_for_timeout(3000)
            
#             for name, getter in [
#                 ("tel", lambda: page.eval_on_selector_all("a[href^='tel:']", "els => els.map(e => e.getAttribute('href'))")),
#                 ("html", lambda: page.content()),
#                 ("body", lambda: page.inner_text("body")),
#                 ("all", lambda: page.evaluate("() => document.documentElement.innerText || ''")),
#             ]:
#                 try:
#                     data = getter()
#                     if isinstance(data, list):
#                         for item in data:
#                             phone = find_phone(item)
#                             if phone:
#                                 print(f"DEBUG: Found {phone} in {name}", file=sys.stderr)
#                                 break
#                     else:
#                         phone = find_phone(data)
#                         if phone:
#                             print(f"DEBUG: Found {phone} in {name}", file=sys.stderr)
#                             break
#                 except:
#                     pass
#                 if phone:
#                     break
            
#             if phone:
#                 break
        
#         # Iframes
#         if not phone:
#             try:
#                 for frame in page.frames:
#                     try:
#                         ft = frame.evaluate("() => document.body ? document.body.innerText : ''")
#                         phone = find_phone(ft)
#                         if phone:
#                             print(f"DEBUG: Found {phone} in iframe", file=sys.stderr)
#                             break
#                     except:
#                         pass
#             except:
#                 pass

#     except Exception as e:
#         print(f"DEBUG ERROR: {e}", file=sys.stderr)
    
#     # Debug
#     try:
#         body = page.inner_text("body")
#         print(f"DEBUG: phone={phone} body_len={len(body)} sample={repr(body[:800])}", file=sys.stderr)
#     except Exception as e:
#         print(f"DEBUG: phone={phone} body_error={e}", file=sys.stderr)
    
#     browser.close()
#     print(phone)
# """

#     script_file = None
#     tmp_path = None
#     try:
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
#             sf.write(script_content)
#             script_file = sf.name

#         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
#             json.dump({"url": url}, f)
#             tmp_path = f.name

#         result = subprocess.run(
#             [sys.executable, script_file, tmp_path],
#             capture_output=True,
#             text=True,
#             timeout=TIMEOUT_PLAYWRIGHT,
#         )

#         # DEBUG: Always print raw output
#         print(f"RAW STDOUT: {result.stdout!r}", file=sys.stderr)
#         print(f"RAW STDERR: {result.stderr!r}", file=sys.stderr)

#         phone = result.stdout.strip()
#         if result.stderr:
#             logger.error(f"Playwright debug: {result.stderr.strip()}")
#         if phone:
#             return phone
#         return ""

#     except subprocess.TimeoutExpired:
#         logger.error(f"Playwright extraction timed out for {url}")
#         return ""
#     except Exception as e:
#         logger.error(f"Playwright extraction failed for {url}: {e}")
#         return ""
#     finally:
#         if script_file and os.path.exists(script_file):
#             os.unlink(script_file)
#         if tmp_path and os.path.exists(tmp_path):
#             try:
#                 os.unlink(tmp_path)
#             except:
#                 pass




"""
phone_extractor.py
------------------
Universal toll-free phone number extractor.
Extracts from: URL, JSON-LD/schema.org, tel: links, page text, iframes.
Handles: consent banners, lazy-load, SPAs, footer-hidden numbers, +1 prefix variants.
"""

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import pytesseract
from PIL import Image
import io

if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\YourName\tesseract\tesseract.exe'

logger = logging.getLogger(__name__)

TIMEOUT_PLAYWRIGHT = 90  # Increased: some sites are slow

# ── Regex ─────────────────────────────────────────────────────────────────────
# Covers:
#   +1-800-123-4567  |  1 (800) 123-4567  |  800.123.4567  |  8001234567
#   All separators: space, dash, dot, none
# TOLL_FREE_PATTERN = re.compile(
#     r'(?<!\d)'                                    # no leading digit
#     r'(?:\+?1[-.\s]?)?'                           # optional country code
#     r'\(?(800|833|844|855|866|877|888)\)?'        # area code
#     r'[-.\s]?\d{3}[-.\s]?\d{4}'                  # rest of number
#     r'(?!\d)'                                     # no trailing digit
# )

TOLL_FREE_PATTERN = re.compile(
    r'(?<!\d)'
    r'(?:\+?1[-.\s()]?)?'
    r'\(?(800|833|844|855|866|877|888)\)?'
    r'[-.\s()]?\d{3}[-.\s()]?\d{4}'
    r'(?!\d)',
    re.IGNORECASE
)

TOLL_FREE_EXTRAS = [
    re.compile(r'1[-.\s]?8[O0][O0][-.\s]?\d{3}[-.\s]?\d{4}', re.IGNORECASE),
    re.compile(r'(?:800|833|844|855|866|877|888)[\s\S]{0,3}\d{3}[\s\S]{0,3}\d{4}'),
    re.compile(r'(?:phone|tel|number|call)["\s:=]+([18][-.\s]?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4})', re.IGNORECASE),
    re.compile(r'\b(800|833|844|855|866|877|888)\d{7}\b'),
]

TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}




def clean_phone(raw: str) -> str | None:
    """Normalize any matched string to a clean 10-digit string or None."""
    if not raw or raw.strip().lower() == "null":
        return None
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
        return digits
    return None


# def find_phone_in_text(text: str) -> str:
#     """Scan arbitrary text and return the first valid toll-free number found."""
#     if not text:
#         return ""
#     for match in TOLL_FREE_PATTERN.finditer(text):
#         cleaned = clean_phone(match.group())
#         if cleaned:
#             return cleaned
#     return ""



def find_phone_in_text(text: str) -> str:
    """Scan arbitrary text and return the first valid toll-free number found."""
    if not text:
        return ""

    # Strategy A — primary pattern
    for match in TOLL_FREE_PATTERN.finditer(text):
        cleaned = clean_phone(match.group())
        if cleaned:
            return cleaned

    # Strategy B — extra patterns
    for pattern in TOLL_FREE_EXTRAS:
        for match in pattern.finditer(text):
            candidates = [match.group()] + list(match.groups())
            for candidate in candidates:
                if candidate:
                    cleaned = clean_phone(candidate)
                    if cleaned:
                        return cleaned

    # Strategy C — brute force digits scan
    digits_only = re.sub(r'\D', '', text)
    for prefix in TOLL_FREE_PREFIXES:
        idx = 0
        while True:
            idx = digits_only.find(prefix, idx)
            if idx == -1:
                break
            start = idx - 1 if idx > 0 and digits_only[idx - 1] == '1' else idx
            block = digits_only[start:start + (11 if start == idx - 1 else 10)]
            cleaned = clean_phone(block)
            if cleaned:
                return cleaned
            idx += 1

    return ""

# ── Playwright script (runs in subprocess) ────────────────────────────────────
_PLAYWRIGHT_SCRIPT = r'''
import sys, json, re, time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}
# TOLL_FREE_PATTERN = re.compile(
#     r'(?<!\d)(?:\+?1[-.\s]?)?\(?(800|833|844|855|866|877|888)\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)'
# )
TOLL_FREE_PATTERN = re.compile(
    r'(?<!\d)(?:\+?1[-.\s()]?)?\(?(800|833|844|855|866|877|888)\)?[-.\s()]?\d{3}[-.\s()]?\d{4}(?!\d)',
    re.IGNORECASE
)

def clean_phone(raw):
    if not raw or raw.strip().lower() == "null":
        return None
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
        return digits
    return None

# def find_phone(text):
#     if not text:
#         return ""
#     for match in TOLL_FREE_PATTERN.finditer(text):
#         c = clean_phone(match.group())
#         if c:
#             return c
#     return ""



def debug(msg):
    print(f"DEBUG: {msg}", file=sys.stderr)

# ── JSON-LD / schema.org extraction ──────────────────────────────────────────
def extract_jsonld(page):
    try:
        scripts = page.eval_on_selector_all(
            'script[type="application/ld+json"]',
            "els => els.map(e => e.textContent)"
        )
        for raw in scripts:
            try:
                data = json.loads(raw)
                # Flatten nested structures
                stack = [data] if isinstance(data, dict) else data if isinstance(data, list) else []
                while stack:
                    node = stack.pop()
                    if isinstance(node, dict):
                        for key in ("telephone", "phone", "contactPoint", "contactOption"):
                            val = node.get(key)
                            if isinstance(val, str):
                                p = find_phone(val)
                                if p:
                                    debug(f"Found in JSON-LD key={key}: {p}")
                                    return p
                            elif isinstance(val, dict):
                                stack.append(val)
                            elif isinstance(val, list):
                                stack.extend(val)
                        stack.extend(v for v in node.values() if isinstance(v, (dict, list)))
                    elif isinstance(node, list):
                        stack.extend(node)
            except Exception:
                pass
    except Exception as e:
        debug(f"JSON-LD error: {e}")
    return ""

# ── Consent banner dismissal ──────────────────────────────────────────────────
CONSENT_TEXTS = [
    'Accept', 'Accept All', 'Agree', 'Continue', 'OK', 'Okay',
    'Yes', 'Confirm', 'Got it', 'Allow', 'Proceed', 'I Agree',
    'Accept Cookies', 'Close', 'Dismiss', 'No Thanks'
]
CONSENT_SELECTORS = [
    "button", "a", "div[role='button']", "span[role='button']",
    "[class*='accept']", "[class*='agree']", "[class*='consent']",
    "[id*='accept']", "[id*='agree']", "[id*='cookie']",
]

def dismiss_consent(page):
    for text in CONSENT_TEXTS:
        for sel in ["button", "a", "[role='button']"]:
            try:
                loc = page.locator(f"{sel}:has-text('{text}')").first
                if loc.count() > 0 and loc.is_visible():
                    loc.click(timeout=2000)
                    debug(f"Dismissed consent: '{text}'")
                    page.wait_for_timeout(500)
                    return
            except Exception:
                pass

# ── tel: link extraction ──────────────────────────────────────────────────────
def extract_tel_links(page):
    try:
        hrefs = page.eval_on_selector_all(
            "a[href^='tel:']",
            "els => els.map(e => e.getAttribute('href'))"
        )
        for href in hrefs:
            p = find_phone(href.replace("tel:", ""))
            if p:
                debug(f"Found in tel: link: {p}")
                return p
    except Exception as e:
        debug(f"tel link error: {e}")
    return ""

# ── Meta tag extraction ───────────────────────────────────────────────────────
def extract_meta(page):
    try:
        metas = page.eval_on_selector_all(
            "meta",
            "els => els.map(e => e.getAttribute('content') || '')"
        )
        for content in metas:
            p = find_phone(content)
            if p:
                debug(f"Found in meta: {p}")
                return p
    except Exception:
        pass
    return ""

# ── Main ──────────────────────────────────────────────────────────────────────
with open(sys.argv[1]) as f:
    url = json.load(f)["url"]

# Quick check: phone in the URL itself
p = find_phone(url)
if p:
    debug(f"Found in URL: {p}")
    print(p)
    sys.exit(0)

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
        ]
    )
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 768},
        locale="en-US",
        java_script_enabled=True,
    )
    page = context.new_page()

    # Block heavy assets to speed up load — keep JS and HTML
    page.route(
        "**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,ttf,eot,mp4,mp3,pdf}",
        lambda route: route.abort()
    )
    page.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    phone = ""

    try:
        # Use domcontentloaded instead of networkidle — more reliable
        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
        except PWTimeout:
            debug("domcontentloaded timed out, proceeding anyway")

        page.wait_for_timeout(2000)
        dismiss_consent(page)
        page.wait_for_timeout(1000)

        # ── Strategy 0: Click any buttons that might reveal phone numbers ───
        try:
            button_texts = [
                'call', 'phone', 'contact', 'help', 'support', 'click', 
                'talk', 'speak', 'agent', 'now', 'free', 'get help',
                'call now', 'call us', 'speak to', 'contact us', 'accept',
            ]
            buttons = page.locator("button, a, [role='button'], input[type='button'], input[type='submit']")
            count = buttons.count()
            for i in range(min(count, 20)):
                try:
                    btn = buttons.nth(i)
                    btn_text = (btn.inner_text() or "").lower()
                    if any(t in btn_text for t in button_texts):
                        debug(f"Clicking button: {btn_text}")
                        btn.click(timeout=3000)
                        page.wait_for_timeout(2000)
                        # Check for phone after each click
                        phone = find_phone(page.content())
                        if phone:
                            debug(f"Found phone after clicking button '{btn_text}': {phone}")
                            print(phone)
                            sys.exit(0)
                        phone = extract_tel_links(page)
                        if phone:
                            debug(f"Found tel link after clicking button '{btn_text}': {phone}")
                            print(phone)
                            sys.exit(0)
                except Exception as e:
                    debug(f"Button click error: {e}")
                    continue
        except Exception as e:
            debug(f"Button strategy error: {e}")

        # ── Strategy 0b: Click ALL buttons regardless of text ────────────────
        try:
            all_buttons = page.locator("button, input[type='button'], input[type='submit']")
            count = all_buttons.count()
            for i in range(min(count, 10)):
                try:
                    btn = all_buttons.nth(i)
                    if btn.is_visible():
                        btn.click(timeout=2000)
                        page.wait_for_timeout(1500)
                        phone = find_phone(page.content())
                        if phone:
                            debug(f"Found phone after clicking button #{i}: {phone}")
                            print(phone)
                            sys.exit(0)
                except Exception:
                    continue
        except Exception as e:
            debug(f"All buttons strategy error: {e}")
        # ── Strategy 1: JSON-LD ─────────────────────────────────────────────
        phone = extract_jsonld(page)
        if phone:
            print(phone)
            sys.exit(0)

        # ── Strategy 2: tel: links ──────────────────────────────────────────
        phone = extract_tel_links(page)
        if phone:
            print(phone)
            sys.exit(0)

        # ── Strategy 3: meta tags ───────────────────────────────────────────
        phone = extract_meta(page)
        if phone:
            print(phone)
            sys.exit(0)

        # ── Strategy 4: visible text (with scroll for footer numbers) ───────
        for scroll_y in [0, 0.25, 0.5, 0.75, 1.0]:
            try:
                page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {scroll_y})")
                page.wait_for_timeout(800)
            except Exception:
                pass

            # Try waiting for any lazy-loaded content to appear
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass

            for label, getter in [
                ("body_text", lambda: page.inner_text("body")),
                ("full_html",  lambda: page.content()),
                ("inner_text", lambda: page.evaluate(
                    "() => document.documentElement.innerText || ''"
                )),
            ]:
                try:
                    data = getter()
                    phone = find_phone(data)
                    if phone:
                        debug(f"Found in {label} at scroll={scroll_y}: {phone}")
                        break
                except Exception as e:
                    debug(f"{label} error: {e}")

            if phone:
                break

        # ── Strategy 5: iframes ─────────────────────────────────────────────
        if not phone:
            for frame in page.frames:
                if frame == page.main_frame:
                    continue
                try:
                    ft = frame.evaluate(
                        "() => document.body ? document.body.innerText : ''"
                    )
                    phone = find_phone(ft)
                    if phone:
                        debug(f"Found in iframe: {phone}")
                        break
                except Exception:
                    pass

        # ── Strategy 6: shadow DOM ──────────────────────────────────────────
        if not phone:
            try:
                shadow_text = page.evaluate(r"""
                    () => {
                        const results = [];
                        const walk = (root) => {
                            root.querySelectorAll('*').forEach(el => {
                                if (el.shadowRoot) walk(el.shadowRoot);
                                const t = el.textContent || '';
                                if (t.match(/\b(800|833|844|855|866|877|888)\b/)) {
                                    results.push(t.trim().substring(0, 200));
                                }
                            });
                        };
                        walk(document);
                        return results.join(' ');
                    }
                """)
                phone = find_phone(shadow_text)
                if phone:
                    debug(f"Found in shadow DOM: {phone}")
            except Exception as e:
                debug(f"Shadow DOM error: {e}")

    except Exception as e:
        debug(f"Top-level error: {e}")
    finally:
        try:
            body_sample = page.inner_text("body")[:500]
            debug(f"Final phone={phone!r} body_sample={body_sample!r}")
        except Exception:
            debug(f"Final phone={phone!r} (body unreadable)")
        browser.close()

print(phone)
'''



def extract_phone_from_url(url: str) -> str:
    # Pass 1 — phone in URL itself
    phone = find_phone_in_text(url)
    if phone:
        return phone

    script_file = None
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as sf:
            sf.write(_PLAYWRIGHT_SCRIPT)
            script_file = sf.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({"url": url}, f)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, script_file, tmp_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_PLAYWRIGHT,
        )

        phone = result.stdout.strip()

        if result.stderr.strip():
            logger.debug(f"STDERR:\n{result.stderr.strip()}")

        # Pass 2 — validate playwright output
        if phone and clean_phone(phone):
            return phone

        # Pass 3 — run find_phone_in_text on ALL stderr debug output
        # sometimes the number appears in debug logs
        phone = find_phone_in_text(result.stderr)
        if phone:
            return phone

        # Pass 4 — run find_phone_in_text on combined stdout+stderr
        phone = find_phone_in_text(result.stdout + " " + result.stderr)
        if phone:
            return phone

        logger.warning(f"No toll-free number found for: {url}")
        return ""

    except subprocess.TimeoutExpired:
        logger.error(f"Playwright timed out ({TIMEOUT_PLAYWRIGHT}s) for: {url}")
        return ""
    except Exception as e:

        # Add this at the bottom of extract_phone_from_url

        try:
            import pytesseract
            from PIL import Image
            import io

            screenshot_result = subprocess.run(
                [sys.executable, "-c", f"""
        from playwright.sync_api import sync_playwright
        import sys
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            p = b.new_page()
            p.goto("{url}", timeout=30000, wait_until="networkidle")
            p.wait_for_timeout(5000)
            sys.stdout.buffer.write(p.screenshot(full_page=True))
            b.close()
        """],
                capture_output=True,
                timeout=60,
            )

            if screenshot_result.stdout:
                img = Image.open(io.BytesIO(screenshot_result.stdout))
                ocr_text = pytesseract.image_to_string(img)
                phone = find_phone_in_text(ocr_text)
                if phone:
                    logger.info(f"Found via OCR: {phone}")
                    return phone

        except Exception as e:
            logger.error(f"OCR failed: {e}")
        logger.error(f"Playwright extraction failed for {url}: {e}")
        return ""
    finally:
        for path in [script_file, tmp_path]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except Exception:
                    pass

# # ── Public API ─────────────────────────────────────────────────────────────────
# def extract_phone_from_url(url: str) -> str:
    """
    Extract a toll-free phone number from any URL.

    Strategies (in order):
      1. Phone in the URL string itself
      2. JSON-LD / schema.org structured data
      3. <a href="tel:..."> links
      4. <meta> tag content
      5. Visible page text (with scroll to expose footer numbers)
      6. iframes
      7. Shadow DOM

    Returns a clean 10-digit string (e.g. "8001234567") or "" if not found.
    """
    # Fast-path: check URL before spinning up Playwright
    phone = find_phone_in_text(url)
    if phone:
        logger.debug(f"Phone found in URL directly: {phone}")
        return phone

    script_file: str | None = None
    tmp_path: str | None = None

    try:
        # Write Playwright script to a temp file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, encoding='utf-8'
        ) as sf:
            sf.write(_PLAYWRIGHT_SCRIPT)
            script_file = sf.name

        # Write URL payload
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False, encoding='utf-8'
        ) as f:
            json.dump({"url": url}, f)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, script_file, tmp_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_PLAYWRIGHT,
        )

        # Log raw output for debugging
        if result.stdout.strip():
            logger.debug(f"STDOUT: {result.stdout.strip()!r}")
        if result.stderr.strip():
            logger.debug(f"STDERR (playwright):\n{result.stderr.strip()}")

        phone = result.stdout.strip()

        # Validate what came back — subprocess output could be garbage
        if phone and clean_phone(phone):
            return phone

        logger.warning(f"No toll-free number found for: {url}")
        return ""

    except subprocess.TimeoutExpired:
        logger.error(f"Playwright timed out ({TIMEOUT_PLAYWRIGHT}s) for: {url}")
        return ""
    except Exception as e:
        logger.error(f"Playwright extraction failed for {url}: {e}")
        return ""
    finally:
        for path in [script_file, tmp_path]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except Exception:
                    pass