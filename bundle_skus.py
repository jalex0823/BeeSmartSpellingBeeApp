"""Bundle SKU mapping and entitlement builder.

Purpose:
- Provide stable, store-friendly product IDs (SKUs) for monetizing avatar bundles
- Keep mapping centralized so server-side IAP verification can unlock the right bundle

Conventions:
- Prefix comes from env BUNDLE_SKU_PREFIX (default: 'com.beesmart.bundle')
- SKU format: <prefix>.<bundle_id>
- bundle_id is normalized to lowercase and limited to [a-z0-9_]

Compatibility:
- Accept multiple SKU prefixes via BUNDLE_SKU_PREFIX_ALIASES
- Also accepts a common legacy prefix 'beesmart.bundle'

Exports:
- bundle_sku_for_id(bundle_id): product_id
- build_bundle_product_entitlements(bundle_catalog): { product_id: {type:'bundle', bundle_id, avatars[]} }
"""

from __future__ import annotations

import os
import re
from typing import Dict


def _sku_prefix() -> str:
    # Reverse-domain style is recommended for App Store / Play
    return os.getenv("BUNDLE_SKU_PREFIX", "com.beesmart.bundle")


def _sku_prefix_aliases() -> list[str]:
    """Return accepted SKU prefixes.

    Configure additional prefixes via:
      BUNDLE_SKU_PREFIX_ALIASES="prefix.one,prefix.two"
    """
    primary = (_sku_prefix() or "").strip()
    common = ["com.beesmart.bundle", "beesmart.bundle"]
    extra: list[str] = []
    raw = os.getenv("BUNDLE_SKU_PREFIX_ALIASES", "").strip()
    if raw:
        extra = [p.strip() for p in raw.split(",") if p.strip()]

    out: list[str] = []
    for p in [primary, *common, *extra]:
        if not p:
            continue
        if p not in out:
            out.append(p)
    return out


def _safe_bundle_id(bundle_id: str) -> str:
    """Normalize bundle id to store-safe token."""
    s = (bundle_id or "").strip().lower()
    # Convert non allowed chars to underscore
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    # Collapse repeats
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def bundle_sku_for_id(bundle_id: str, *, prefix: str | None = None) -> str:
    safe = _safe_bundle_id(bundle_id)
    pfx = (prefix or _sku_prefix()).strip().rstrip(".")
    return f"{pfx}.{safe}" if safe else pfx


def build_bundle_product_entitlements(bundle_catalog: dict) -> Dict[str, dict]:
    """Build product_id -> entitlement mapping for bundles."""
    entitlements: Dict[str, dict] = {}
    prefixes = _sku_prefix_aliases()

    for bundle_id, cfg in (bundle_catalog or {}).items():
        if not isinstance(bundle_id, str) or not bundle_id.strip():
            continue
        cfg = cfg or {}
        avatars = list(cfg.get("avatars", []) or [])
        for prefix in prefixes:
            pid = bundle_sku_for_id(bundle_id, prefix=prefix)
            entitlements[pid] = {"type": "bundle", "bundle_id": bundle_id, "avatars": avatars}

    return entitlements
