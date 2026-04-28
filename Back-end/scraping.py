# # from seleniumbase import SB
# # import random
# # import time


# # # ── Fingerprint profiles (rotate randomly) ───────────────────────────────────
# # FINGERPRINTS = [
# #     {
# #         "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #         "platform": "Win32", "vendor": "Google Inc.", "cores": 8, "memory": 8,
# #         "screen_w": 1920, "screen_h": 1080, "avail_h": 1040,
# #         "timezone": "America/Chicago", "lang": "en-US",
# #     },
# #     {
# #         "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
# #         "platform": "Win32", "vendor": "Google Inc.", "cores": 4, "memory": 4,
# #         "screen_w": 1366, "screen_h": 768, "avail_h": 728,
# #         "timezone": "America/New_York", "lang": "en-US",
# #     },
# #     {
# #         "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #         "platform": "MacIntel", "vendor": "Apple Computer, Inc.", "cores": 10, "memory": 16,
# #         "screen_w": 1440, "screen_h": 900, "avail_h": 860,
# #         "timezone": "America/Los_Angeles", "lang": "en-US",
# #     },
# # ]

# # FP = random.choice(FINGERPRINTS)
# # print(f"[fingerprint] Using agent: {FP['agent'][:60]}...")


# # def human_delay(min_ms=300, max_ms=900):
# #     """Randomised pause with micro-jitter."""
# #     base = random.uniform(min_ms, max_ms) / 1000
# #     jitter = random.uniform(0, 0.05)
# #     time.sleep(base + jitter)


# # def inject_fingerprint(sb):
# #     """Overwrite JS properties that bot-detection scripts probe."""
# #     sb.execute_script(f"""
# #         function tryDefine(obj, prop, value) {{
# #             try {{
# #                 const desc = Object.getOwnPropertyDescriptor(obj, prop);
# #                 if (!desc || desc.configurable) {{
# #                     Object.defineProperty(obj, prop, {{
# #                         get: () => value,
# #                         configurable: true
# #                     }});
# #                 }}
# #             }} catch(e) {{}}
# #         }}

# #         tryDefine(navigator, 'platform',  '{FP["platform"]}');
# #         tryDefine(navigator, 'vendor',    '{FP["vendor"]}');
# #         tryDefine(navigator, 'languages', ['{FP["lang"]}', 'en']);
# #         tryDefine(navigator, 'hardwareConcurrency', {FP["cores"]});
# #         tryDefine(navigator, 'deviceMemory',        {FP["memory"]});
# #         tryDefine(screen,    'width',       {FP["screen_w"]});
# #         tryDefine(screen,    'height',      {FP["screen_h"]});
# #         tryDefine(screen,    'availWidth',  {FP["screen_w"]});
# #         tryDefine(screen,    'availHeight', {FP["avail_h"]});
# #         tryDefine(screen,    'colorDepth',  24);
# #         tryDefine(navigator, 'webdriver',   undefined);

# #         tryDefine(navigator, 'plugins', (() => {{
# #             const arr = [
# #                 {{name:'Chrome PDF Plugin',   filename:'internal-pdf-viewer'}},
# #                 {{name:'Chrome PDF Viewer',   filename:'mhjfbmdgcfjbbpaeojofohoefgiehjai'}},
# #                 {{name:'Native Client',       filename:'internal-nacl-plugin'}},
# #             ];
# #             try {{ arr.__proto__ = PluginArray.prototype; }} catch(e) {{}}
# #             return arr;
# #         }})());

# #         if (!window.chrome) {{
# #             window.chrome = {{
# #                 runtime: {{connect:()=>{{}}, sendMessage:()=>{{}}}},
# #                 loadTimes: () => ({{firstPaintTime: {random.uniform(0.3, 0.9):.3f}}}),
# #                 csi: () => ({{pageT: {random.uniform(500, 900):.1f}}}),
# #             }};
# #         }}

# #         tryDefine(navigator, 'connection', {{
# #             effectiveType: '4g',
# #             rtt: {random.choice([20, 30, 50, 60])},
# #             downlink: {random.choice([5, 8, 10, 15])}
# #         }});
# #     """)

# # def simulate_human_mouse(sb):
# #     for _ in range(random.randint(2, 4)):
# #         x = random.randint(200, 900)
# #         y = random.randint(100, 500)
# #         sb.execute_script(f"""
# #             (() => {{
# #                 window.dispatchEvent(new MouseEvent('mousemove', {{
# #                     clientX:{x}, clientY:{y}, bubbles:true
# #                 }}));
# #             }})()
# #         """)
# #         time.sleep(random.uniform(0.1, 0.3))

# # def random_scroll(sb):
# #     amount = random.randint(80, 250)
# #     sb.execute_script(f"window.scrollBy(0, {amount})")
# #     time.sleep(random.uniform(0.3, 0.7))
# #     sb.execute_script(f"window.scrollBy(0, -{amount // 2})")
# #     human_delay(200, 500)


