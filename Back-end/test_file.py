import re
import logging
import base64
import io
from seleniumbase import SB
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

def scrape_800forall_cnam(phone_number: str, max_retries: int = 5) -> str:
    """Scrape 800forall using YOUR original selectors"""
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"[800FORALL] Attempt {attempt}/{max_retries} for {phone_number}")
        
        with SB(browser="chrome", headless=True, undetectable=True) as sb:
            try:
                sb.open("https://www.800forall.com/SearchWhoOwns.aspx")
                sb.wait_for_element_visible("input#txtNumber", timeout=15)
                
                # YOUR way of entering phone number
                sb.execute_script(
                    f"document.getElementById('txtNumber').value = '{phone_number}';"
                )
                sb.wait(1)
                
                sb.execute_script(
                    "document.getElementById('btnSeeWhoOwnsIt').click();"
                )
                sb.wait(2)
                
                # YOUR captcha detection
                captcha_visible = sb.execute_script(
                    "return document.querySelector('.mob_cap') !== null && "
                    "document.querySelector('.mob_cap').offsetParent !== null;"
                )
                
                if captcha_visible:
                    logger.info(f"[800FORALL] CAPTCHA detected on attempt {attempt}")
                    
                    # YOUR method to get captcha
                    captcha_b64 = sb.execute_script("""
                        var canvas = document.createElement('canvas');
                        var img = document.querySelector('img[id*="captcha"], img[src*="captcha"], img[src*="Captcha"]');
                        if (!img) {
                            var refresh = document.querySelector('.CaptchaRefresh, input[name="btnRefresh"]');
                            if (refresh) {
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
                    
                    if captcha_b64:
                        img_data = base64.b64decode(captcha_b64)
                        img = Image.open(io.BytesIO(img_data))
                        img = img.convert("L")
                        img = img.point(lambda x: 0 if x < 128 else 255, '1')
                        
                        captcha_text = pytesseract.image_to_string(
                            img,
                            config="--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
                        ).strip()
                        
                        captcha_text = re.sub(r'[^A-Za-z0-9]', '', captcha_text)[:3]
                        logger.info(f"[800FORALL] OCR captcha result: '{captcha_text}'")
                        
                        if captcha_text:
                            sb.execute_script(
                                f"document.getElementById('txtCaptcha').value = '{captcha_text}';"
                            )
                            sb.wait(0.5)
                            
                            sb.execute_script(
                                "document.getElementById('btnSeeWhoOwnsIt').click();"
                            )
                            sb.wait(3)
                    else:
                        logger.warning(f"[800FORALL] Could not get captcha")
                        continue
                
                # YOUR selectors to get the result
                result = sb.execute_script("""
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
                    var main = document.querySelector('main, #main, .main, aside, #content');
                    return main ? main.innerText.trim() : '';
                """)
                
                if result and len(result) > 2:
                    noise = ["search tips", "enter a number", "who owns", "by using this", "terms of use"]
                    if not any(n in result.lower() for n in noise):
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


if __name__ == "__main__":
    result = scrape_800forall_cnam('8775131557')
    print(f'CNAM RESULT: {repr(result)}')