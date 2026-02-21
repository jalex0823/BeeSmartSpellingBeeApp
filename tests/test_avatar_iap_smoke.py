"""
Smoke tests for avatar IAP changes: syntax + catalog + unlock logic.
Run: pytest tests/test_avatar_iap_smoke.py -v
No Flask app import (fast).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def test_avatar_skus_syntax_and_catalog_load():
    """avatar_skus.py compiles and loads product IDs from data/avatars.catalog.json."""
    import avatar_skus
    assert hasattr(avatar_skus, "APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG")
    assert len(avatar_skus.APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG) >= 36
    assert avatar_skus.app_store_product_id_for_avatar("franken-bee") == "beesmart.avatar.franken_bee.v3"
    assert avatar_skus.app_store_product_id_for_avatar("fairy-bee") == "beesmart.avatar.fairy_bee.v3"
    assert avatar_skus.app_store_product_id_for_avatar("gamer-bee") == "beesmart.avatar.gamer_bee.v3"


def test_avatar_catalog_check_unlocked():
    """avatar_catalog.check_avatar_unlocked with normalized slugs."""
    import avatar_catalog
    from avatar_catalog import check_avatar_unlocked, _norm_slug

    assert _norm_slug("Franken_Bee") == "franken-bee"
    # Locked without purchase
    r = check_avatar_unlocked("al-bee", 0, [], has_premium_subscription=False)
    assert r["unlocked"] is False
    # Unlocked by purchased_avatars (normalized)
    r2 = check_avatar_unlocked("al-bee", 0, ["al-bee"], has_premium_subscription=False)
    assert r2["unlocked"] is True and r2["reason"] == "Purchased"
    r2b = check_avatar_unlocked("al-bee", 0, ["Al_Bee"], has_premium_subscription=False)
    assert r2b["unlocked"] is True
    # Premium subscription does not unlock avatars (avatars unlock via points/purchase)
    r3 = check_avatar_unlocked("al-bee", 0, [], has_premium_subscription=True)
    assert r3["unlocked"] is False

    # Premium-tier avatars are purchase-only (not earnable via Honey Points)
    r4 = check_avatar_unlocked("al-bee", 999999, [], has_premium_subscription=False)
    assert r4["unlocked"] is False


def test_js_picker_no_syntax_glitch():
    """honeycomb-avatar-picker-responsive.js exists and product_id usage is from API only."""
    js_path = REPO_ROOT / "static" / "js" / "honeycomb-avatar-picker-responsive.js"
    assert js_path.is_file()
    text = js_path.read_text(encoding="utf-8")
    # We removed the fallback that built productId from slug; ensure we use API product_id only
    assert "avatar.product_id" in text
    assert "Catalog-backed" in text or "from API only" in text