# # def force_select_radio(sb, selector):
# #     sb.execute_script(f"""
# #         (() => {{
# #             const el = document.querySelector('{selector}');
# #             if (el) {{
# #                 el.focus();
# #                 el.click();
# #                 el.checked = true;
# #                 ['click','input','change'].forEach(evt =>
# #                     el.dispatchEvent(new Event(evt, {{bubbles:true}}))
# #                 );
# #             }}
# #         }})()
# #     """)
# #     human_delay(400, 800)

# # def human_type(sb, selector, text):
# #     sb.execute_script(f"""
# #         (() => {{
# #             const el = document.querySelector('{selector}');
# #             if (el) el.focus();
# #         }})()
# #     """)
# #     human_delay(200, 400)
# #     sb.execute_script(f"""
# #         (() => {{
# #             const el = document.querySelector('{selector}');
# #             if (el) {{ el.value = ''; el.dispatchEvent(new Event('input', {{bubbles:true}})); }}
# #         }})()
# #     """)
# #     for char in text:
# #         escaped = char.replace("'", "\\'")
# #         sb.execute_script(f"""
# #             (() => {{
# #                 const el = document.querySelector('{selector}');
# #                 if (el) {{
# #                     el.value += '{escaped}';
# #                     el.dispatchEvent(new Event('input', {{bubbles:true}}));
# #                 }}
# #             }})()
# #         """)
# #         time.sleep(random.uniform(0.045, 0.13))
# #     sb.execute_script(f"""
# #         (() => {{
# #             const el = document.querySelector('{selector}');
# #             if (el) el.dispatchEvent(new Event('change', {{bubbles:true}}));
# #         }})()
# #     """)
# #     human_delay(300, 600)

# # def set_select(sb, sel_id, value):
# #     sb.execute_script(f"""
# #         (() => {{
# #             const sel = document.querySelector("select[id='{sel_id}']");
# #             if (sel) {{
# #                 sel.value = '{value}';
# #                 sel.dispatchEvent(new Event('change', {{bubbles:true}}));
# #             }}
# #         }})()
# #     """)
# #     human_delay(300, 700)

# # def wait_and_click_continue(sb):
# #     sb.wait_for_element_visible("button", timeout=20)
# #     for _ in range(40):
# #         disabled = sb.execute_script("""
# #             (() => {
# #                 const btn = [...document.querySelectorAll('button')]
# #                     .find(b => b.textContent.trim() === 'Continue');
# #                 return btn ? btn.disabled : true;
# #             })()
# #         """)
# #         if not disabled:
# #             break
# #         time.sleep(0.5)
# #     simulate_human_mouse(sb)
# #     human_delay(600, 1200)
# #     sb.execute_script("""
# #         (() => {
# #             const btn = [...document.querySelectorAll('button')]
# #                 .find(b => b.textContent.trim() === 'Continue');
# #             if (btn) btn.click();
# #         })()
# #     """)
# #     human_delay(2000, 3500)

# # def wait_for_url_fragment(sb, fragment, timeout=15):
# #     """Poll until the current URL contains fragment."""
# #     for _ in range(timeout * 2):
# #         if fragment in sb.get_current_url():
# #             return
# #         time.sleep(0.5)
# #     print(f"[warn] URL fragment '{fragment}' not seen after {timeout}s")


# # # ── Main ──────────────────────────────────────────────────────────────────────
# # with SB(
# #     browser="chrome",
# #     headless=False,
# #     agent=FP["agent"],
# #     undetectable=True,
# #     slow=True,
# # ) as sb:

# #     sb.open("https://reportfraud.ftc.gov/")
# #     inject_fingerprint(sb)
# #     human_delay(2000, 3500)
# #     random_scroll(sb)
# #     simulate_human_mouse(sb)
# #     print("Loaded:", sb.get_current_url())

# #     # ── Step 1: Report Now ────────────────────────────────────────────────────
# #     sb.wait_for_element_visible("button", timeout=15)
# #     sb.execute_script("""
# #         (() => {
# #             const btn = [...document.querySelectorAll('button')]
# #                 .find(b => b.textContent.includes('Report Now'));
# #             if (btn) btn.click();
# #         })()
# #     """)
# #     wait_for_url_fragment(sb, "/assistant")
# #     inject_fingerprint(sb)
# #     human_delay(1500, 2500)
# #     print("After Report Now:", sb.get_current_url())

# #     # ── Step 2: Category ──────────────────────────────────────────────────────
# #     sb.wait_for_element_present("#cat-radio-1", timeout=15)
# #     human_delay(800, 1500)
# #     random_scroll(sb)
# #     force_select_radio(sb, "#cat-radio-1")
# #     print("cat-radio-1 checked:", sb.execute_script("return document.querySelector('#cat-radio-1').checked"))

# #     human_delay(1000, 2000)
# #     wait_and_click_continue(sb)
# #     inject_fingerprint(sb)
# #     print("After category Continue:", sb.get_current_url())

