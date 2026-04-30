# import django
# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# django.setup()

# from reports.services.resporg import extract_phone_from_url
# result = extract_phone_from_url('https://learnbrainhub-b0h3ccg0bge0cbf3.z03.azurefd.net/winvrs.html')
# print('RESULT:', repr(result))

from seleniumbase import SB
import pytesseract
from PIL import Image
import io
import base64
import re
import logging

logger = logging.getLogger(__name__)

TOLL_FREE_PREFIXES = {"800", "833", "844", "855", "866", "877", "888"}


def clean_phone(raw: str):
    if not raw:
        return None
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) == 10 and digits[:3] in TOLL_FREE_PREFIXES:
        return digits
    return None


def scrape_800forall_cnam(phone_number: str, max_retries: int = 5) -> str:
    """
    Scrape 800forall.com to get CNAM/owner name for a toll-free number.
    Uses SeleniumBase + Tesseract OCR to solve the CAPTCHA.
    Returns the owner/company name or empty string.
    """
    for attempt in range(1, max_retries + 1):
        logger.info(f"[800FORALL] Attempt {attempt}/{max_retries} for {phone_number}")
        try:
            with SB(browser="chrome", headless=True, undetectable=True) as sb:

                sb.open("https://www.800forall.com/SearchWhoOwns.aspx")
                sb.wait_for_element_visible("input#txtNumber", timeout=15)
                sb.execute_script(
                    "document.getElementById('txtNumber').value = arguments[0];",
                    phone_number
                )
                sb.wait(1)

                # Click See Who Owns It to trigger captcha
                sb.execute_script(
                    "document.getElementById('btnSeeWhoOwnsIt').click();"
                )
                sb.wait(2)

                # Check if captcha appeared
                captcha_visible = sb.execute_script(
                    "return document.querySelector('.mob_cap') !== null && "
                    "document.querySelector('.mob_cap').offsetParent !== null;"
                )

                if captcha_visible:
                    logger.info(f"[800FORALL] CAPTCHA detected on attempt {attempt}")

                    # Get captcha image as base64
                    captcha_b64 = sb.execute_script("""
                        var canvas = document.createElement('canvas');
                        var img = document.querySelector('img[id*="captcha"], img[src*="captcha"], img[src*="Captcha"]');
                        if (!img) {
                            // Try finding by class or nearby element
                            var refresh = document.querySelector('.CaptchaRefresh, input[name="btnRefresh"]');
                            if (refresh) {
                                // Look for img sibling or parent img
                                var parent = refresh.closest('div');
                                if (parent) img = parent.querySelector('img');
                            }
                        }
                        if (!img) return null;
                        canvas.width = img.naturalWidth || img.width;
                        canvas.height = img.naturalHeight || img.height;
                        var ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        return canvas.toDataURL('image/png').split(',')[1];
                    """)

                    if not captcha_b64:
                        # Fallback: screenshot the captcha element area
                        logger.warning("[800FORALL] Could not get captcha via canvas, using screenshot")
                        sb.save_screenshot("/tmp/captcha_area.png")
                        with open("/tmp/captcha_area.png", "rb") as f:
                            captcha_b64 = base64.b64encode(f.read()).decode()

                    # OCR the captcha
                    img_data = base64.b64decode(captcha_b64)
                    img = Image.open(io.BytesIO(img_data))

                    # Preprocess for better OCR
                    img = img.convert("L")  # Grayscale
                    img = img.point(lambda x: 0 if x < 128 else 255, '1')  # Binarize

                    captcha_text = pytesseract.image_to_string(
                        img,
                        config="--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
                    ).strip()

                    # Clean to 3 chars max
                    captcha_text = re.sub(r'[^A-Za-z0-9]', '', captcha_text)[:3]
                    logger.info(f"[800FORALL] OCR captcha result: '{captcha_text}'")

                    if not captcha_text:
                        logger.warning(f"[800FORALL] OCR failed on attempt {attempt}, retrying...")
                        continue

                    # Fill captcha
                    sb.execute_script(
                        "document.getElementById('txtCaptcha').value = arguments[0];",
                        captcha_text
                    )
                    sb.wait(0.5)

                    # Submit
                    sb.execute_script(
                        "document.getElementById('btnSeeWhoOwnsIt').click();"
                    )
                    sb.wait(3)

                # Check for error popup
                error_visible = sb.execute_script(
                    "var el = document.querySelector('.WNTypetextsection p, .error, [class*=\"error\"]');"
                    "return el ? el.innerText : null;"
                )
                if error_visible and ("unavailable" in error_visible.lower() or "try again" in error_visible.lower()):
                    logger.warning(f"[800FORALL] Got error on attempt {attempt}: {error_visible}")
                    continue

                # Extract result — company name
                result = sb.execute_script("""
                    // Try multiple selectors
                    var selectors = [
                        '.ThisNumber',
                        '.WNxyztextfield',
                        '#divWhoOwnsIt',
                        '[class*="result"]',
                        '[class*="owner"]',
                        '[class*="company"]',
                    ];
                    for (var i = 0; i < selectors.length; i++) {
                        var el = document.querySelector(selectors[i]);
                        if (el && el.innerText && el.innerText.trim().length > 0) {
                            return el.innerText.trim();
                        }
                    }
                    // Fallback: get all text in main content
                    var main = document.querySelector('main, #main, .main, aside, #content');
                    return main ? main.innerText.trim() : '';
                """)

                if result and len(result) > 2:
                    # Filter out generic noise
                    noise = ["search tips", "enter a number", "who owns", "by using this", "terms of use"]
                    result_lower = result.lower()
                    if not any(n in result_lower for n in noise):
                        logger.info(f"[800FORALL] Found owner: {result[:100]}")
                        return result.strip()
                    else:
                        logger.warning(f"[800FORALL] Result was noise on attempt {attempt}")
                        continue
                else:
                    logger.warning(f"[800FORALL] No result on attempt {attempt}")
                    continue

        except Exception as e:
            logger.error(f"[800FORALL] Exception on attempt {attempt}: {e}")
            continue

    logger.error(f"[800FORALL] All {max_retries} attempts failed for {phone_number}")
    return ""