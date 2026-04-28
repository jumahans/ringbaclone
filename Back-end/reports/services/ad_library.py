import os
import requests
import logging

logger = logging.getLogger(__name__)

FACEBOOK_AD_LIBRARY_URL = "https://graph.facebook.com/v19.0/ads_archive"
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "1305244264947288|yIykXmD-oSmVntJwf7qnWtp1EnU")

FIELDS = ",".join([
    "id",
    "ad_creation_time",
    "ad_delivery_start_time",
    "ad_delivery_stop_time",
    "ad_snapshot_url",
    "ad_creative_bodies",
    "ad_creative_link_titles",
    "ad_creative_link_descriptions",
    "currency",
    "estimated_audience_size",
    "impressions",
    "page_id",
    "page_name",
    "publisher_platforms",
    "spend",
    "languages",
])


def _format_ad(ad: dict) -> dict:
    return {
        "ad_id":         ad.get("id", ""),
        "page_name":     ad.get("page_name", ""),
        "page_id":       ad.get("page_id", ""),
        "status":        "Active" if not ad.get("ad_delivery_stop_time") else "Inactive",
        "started":       ad.get("ad_delivery_start_time", ""),
        "stopped":       ad.get("ad_delivery_stop_time", ""),
        "created":       ad.get("ad_creation_time", ""),
        "platforms":     ad.get("publisher_platforms", []),
        "spend":         ad.get("spend", {}).get("spend_range", "") if isinstance(ad.get("spend"), dict) else "",
        "impressions":   ad.get("impressions", {}).get("lower_bound", "") if isinstance(ad.get("impressions"), dict) else "",
        "snapshot_url":  ad.get("ad_snapshot_url", ""),
        "ad_text":       (ad.get("ad_creative_bodies") or [""])[0],
        "ad_title":      (ad.get("ad_creative_link_titles") or [""])[0],
        "languages":     ad.get("languages", []),
        "audience_size": ad.get("estimated_audience_size", {}).get("lower_bound", "") if isinstance(ad.get("estimated_audience_size"), dict) else "",
    }


def _search_by_domain(domain: str) -> list:
    """Search all ads linked to a domain."""
    try:
        params = {
            "access_token": FACEBOOK_ACCESS_TOKEN,
            "ad_type": "ALL",
            "ad_reached_countries": ["US"],
            "search_terms": domain,
            "fields": FIELDS,
            "limit": 10,
        }
        response = requests.get(FACEBOOK_AD_LIBRARY_URL, params=params, timeout=15)
        data = response.json()

        if "error" in data:
            logger.error(f"[FB ADS] Domain search error: {data['error']}")
            return []

        ads = data.get("data", [])
        logger.info(f"[FB ADS] Domain search found {len(ads)} ads for: {domain}")
        return [_format_ad(ad) for ad in ads]

    except Exception as e:
        logger.error(f"[FB ADS] Domain search failed: {e}")
        return []


def _search_by_ad_id(ad_id: str) -> list:
    """Search for a specific ad by its ID."""
    try:
        url = f"https://graph.facebook.com/v19.0/{ad_id}"
        params = {
            "access_token": FACEBOOK_ACCESS_TOKEN,
            "fields": FIELDS,
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if "error" in data:
            logger.error(f"[FB ADS] Ad ID search error: {data['error']}")
            return []

        if "id" in data:
            logger.info(f"[FB ADS] Ad ID search found ad: {ad_id}")
            return [_format_ad(data)]

        return []

    except Exception as e:
        logger.error(f"[FB ADS] Ad ID search failed: {e}")
        return []


def search_facebook_ads(domain: str, campaign_id: str = "") -> dict:
    """
    Search Facebook Ad Library.
    If campaign_id exists — search by ad ID first.
    Always search by domain.
    Combine and deduplicate results.
    """
    all_ads = []
    seen_ids = set()

    # Search by ad ID if campaign ID provided
    if campaign_id:
        logger.info(f"[FB ADS] Searching by ad ID: {campaign_id}")
        id_results = _search_by_ad_id(campaign_id)
        for ad in id_results:
            if ad["ad_id"] not in seen_ids:
                seen_ids.add(ad["ad_id"])
                all_ads.append(ad)

    # Clean domain
    clean_domain = domain.replace("https://", "").replace("http://", "").split("/")[0].split("?")[0]

    # Search by domain
    if clean_domain:
        logger.info(f"[FB ADS] Searching by domain: {clean_domain}")
        domain_results = _search_by_domain(clean_domain)
        for ad in domain_results:
            if ad["ad_id"] not in seen_ids:
                seen_ids.add(ad["ad_id"])
                all_ads.append(ad)

    logger.info(f"[FB ADS] Total unique ads found: {len(all_ads)}")

    return {
        "found": len(all_ads) > 0,
        "ads": all_ads,
        "total": len(all_ads),
        "error": "",
    }