# #     # ── Step 3: Subcategory ───────────────────────────────────────────────────
# #     sb.wait_for_element_present("#subcat-radio-2", timeout=15)
# #     human_delay(800, 1500)
# #     force_select_radio(sb, "#subcat-radio-2")
# #     print("subcat-radio-2 checked:", sb.execute_script("return document.querySelector('#subcat-radio-2').checked"))

# #     human_delay(1000, 2000)
# #     wait_and_click_continue(sb)
# #     inject_fingerprint(sb)
# #     print("After subcategory Continue:", sb.get_current_url())

# #     # ── Step 4: Money lost? ───────────────────────────────────────────────────
# #     sb.wait_for_element_present("#yes-or-no-money-no", timeout=15)
# #     human_delay(600, 1200)
# #     force_select_radio(sb, "#yes-or-no-money-no")

# #     # ── Step 5: Scammer info ──────────────────────────────────────────────────
# #     human_delay(500, 1000)
# #     set_select(sb, "rdcontact", "3: 128")

# #     human_type(sb, "#rcname", "they are pretending to be amazon")
# #     human_type(sb, "#rccompanyFirstName", "John")
# #     human_type(sb, "#rccompanyLastName", "Doe")

# #     force_select_radio(sb, "#yes-or-no-contact-no")
# #     human_delay(500, 1000)

# #     description = (
# #         "They are impersonating Amazon. "
# #         "The scam phone number is 8885550100 and the landing page is http://amazon.com"
# #     )
# #     # Escape for safe JS string embedding
# #     escaped_description = description.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    
# #     sb.execute_script(f"""
# #         (() => {{
# #             const ta = document.querySelector('textarea');
# #             if (ta) {{
# #                 ta.value = '{escaped_description}';
# #                 ta.dispatchEvent(new Event('input',  {{bubbles:true}}));
# #                 ta.dispatchEvent(new Event('change', {{bubbles:true}}));
# #             }}
# #         }})()
# #     """)
# #     human_delay(500, 1000)
# #     print("Textarea:", sb.execute_script("""
# #         (() => {{
# #             const ta = document.querySelector('textarea');
# #             return ta ? ta.value : 'not found';
# #         }})()
# #     """))

# #     simulate_human_mouse(sb)
# #     human_delay(1000, 2000)
# #     wait_and_click_continue(sb)
# #     inject_fingerprint(sb)
# #     print("After scammer info Continue:", sb.get_current_url())

# #     # ── Step 6: Reporter info ─────────────────────────────────────────────────
# #     sb.wait_for_element_present("#yes-or-no-report-other-yes", timeout=15)
# #     human_delay(600, 1200)
# #     force_select_radio(sb, "#yes-or-no-report-other-yes")

# #     human_delay(500, 1000)
# #     human_type(sb, "#rayfirstName", "John")
# #     human_type(sb, "#raylastName", "Doe")

# #     set_select(sb, "raycountry", "1: USA")
# #     human_delay(800, 1500)

# #     address_fields = {
# #         "#reportAboutYourAddress": "724 Evergreen Terrace",
# #         "#rayaddresstwo":          "Apt 1",
# #         "#raycity":                "Springfield",
# #         "#rayotherState":          "Illinois",
# #         "#USZipCode":              "62701",
# #     }
# #     for selector, value in address_fields.items():
# #         random_scroll(sb)
# #         human_type(sb, selector, value)

# #     human_type(sb, "#rayphone", "2175550123")
# #     human_type(sb, "#rayemail", "john.doe@example.com")

# #     set_select(sb, "rayphoneType", "2: 0")
# #     set_select(sb, "rayAgeRange",  "4: 3")

# #     force_select_radio(sb, "#yes-or-no-small-business-no")
# #     human_delay(1000, 2000)
# #     simulate_human_mouse(sb)

# #     # ── Step 7: Submit ────────────────────────────────────────────────────────
# #     sb.execute_script("""
# #         (() => {
# #             const btn = [...document.querySelectorAll('button')]
# #                 .find(b => b.textContent.trim() === 'Submit');
# #             if (btn) btn.click();
# #         })()
# #     """)
# #     human_delay(5000, 7000)

# #     print("Final URL:", sb.get_current_url())
# #     print("Title:",     sb.get_title())



# from seleniumbase import SB
# import random
# import time


# # ── Fingerprint profiles (rotate randomly) ───────────────────────────────────
# FINGERPRINTS = [
#     {
#         "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#         "platform": "Win32", "vendor": "Google Inc.", "cores": 8, "memory": 8,
#         "screen_w": 1920, "screen_h": 1080, "avail_h": 1040,
#         "timezone": "America/Chicago", "lang": "en-US",
#     },
#     {
#         "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
#         "platform": "Win32", "vendor": "Google Inc.", "cores": 4, "memory": 4,
#         "screen_w": 1366, "screen_h": 768, "avail_h": 728,
#         "timezone": "America/New_York", "lang": "en-US",
#     },
#     {
#         "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#         "platform": "MacIntel", "vendor": "Apple Computer, Inc.", "cores": 10, "memory": 16,
#         "screen_w": 1440, "screen_h": 900, "avail_h": 860,
#         "timezone": "America/Los_Angeles", "lang": "en-US",
#     },
# ]

