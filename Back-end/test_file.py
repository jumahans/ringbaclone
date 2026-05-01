# from seleniumbase import SB
# import pytesseract
# from PIL import Image
# import io
# import base64
# import re
# import logging

# logger = logging.getLogger(__name__)

# TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}


# def clean_phone(raw: str):
#     if not raw:
#         return None
#     digits = re.sub(r'\D', '', raw)
#     if len(digits) == 11 and digits.startswith('1'):
#         digits = digits[1:]
#     if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
#         return digits
#     return None


# def js_str(value: str) -> str:
#     """Safely escape a string for direct embedding in a JS snippet."""
#     escaped = value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
#     return f"'{escaped}'"


# def scrape_800forall_cnam(phone_number: str, max_retries: int = 5) -> str:
#     for attempt in range(1, max_retries + 1):
#         logger.info(f"[800FORALL] Attempt {attempt}/{max_retries} for {phone_number}")
#         try:
#             with SB(browser="chrome", headless=True, undetectable=True) as sb:

#                 sb.open("https://www.800forall.com/SearchWhoOwns.aspx")
#                 sb.wait_for_element_visible("input#txtNumber", timeout=15)

#                 # ✅ Embed value directly — no arguments[]
#                 sb.execute_script(
#                     f"document.getElementById('txtNumber').value = {js_str(phone_number)};"
#                 )
#                 sb.wait(1)

#                 sb.execute_script(
#                     "document.getElementById('btnSeeWhoOwnsIt').click();"
#                 )
#                 sb.wait(2)

#                 captcha_visible = sb.execute_script(
#                     "return document.querySelector('.mob_cap') !== null && "
#                     "document.querySelector('.mob_cap').offsetParent !== null;"
#                 )

#                 if captcha_visible:
#                     logger.info(f"[800FORALL] CAPTCHA detected on attempt {attempt}")

#                     captcha_b64 = sb.execute_script("""
#                         var canvas = document.createElement('canvas');
#                         var img = document.querySelector('img[id*="captcha"], img[src*="captcha"], img[src*="Captcha"]');
#                         if (!img) {
#                             var refresh = document.querySelector('.CaptchaRefresh, input[name="btnRefresh"]');
#                             if (refresh) {
#                                 var parent = refresh.closest('div');
#                                 if (parent) img = parent.querySelector('img');
#                             }
#                         }
#                         if (!img) return null;
#                         canvas.width = img.naturalWidth || img.width;
#                         canvas.height = img.naturalHeight || img.height;
#                         var ctx = canvas.getContext('2d');
#                         ctx.drawImage(img, 0, 0);
#                         return canvas.toDataURL('image/png').split(',')[1];
#                     """)

#                     if not captcha_b64:
#                         logger.warning("[800FORALL] Could not get captcha via canvas, using screenshot")
#                         sb.save_screenshot("/tmp/captcha_area.png")
#                         with open("/tmp/captcha_area.png", "rb") as f:
#                             captcha_b64 = base64.b64encode(f.read()).decode()

#                     img_data = base64.b64decode(captcha_b64)
#                     img = Image.open(io.BytesIO(img_data))
#                     img = img.convert("L")
#                     img = img.point(lambda x: 0 if x < 128 else 255, '1')

#                     captcha_text = pytesseract.image_to_string(
#                         img,
#                         config="--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
#                     ).strip()

#                     captcha_text = re.sub(r'[^A-Za-z0-9]', '', captcha_text)[:3]
#                     logger.info(f"[800FORALL] OCR captcha result: '{captcha_text}'")

#                     if not captcha_text:
#                         logger.warning(f"[800FORALL] OCR failed on attempt {attempt}, retrying...")
#                         continue

#                     # ✅ Embed captcha value directly — no arguments[]
#                     sb.execute_script(
#                         f"document.getElementById('txtCaptcha').value = {js_str(captcha_text)};"
#                     )
#                     sb.wait(0.5)

#                     sb.execute_script(
#                         "document.getElementById('btnSeeWhoOwnsIt').click();"
#                     )
#                     sb.wait(3)

#                 error_visible = sb.execute_script(
#                     "var el = document.querySelector('.WNTypetextsection p, .error, [class*=\"error\"]');"
#                     "return el ? el.innerText : null;"
#                 )
#                 if error_visible and ("unavailable" in error_visible.lower() or "try again" in error_visible.lower()):
#                     logger.warning(f"[800FORALL] Got error on attempt {attempt}: {error_visible}")
#                     continue

#                 result = sb.execute_script("""
#                     var selectors = [
#                         '.ThisNumber',
#                         '.WNxyztextfield',
#                         '#divWhoOwnsIt',
#                         '[class*="result"]',
#                         '[class*="owner"]',
#                         '[class*="company"]',
#                     ];
#                     for (var i = 0; i < selectors.length; i++) {
#                         var el = document.querySelector(selectors[i]);
#                         if (el && el.innerText && el.innerText.trim().length > 0) {
#                             return el.innerText.trim();
#                         }
#                     }
#                     var main = document.querySelector('main, #main, .main, aside, #content');
#                     return main ? main.innerText.trim() : '';
#                 """)

#                 if result and len(result) > 2:
#                     noise = ["search tips", "enter a number", "who owns", "by using this", "terms of use"]
#                     if not any(n in result.lower() for n in noise):
#                         logger.info(f"[800FORALL] Found owner: {result[:100]}")
#                         return result.strip()
#                     else:
#                         logger.warning(f"[800FORALL] Result was noise on attempt {attempt}")
#                         continue
#                 else:
#                     logger.warning(f"[800FORALL] No result on attempt {attempt}")
#                     continue

#         except Exception as e:
#             logger.error(f"[800FORALL] Exception on attempt {attempt}: {e}")
#             continue

#     logger.error(f"[800FORALL] All {max_retries} attempts failed for {phone_number}")
#     return ""


# logging.basicConfig(level=logging.INFO)
# result = scrape_800forall_cnam('8557141574')
# print('CNAM RESULT:', repr(result))    




# import os
# from twilio.rest import Client

# # Option 1: Hardcode for testing only (then remove)
# api_key_sid = "SK69e4ac4610171d67efa89cf4d586000d"

# api_key_secret = "OIXpjMJJAWqMIFAZW9o4XR6xAbJHcvSE"

# # Option 2: Load from environment (better)
# # api_key_sid = os.environ.get('TWILIO_API_KEY_SID')
# # api_key_secret = os.environ.get('TWILIO_API_KEY_SECRET')

# client = Client(api_key_sid, api_key_secret)

# # Try with a real, valid US mobile number first
# lookup = client.lookups.v2.phone_numbers("+15108675310").fetch(
#     fields="line_type_intelligence"
# )

# print(lookup.phone_number)
# print(lookup.line_type_intelligence)




from resporg import lookup_resporg

result = lookup_resporg("5108675310")
print(f"Carrier: {result.carrier_name}")
print(f"Line type: {result.line_type}")
print(f"MCC: {result.mcc}")
print(f"MNC: {result.mnc}")




