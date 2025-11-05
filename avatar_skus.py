"""
Avatar SKU mapping and generator

Purpose:
- Provide stable, store-friendly product IDs (SKUs) for monetizing individual avatars
- Keep a central mapping so server-side IAP verification can unlock the right avatar
- Future-proof: if an avatar isn't in the DB yet, we still generate a deterministic SKU

Conventions:
- Prefix comes from env AVATAR_SKU_PREFIX (default: 'beesmart.avatar')
- SKU format: <prefix>.<slug>
- Slug generation: CamelCase → kebab-case, trim punctuation, lowercased

Exports:
- AVATAR_SKUS: { avatar_slug: product_id }
- build_product_entitlements(): { product_id: { 'type': 'avatar', 'avatar_id': avatar_slug } }
"""

from __future__ import annotations

import os
import re
from typing import Dict, Iterable


def _slugify_avatar_name(name: str) -> str:
    """Convert a display name like 'QueenBee' or 'Space Bee' to a slug 'queen-bee'.
    Rules:
      - Strip extension and trailing punctuation (e.g., '!') if present
      - Convert CamelCase boundaries into dashes
      - Replace non-alphanumeric with dashes, collapse repeats
      - Lowercase
    """
    if not name:
        return ""

    # Drop extension if present
    base = re.sub(r"\.[A-Za-z0-9]+$", "", name)
    # Remove trailing punctuation like '!'
    base = base.rstrip('!')
    # Trim whitespace
    base = base.strip()
    # Convert CamelCase boundaries into dash
    base = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", base)
    # Replace non-alphanumeric with dash
    base = re.sub(r"[^A-Za-z0-9]+", "-", base)
    # Collapse multiple dashes
    base = re.sub(r"-+", "-", base)
    # Lowercase and trim dashes
    slug = base.strip('-').lower()
    return slug


def _sku_prefix() -> str:
    # Use reverse-domain style by default for App Store/Play best practices
    return os.getenv('AVATAR_SKU_PREFIX', 'com.beesmart.avatar')


def sku_for_slug(avatar_slug: str) -> str:
    """Build SKU for a given avatar slug"""
    prefix = _sku_prefix()
    # Ensure slug is safe
    safe = re.sub(r"[^a-z0-9-]", "-", (avatar_slug or '').lower())
    safe = re.sub(r"-+", "-", safe).strip('-')
    return f"{prefix}.{safe}"


def build_skus_from_names(names: Iterable[str]) -> Dict[str, str]:
    """Generate {slug: sku} mapping from a list of display names or filenames.
    This is tolerant of names like 'QueenBee!.png' or 'CoolBee'.
    """
    mapping: Dict[str, str] = {}
    for name in names:
        slug = _slugify_avatar_name(name)
        if not slug:
            continue
        mapping[slug] = sku_for_slug(slug)
    return mapping


def build_skus_from_catalog() -> Dict[str, str]:
    """If avatar_catalog is available, build SKUs for all purchasable avatars."""
    try:
        from avatar_catalog import AVATAR_CATALOG  # type: ignore
    except Exception:
        return {}

    mapping: Dict[str, str] = {}
    for a in AVATAR_CATALOG:
        slug = (a.get('id') or '').strip()
        if not slug:
            continue
        # Only create SKUs for purchasable avatars
        if not a.get('is_purchasable', True):
            continue
        mapping[slug] = sku_for_slug(slug)
    return mapping


def build_product_entitlements(extra_names: Iterable[str] | None = None) -> Dict[str, dict]:
    """Return product_id -> entitlement mapping for avatars.
    Order of sources:
      1) Catalog (ids)
      2) Extra display names (e.g., PNG filenames) provided by caller
    Later sources win for the same slug (identical outcome since SKU is deterministic).
    """
    catalog = build_skus_from_catalog()
    extras = build_skus_from_names(extra_names or [])
    merged: Dict[str, str] = {**catalog, **extras}

    # Optional alias mapping from PNG-derived slugs → canonical catalog ids
    # Helps when file naming differs (e.g., SpaceBee → astro-bee)
    ALIASES: Dict[str, str] = {
        'space-bee': 'astro-bee',
        'doc-bee': 'doctor-bee',
        'motor-bee': 'biker-bee',
        'bee-knight': 'knight-bee',
        'j-rock-bee': 'rocker-bee',
    }

    # Discover available catalog ids (if avatar_catalog import succeeded)
    try:
        from avatar_catalog import AVATAR_CATALOG  # type: ignore
        catalog_ids = { (a.get('id') or '').strip() for a in AVATAR_CATALOG }
    except Exception:
        catalog_ids = set()

    entitlements: Dict[str, dict] = {}
    for slug, pid in merged.items():
        target_slug = slug
        if catalog_ids and slug not in catalog_ids:
            alias = ALIASES.get(slug)
            if alias and alias in catalog_ids:
                target_slug = alias
        entitlements[pid] = { 'type': 'avatar', 'avatar_id': target_slug }
    return entitlements


# Seed with the provided filenames to guarantee coverage today
_PNG_NAMES = [
    'AlBee!.png', 'BeeKnight!.png', 'BrotherBee!.png', 'BudaBee!.png', 'BuilderBee!.png',
    'BuzzBee!.png', 'CoolBee!.png', 'CutieBee!.png', 'DetectiveBee!.png', 'DivaBee!.png',
    'DocBee!.png', 'ExplorerBee!.png', 'FrankenBee!.png', 'HoneyComb!.png', 'JRockBee!.png',
    'MascotBee!.png', 'MotorBee!.png', 'OBee!.png', 'ProfessorBee!.png', 'QueenBee!.png',
    'RoboBee!.png', 'RockerBee!.png', 'SeaBee!.png', 'SelfieBee!.png', 'SingerBee!.png',
    'SpaceBee!.png', 'SuperBee!.png', 'VampBee!.png', 'WareBee!.png', 'ZomBee!.png'
]

# Public: avatars → product IDs
AVATAR_SKUS: Dict[str, str] = {
    **build_skus_from_catalog(),
    **build_skus_from_names(_PNG_NAMES),
}