# FP = random.choice(FINGERPRINTS)
# print(f"[fingerprint] Using agent: {FP['agent'][:60]}...")


# # ── Helpers ───────────────────────────────────────────────────────────────────

# def human_delay(min_ms=300, max_ms=900):
#     base = random.uniform(min_ms, max_ms) / 1000
#     jitter = random.uniform(0, 0.05)
#     time.sleep(base + jitter)


# def inject_fingerprint(sb):
#     # Always use sb.driver.execute_script — plain Selenium, survives page navigations
#     sb.driver.execute_script(f"""
#         (function() {{
#             function tryDefine(obj, prop, value) {{
#                 try {{
#                     var desc = Object.getOwnPropertyDescriptor(obj, prop);
#                     if (!desc || desc.configurable) {{
#                         Object.defineProperty(obj, prop, {{
#                             get: function() {{ return value; }},
#                             configurable: true
#                         }});
#                     }}
#                 }} catch(e) {{}}
#             }}
#             tryDefine(navigator, 'platform',  '{FP["platform"]}');
#             tryDefine(navigator, 'vendor',    '{FP["vendor"]}');
#             tryDefine(navigator, 'languages', ['{FP["lang"]}', 'en']);
#             tryDefine(navigator, 'hardwareConcurrency', {FP["cores"]});
#             tryDefine(navigator, 'deviceMemory',        {FP["memory"]});
#             tryDefine(screen,    'width',       {FP["screen_w"]});
#             tryDefine(screen,    'height',      {FP["screen_h"]});
#             tryDefine(screen,    'availWidth',  {FP["screen_w"]});
#             tryDefine(screen,    'availHeight', {FP["avail_h"]});
#             tryDefine(screen,    'colorDepth',  24);
#             tryDefine(navigator, 'webdriver',   undefined);
#         }})();
#     """)


# def simulate_human_mouse(sb):
#     for _ in range(random.randint(2, 4)):
#         x = random.randint(200, 900)
#         y = random.randint(100, 500)
#         sb.driver.execute_script(f"""
#             window.dispatchEvent(new MouseEvent('mousemove', {{
#                 clientX: {x}, clientY: {y}, bubbles: true
#             }}));
#         """)
#         time.sleep(random.uniform(0.1, 0.3))


# def random_scroll(sb):
#     amount = random.randint(80, 250)
#     sb.driver.execute_script(f"window.scrollBy(0, {amount});")
#     time.sleep(random.uniform(0.3, 0.7))
#     sb.driver.execute_script(f"window.scrollBy(0, -{amount // 2});")
#     human_delay(200, 500)


# def js_click(sb, element_id):
#     sb.driver.execute_script(f"""
#         (function() {{
#             var el = document.getElementById('{element_id}');
#             if (el) {{
#                 el.focus();
#                 el.click();
#                 ['mousedown', 'mouseup', 'click'].forEach(function(evt) {{
#                     el.dispatchEvent(new MouseEvent(evt, {{bubbles: true}}));
#                 }});
#             }}
#         }})();
#     """)
#     human_delay(400, 800)


# def js_click_selector(sb, selector):
#     safe = selector.replace("'", "\\'")
#     sb.driver.execute_script(f"""
#         (function() {{
#             var el = document.querySelector('{safe}');
#             if (el) {{
#                 el.focus();
#                 el.click();
#                 ['mousedown', 'mouseup', 'click'].forEach(function(evt) {{
#                     el.dispatchEvent(new MouseEvent(evt, {{bubbles: true}}));
#                 }});
#             }}
#         }})();
#     """)
#     human_delay(400, 800)


# def human_type(sb, selector, text):
#     safe_selector = selector.replace("'", "\\'")
#     # Clear field first
#     sb.driver.execute_script(f"""
#         (function() {{
#             var el = document.querySelector('{safe_selector}');
#             if (el) {{
#                 el.focus();
#                 el.value = '';
#                 el.dispatchEvent(new Event('input', {{bubbles: true}}));
#             }}
#         }})();
#     """)
#     human_delay(200, 400)
#     # Type character by character
#     for char in text:
#         escaped = char.replace("\\", "\\\\").replace("'", "\\'")
#         sb.driver.execute_script(f"""
#             (function() {{
#                 var el = document.querySelector('{safe_selector}');
#                 if (el) {{
#                     el.value += '{escaped}';
#                     el.dispatchEvent(new Event('input', {{bubbles: true}}));
#                 }}
#             }})();
#         """)
#         time.sleep(random.uniform(0.045, 0.13))
#     # Fire change event
#     sb.driver.execute_script(f"""
#         (function() {{
#             var el = document.querySelector('{safe_selector}');
#             if (el) el.dispatchEvent(new Event('change', {{bubbles: true}}));
#         }})();
#     """)
#     human_delay(300, 600)


