import os
import re
import json
import logging
import subprocess
import tempfile

logger = logging.getLogger(__name__)

TIMEOUT_PLAYWRIGHT = 60

def search_google_ads(domain: str) -> dict:
    """
    Search Google Ads Transparency Center for ads running on a given domain.
    Uses SeleniumBase to scrape the public transparency center.
    """

    empty = {
        "found": False,
        "ads": [],
        "total": 0,
        "error": "",
    }

    # Clean domain
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0].split("?")[0]

    if not domain:
        empty["error"] = "No domain provided"
        return empty

    try:
        from seleniumbase import SB
        import re

        url = f"https://adstransparency.google.com/?query={domain}&region=anywhere"
        ads = []

        with SB(browser="chrome", headless=True, undetectable=True) as sb:
            sb.open(url)
            sb.sleep(5)

            # Wait for results
            try:
                sb.wait_for_element_present("creative-preview", timeout=10)
            except:
                pass

            sb.sleep(2)

            # Try to extract ad cards
            ads_raw = sb.execute_script("""
                () => {
                    const results = [];
                    const cards = document.querySelectorAll(
                        'creative-preview, .creative-card, [data-creative-id], .ad-card'
                    );

                    cards.forEach((card, i) => {
                        if (i >= 10) return;

                        const getText = (sel) => {
                            const el = card.querySelector(sel);
                            return el ? el.textContent.trim() : '';
                        };

                        results.push({
                            advertiser: getText('.advertiser-name, [class*="advertiser"]') || 'Unknown',
                            ad_text: getText('.ad-text, .creative-text, [class*="body"]') || '',
                            ad_title: getText('.ad-title, .headline, [class*="title"]') || '',
                            first_shown: getText('[class*="date"]') || '',
                            format: getText('[class*="format"]') || '',
                            region: 'US',
                            creative_id: card.getAttribute('data-creative-id') || '',
                            link: `https://adstransparency.google.com/?query=${domain}`,
                        });
                    });

                    return results;
                }
            """)

            if ads_raw:
                ads = ads_raw
            else:
                # Fallback — search page source for advertiser data
                html = sb.get_page_source()

                advertiser_matches = re.findall(r'"advertiserName"\s*:\s*"([^"]+)"', html)
                creative_matches = re.findall(r'"creativeId"\s*:\s*"([^"]+)"', html)

                if advertiser_matches:
                    for i, name in enumerate(advertiser_matches[:10]):
                        ads.append({
                            "advertiser": name,
                            "ad_text": "",
                            "ad_title": "",
                            "first_shown": "",
                            "format": "",
                            "region": "US",
                            "creative_id": creative_matches[i] if i < len(creative_matches) else "",
                            "link": f"https://adstransparency.google.com/?query={domain}",
                        })

        if ads:
            logger.info(f"[GOOGLE ADS] Found {len(ads)} ads for: {domain}")
            return {
                "found": True,
                "ads": ads,
                "total": len(ads),
                "error": "",
            }

        logger.info(f"[GOOGLE ADS] No ads found for: {domain}")
        return empty

    except Exception as e:
        logger.error(f"[GOOGLE ADS] Failed: {e}")
        empty["error"] = str(e)
        return empty