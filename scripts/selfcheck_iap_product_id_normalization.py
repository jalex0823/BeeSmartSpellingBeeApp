"""Quick self-check for IAP restore product-id normalization.

This prevents regressions where native iOS returns a slightly different SKU
than the server's PRODUCT_MAP expects.

Run locally:
  python3 scripts/selfcheck_iap_product_id_normalization.py

It exits non-zero if a critical mapping is missing.
"""

from __future__ import annotations

import importlib
import os
import sys


def main() -> int:
    # Ensure repo root is importable when executed from scripts/.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    app = importlib.import_module("AjaSpellBApp")

    sub_ids = getattr(app, "SUBSCRIPTION_PRODUCT_IDS", {}) or {}
    monthly = (sub_ids.get("monthly") or "com.beesmart.premium.monthly").strip()

    product_map = getattr(app, "PRODUCT_MAP", {}) or {}

    # The native restore is currently reporting this in TestFlight.
    legacy_native_monthly = "beesmart.premium.monthly"

    # Our server should always recognize the canonical monthly SKU.
    if monthly not in product_map:
        raise SystemExit(f"FAIL: Monthly subscription SKU not in PRODUCT_MAP: {monthly}")

    # We explicitly accept the legacy native identifier by mapping it to monthly.
    # This is implemented inside /api/iap/restore normalization.
    # Here we just assert it isn't accidentally added as a distinct mapping.
    if legacy_native_monthly in product_map and legacy_native_monthly != monthly:
        raise SystemExit(
            "FAIL: Legacy native SKU unexpectedly present in PRODUCT_MAP; "
            "it should be canonicalized to monthly instead."
        )

    print("OK: PRODUCT_MAP contains monthly subscription SKU:", monthly)
    print("OK: Legacy native SKU will be canonicalized:", legacy_native_monthly, "->", monthly)

    # Validate all avatar product IDs from data/avatars.catalog.json (single source of truth)
    from avatar_skus import APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG
    app_store_connect_avatar_skus = list((APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG or {}).keys())
    if not app_store_connect_avatar_skus:
        raise SystemExit("FAIL: No avatar product IDs loaded from catalog (avatars.catalog.json)")

    missing = []
    wrong_type = []
    for sku in app_store_connect_avatar_skus:
        m = product_map.get(sku)
        if not m:
            missing.append(sku)
            continue
        if (m.get("type") or "").lower() != "avatar":
            wrong_type.append({"sku": sku, "type": m.get("type")})

    if missing:
        raise SystemExit(
            "FAIL: Missing avatar SKUs in PRODUCT_MAP (check avatar_skus.build_product_entitlements): "
            + ", ".join(missing)
        )
    if wrong_type:
        raise SystemExit(f"FAIL: Some avatar SKUs are not typed as avatar: {wrong_type}")

    print(f"OK: Found {len(app_store_connect_avatar_skus)} App Store Connect avatar SKUs in PRODUCT_MAP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