# def set_select(sb, sel_id, value):
#     safe_value = value.replace("'", "\\'")
#     sb.driver.execute_script(f"""
#         (function() {{
#             var sel = document.getElementById('{sel_id}');
#             if (sel) {{
#                 sel.value = '{safe_value}';
#                 sel.dispatchEvent(new Event('change', {{bubbles: true}}));
#             }}
#         }})();
#     """)
#     human_delay(300, 700)


# def safe_set(sb, element_id, value):
#     safe_value = value.replace("\\", "\\\\").replace("'", "\\'")
#     result = sb.driver.execute_script(f"""
#         return (function() {{
#             var el = document.getElementById('{element_id}');
#             if (el) {{
#                 el.value = '{safe_value}';
#                 el.dispatchEvent(new Event('input',  {{bubbles: true}}));
#                 el.dispatchEvent(new Event('change', {{bubbles: true}}));
#                 return true;
#             }}
#             return false;
#         }})();
#     """)
#     if result:
#         print(f"  Set {element_id} = {value}")
#     else:
#         print(f"  SKIPPED (not found): {element_id}")
#     human_delay(300, 600)


# def click_next(sb):
#     simulate_human_mouse(sb)
#     human_delay(600, 1000)
#     sb.driver.execute_script("""
#         (function() {
#             var btn = document.querySelector('button.usa-button.next');
#             if (btn) {
#                 btn.focus();
#                 btn.click();
#                 ['mousedown', 'mouseup', 'click'].forEach(function(evt) {
#                     btn.dispatchEvent(new MouseEvent(evt, {bubbles: true}));
#                 });
#             }
#         })();
#     """)
#     human_delay(2500, 4000)


# def wait_for_page_load(sb, timeout=30):
#     for _ in range(timeout * 2):
#         try:
#             state = sb.driver.execute_script("return document.readyState;")
#             if state == "complete":
#                 return
#         except Exception:
#             pass
#         time.sleep(0.5)
#     print("[warn] Page load timeout")


# # ════════════════════════════════════════════════════════════════════════════
# # IC3 — plain SB, no undetectable mode
# # IC3 is a US government form with no meaningful bot detection.
# # Plain mode keeps a stable WebDriver session that follows POST navigations.
# # undetectable=True / uc_subprocess=True both break on form submit (POST nav).
# # ════════════════════════════════════════════════════════════════════════════
# with SB(
#     browser="chrome",
#     headless=False,
#     agent=FP["agent"],
#     slow=True,
# ) as sb:

#     sb.open("https://www.ic3.gov/")
#     inject_fingerprint(sb)
#     human_delay(2000, 3500)
#     random_scroll(sb)
#     simulate_human_mouse(sb)
#     print("Loaded:", sb.get_current_url())

#     # ── Click "File a Complaint" ──────────────────────────────────────────────
#     sb.wait_for_element_visible("button#fileComplaint", timeout=15)
#     human_delay(800, 1500)
#     sb.driver.find_element("css selector", "button#fileComplaint").click()
#     human_delay(2000, 3500)
#     print("After File a Complaint:", sb.get_current_url())

#     # ── Click "Accept" — opens new tab ────────────────────────────────────────
#     sb.wait_for_element_visible("button#acceptFile", timeout=15)
#     human_delay(800, 1500)
#     sb.driver.find_element("css selector", "button#acceptFile").click()
#     human_delay(3000, 5000)

#     # Switch to new tab
#     sb.switch_to_newest_window()
#     inject_fingerprint(sb)
#     human_delay(2000, 3500)
#     print("After Accept - New tab URL:", sb.get_current_url())
#     all_inputs = sb.driver.execute_script(
#     "return Array.from(document.querySelectorAll('input, select, textarea')).map(function(el) { return el.id + ' | ' + el.name + ' | ' + el.type; });"
#     )
#     for inp in all_inputs:
#         print(inp)

#     # ── Step 1: Complainant info ──────────────────────────────────────────────
#     sb.wait_for_element_present("input#IsVictim_no", timeout=20)
#     human_delay(600, 1200)
#     random_scroll(sb)

#     js_click(sb, "IsVictim_no")
#     human_delay(500, 1000)

#     human_type(sb, "input[type=text][id='Complainant_Name']",   "John Doe")
#     human_type(sb, "input[type=tel][id='Complainant_Phone']",   "2175550123")
#     human_type(sb, "input[type=email][id='Complainant_Email']", "john@gmail.com")

#     simulate_human_mouse(sb)
#     click_next(sb)
#     print("After Step 1:", sb.get_current_url())

#     # ── Step 2: Victim info ───────────────────────────────────────────────────
#     sb.wait_for_element_present("input#Victim_Name", timeout=20)
#     human_delay(800, 1500)
#     random_scroll(sb)

#     human_type(sb, "input[type=text][id='Victim_Name']",    "John Doe")
#     set_select(sb, "Victim_AgeRange", "TwentyTo29")
#     human_type(sb, "input[type=text][id='Victim_Address1']","724 Evergreen Terrace")
#     human_type(sb, "input[type=text][id='Victim_City']",    "Springfield")
#     set_select(sb, "Victim_Country", "USA")
#     human_delay(1000, 1500)
#     set_select(sb, "Victim_State", "AL")
#     human_type(sb, "input[type=text][id='Victim_ZipCode']", "62701")
#     human_type(sb, "input[type=tel][id='Victim_Phone']",    "2175550123")
#     human_type(sb, "input[type=email][id='Victim_Email']",  "john@gmail.com")

#     js_click(sb, "Victim_IsBusiness_no")
#     human_delay(500, 1000)

#     simulate_human_mouse(sb)
#     click_next(sb)
#     print("After Step 2:", sb.get_current_url())

#     # ── Step 3: Money sent ────────────────────────────────────────────────────
#     sb.wait_for_element_present("input#MoneySent_no", timeout=20)
#     human_delay(600, 1200)

#     js_click(sb, "MoneySent_no")
#     human_delay(500, 1000)

#     simulate_human_mouse(sb)
#     click_next(sb)
#     print("After Step 3:", sb.get_current_url())

#     # ── Step 4: Subject info ──────────────────────────────────────────────────
#     sb.wait_for_element_present("input#Subjects_0__Name", timeout=20)
#     human_delay(800, 1500)

#     # Try expanding subject accordion if present
#     try:
#         js_click_selector(sb, "button.add-subject")
#         human_delay(1000, 1500)
#     except Exception:
#         pass

#     sb.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     human_delay(1000, 1500)

#     safe_set(sb, "Subjects_0__Name",         "Website phishing Scam")
#     safe_set(sb, "Subjects_0__BusinessName", "Amazon")
#     safe_set(sb, "Subjects_0__Address",      "724 Evergreen Terrace")
#     safe_set(sb, "Subjects_0__City",         "Springfield")
#     set_select(sb, "Subjects_0_Country",     "USA")
#     human_delay(500, 1000)
#     safe_set(sb, "Subjects_0__ZipCode",      "62701")
#     safe_set(sb, "Subjects_0__Phone",        "2175550123")
#     safe_set(sb, "Subjects_0__Email",        "john@gmail.com")
#     safe_set(sb, "Subjects_0__Website",      "https://www.amazon.com")
#     safe_set(sb, "Subjects_0__IPAddress",    "192.168.1.1")

#     simulate_human_mouse(sb)
#     click_next(sb)
#     print("After Step 4:", sb.get_current_url())

#     # ── Step 5: Incident description ──────────────────────────────────────────
#     sb.wait_for_element_present("textarea#IncidentDescription", timeout=20)
#     human_delay(800, 1500)
#     random_scroll(sb)

#     incident_text = "Phone number 2175550123 impersonating Amazon. Landing page: https://www.amazon.com."
#     safe_incident = incident_text.replace("\\", "\\\\").replace("'", "\\'")
#     sb.driver.execute_script(f"""
#         (function() {{
#             var ta = document.getElementById('IncidentDescription');
#             if (ta) {{
#                 ta.focus();
#                 ta.value = '{safe_incident}';
#                 ta.dispatchEvent(new Event('input',  {{bubbles: true}}));
#                 ta.dispatchEvent(new Event('change', {{bubbles: true}}));
#                 ta.blur();
#             }}
#         }})();
#     """)
#     human_delay(500, 1000)

#     simulate_human_mouse(sb)
#     click_next(sb)
#     print("After Step 5:", sb.get_current_url())

#     # ── Step 6: Complaint update ──────────────────────────────────────────────
#     sb.wait_for_element_present("input#ComplaintUpdate_no", timeout=20)
#     human_delay(600, 1200)

#     js_click(sb, "ComplaintUpdate_no")
#     human_delay(500, 1000)

#     simulate_human_mouse(sb)
#     click_next(sb)
#     print("After Step 6:", sb.get_current_url())

#     # ── Step 7: Digital signature and submit ──────────────────────────────────
#     sb.wait_for_element_present("input#DigitalSignature", timeout=20)
#     human_delay(1000, 2000)
#     random_scroll(sb)

#     human_type(sb, "input[id='DigitalSignature']", "John Doe")
#     human_delay(2000, 3500)

#     simulate_human_mouse(sb)
#     random_scroll(sb)
#     inject_fingerprint(sb)
#     human_delay(3000, 5000)

#     print("Submitting form...")
#     submit_btn = sb.driver.find_element("css selector", "button[type='submit']")
#     sb.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
#     human_delay(800, 1200)
#     submit_btn.click()

#     # Poll rapidly right after click to catch the confirmation page
#     # before IC3 redirects to /Search/Results
#     print("Waiting for server response...")
#     confirmation_html = None
#     confirmation_url  = None

#     for _ in range(60):  # up to 30 seconds
#         time.sleep(0.5)
#         try:
#             current_url = sb.driver.execute_script("return window.location.href;")
#             page_html   = sb.driver.execute_script("return document.documentElement.innerHTML;")

#             # Catch the confirmation page the moment it appears
#             if any(kw in page_html.lower() for kw in [
#                 "complaint number", "confirmation", "thank you",
#                 "successfully submitted", "reference number", "ic3 complaint"
#             ]):
#                 confirmation_html = page_html
#                 confirmation_url  = current_url
#                 print(f"[+] Confirmation page captured at: {current_url}")
#                 break

#             # Still on complaint form — keep waiting
#             if "complaint.ic3.gov" in current_url and "Search" not in current_url:
#                 continue

#             # Navigated away — grab whatever is here
#             if current_url != "https://complaint.ic3.gov/":
#                 confirmation_html = page_html
#                 confirmation_url  = current_url
#                 break

#         except Exception:
#             pass

#     human_delay(1000, 2000)
#     final_url   = sb.get_current_url()
#     final_title = sb.get_title()
#     print("Final URL:",  final_url)
#     print("Title:",      final_title)

#     if confirmation_html:
#         # Extract confirmation/complaint number from captured HTML
#         import re
#         number_match = re.search(
#             r'(complaint\s*(?:number|#|id)[:\s#]*)([\w\-]+)',
#             confirmation_html, re.IGNORECASE
#         )
#         ref_match = re.search(
#             r'(reference\s*(?:number|#|id)[:\s#]*)([\w\-]+)',
#             confirmation_html, re.IGNORECASE
#         )
#         if number_match:
#             print(f"RESULT: SUCCESS — Complaint number: {number_match.group(2)}")
#         elif ref_match:
#             print(f"RESULT: SUCCESS — Reference number: {ref_match.group(2)}")
#         else:
#             print("RESULT: SUCCESS — Confirmation page was captured.")
#     elif "Search/Results" in final_url:
#         # IC3 redirected to search results — this means the POST went through
#         # but we missed the confirmation page. The complaint was still filed.
#         print("RESULT: SUBMITTED — IC3 redirected to search page.")
#         print("        The complaint was filed but confirmation page was not captured.")
#         print("        Check your email for a confirmation from IC3.")
#     elif "chrome-error" in final_url:
#         print("RESULT: ERROR — Navigation failed, check network connection.")
#     elif "complaint.ic3.gov" in final_url:
#         error_msg = sb.driver.execute_script("""
#             return (function() {
#                 var err = document.querySelector(
#                     '.usa-alert--error, .validation-summary-errors, .field-validation-error'
#                 );
#                 return err ? err.textContent.trim() : null;
#             })();
#         """)
#         if error_msg:
#             print("RESULT: FORM ERROR —", error_msg)
#         else:
#             print("RESULT: Still on form page — unknown state.")








# # from playwright.sync_api import sync_playwright

# # with sync_playwright() as p:
# #     browser = p.chromium.launch(headless=False, slow_mo=50)
# #     context = browser.new_context(
# #         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #         viewport={"width": 1366, "height": 768},
# #         locale="en-US",
# #     )
# #     page = context.new_page()
# #     page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
# #     page.goto("https://www.ic3.gov/", timeout=60000)
# #     page.wait_for_timeout(2000)
# #     page.click("button[id=fileComplaint]")
# #     page.wait_for_timeout(2000)

# #     with context.expect_page() as new_page:
# #         page.click("button[id=acceptFile]")

# #     page = new_page.value
# #     page.wait_for_load_state("domcontentloaded")
# #     page.wait_for_timeout(3000)

# #     # Step 1 — Complainant info
# #     page.evaluate("document.getElementById('IsVictim_no').click()")
# #     page.wait_for_timeout(500)
# #     page.fill("input[type=text][id=Complainant_Name]", "John Doe")
# #     page.fill("input[type=tel][id=Complainant_Phone]", "2175550123")
# #     page.fill("input[type=email][id=Complainant_Email]", "john@gmail.com")
# #     page.evaluate("document.querySelector('button.usa-button.next').click()")
# #     page.wait_for_timeout(3000)

# #     # Step 2 — Victim info
# #     page.fill("input[type=text][id=Victim_Name]", "John Doe")
# #     page.select_option("select[id=Victim_AgeRange]", value="TwentyTo29")
# #     page.fill("input[type=text][id=Victim_Address1]", "724 Evergreen Terrace")
# #     page.fill("input[type=text][id=Victim_City]", "Springfield")
# #     page.select_option("select[id=Victim_Country]", value="USA")
# #     page.wait_for_timeout(1000)
# #     page.select_option("select[id=Victim_State]", value="AL")
# #     page.fill("input[type=text][id=Victim_ZipCode]", "62701")
# #     page.fill("input[type=tel][id=Victim_Phone]", "2175550123")
# #     page.fill("input[type=email][id=Victim_Email]", "john@gmail.com")
# #     page.evaluate("document.getElementById('Victim_IsBusiness_no').click()")
# #     page.wait_for_timeout(500)
# #     page.evaluate("document.querySelector('button.usa-button.next').click()")
# #     page.wait_for_timeout(3000)

# #     # Step 3 — Money sent
# #     page.evaluate("document.getElementById('MoneySent_no').click()")
# #     page.wait_for_timeout(500)
# #     page.evaluate("document.querySelector('button.usa-button.next').click()")
# #     page.wait_for_timeout(3000)

# #     # Step 4 — Subject info (FIXED: click to expand section first)
# #     # Try clicking "Add Subject" button or the subject section header to expand it
# #     try:
# #         page.click("button:has-text('Add Subject')", timeout=5000)
# #         page.wait_for_timeout(1000)
# #     except:
# #         pass
    
# #     # Try clicking the subject section header/accordion
# #     try:
# #         page.click("text=Subject Information", timeout=5000)
# #         page.wait_for_timeout(1000)
# #     except:
# #         pass
    
# #     # Scroll down to make sure subject fields are visible
# #     page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
# #     page.wait_for_timeout(1000)
    
# #     # Now fill the fields using evaluate to bypass visibility check
# #     page.evaluate("document.getElementById('Subjects_0__Name').value = 'Website phishing Scam'")
# #     page.evaluate("document.getElementById('Subjects_0__BusinessName').value = 'Amazon'")
# #     page.evaluate("document.getElementById('Subjects_0__Address').value = '724 Evergreen Terrace'")
# #     page.evaluate("document.getElementById('Subjects_0__City').value = 'Springfield'")
# #     page.select_option("select[id=Subjects_0_Country]", value="USA")
# #     page.evaluate("document.getElementById('Subjects_0__ZipCode').value = '62701'")
# #     page.evaluate("document.getElementById('Subject_0__Phone').value = '2175550123'")
# #     page.evaluate("document.getElementById('Subjects_0__Email').value = 'john@gmail.com'")
# #     page.evaluate("document.getElementById('Subjects_0__Website').value = 'https://www.amazon.com'")
# #     page.evaluate("document.getElementById('Subjects_0__IpAddress').value = '192.168.1.1'")
# #     page.evaluate("document.querySelector('button.usa-button.next').click()")
# #     page.wait_for_timeout(3000)

# #     # Step 5 — Incident description
# #     page.fill("textarea[id=IncidentDescription]", "Phone number 2175550123 impersonating Amazon. Landing page: https://www.amazon.com.")
# #     page.evaluate("document.querySelector('button.usa-button.next').click()")
# #     page.wait_for_timeout(3000)

# #     # Step 6 — Complaint update
# #     page.evaluate("document.getElementById('ComplaintUpdate_no').click()")
# #     page.wait_for_timeout(500)
# #     page.evaluate("document.querySelector('button.usa-button.next').click()")
# #     page.wait_for_timeout(3000)

# #     # Step 7 — Digital signature and submit
# #     page.fill("input[id=DigitalSignature]", "John Doe")
# #     page.wait_for_timeout(1000)
# #     page.evaluate("document.querySelector('button[type=submit]').click()")
# #     page.wait_for_timeout(5000)

# #     print(page.url)
# #     print(page.title())

# #     browser.close()





# from playwright.sync_api import sync_playwright

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False, slow_mo=50)
#     page = browser.new_page()
#     page.goto("https://edulogicpoint-g9hzcwcyewfrc0d8.z03.azurefd.net/Ma0cHelpAsMEr0t0140/index.html")
#     page.wait_for_timeout(3000)
    
#     # Click Accept button
#     page.click("button:has-text('Accept')")
#     page.wait_for_timeout(3000)
    
#     # Now get the body
#     body = page.inner_text("body")
#     print(body)
    
#     # Also print full HTML to see what loaded
#     html = page.content()
#     print(html)
    
#     browser.close()


from playwright.sync_api import sync_playwright 

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://msrc.microsoft.com/report/")
    page.locator('a[href*="IncidentType=Malware"][href*="ThreatType=URL"]').click()
    page.fill("input[type=text][id=TextField278]", "hansjuma")
    page.fill("input[type=email][id=TextField283]", "haansjuma@gmail.com")
    page.fill("input[type=text][id=TextField288]", "hansorganization")
    page.fill("input[type=tel][id=TextField293]", "0700392123")
    page.fill("textarea[id=TextAreaField298]", "This is a test report of a malicious URL impersonating Microsoft. The URL is http://malicious-example.com and it is sending phishing emails to users.")
    from datetime import date

    page.locator('i[data-icon-name="Calendar"]').click()
    page.locator(f'button[class*="ms-DatePicker-day"]:has-text("{date.today().day}")').click()
    page.fill("input[type=time][id=TextField68]", f"{date.now().strftime('%I:%M %p')}")


    # with context.expect_page() as new_page:
    #     page.locator('a[href*="IncidentType=Malware"]').click()
    

    browser.close()