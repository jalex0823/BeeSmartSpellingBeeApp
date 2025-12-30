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
    # App Store Connect Product ID format (current):
    #   beesmart.avatar.<underscore_slug>.v2
    #
    # We keep the prefix as 'beesmart.avatar' and add the '.v2' suffix when
    # generating the SKU.
    return os.getenv('AVATAR_SKU_PREFIX', 'beesmart.avatar')


def _sku_prefix_aliases() -> list[str]:
    """Return a list of accepted SKU prefixes.

    Why:
      - Historical docs and older builds used different prefixes (e.g. 'beesmart.avatar')
      - App/Store IDs are sticky once created in the stores
      - Server should be liberal in what it accepts while mapping to canonical avatar ids

    Configure additional accepted prefixes via:
      AVATAR_SKU_PREFIX_ALIASES="prefix.one,prefix.two"
    """
    primary = (_sku_prefix() or '').strip()
    # Accept historical prefixes for restore/back-compat.
    # NOTE: Generation is controlled by _sku_prefix() + sku_for_slug().
    common = ['beesmart.avatar', 'com.beesmart.avatar', 'com.beesmart.iap.avatar.v2']
    extra = []
    raw = os.getenv('AVATAR_SKU_PREFIX_ALIASES', '')
    if raw:
        extra = [p.strip() for p in raw.split(',') if p.strip()]
    # Stable de-dupe while preserving order
    out: list[str] = []
    for p in [primary, *common, *extra]:
        if not p:
            continue
        if p not in out:
            out.append(p)
    return out


def _slug_variants_for_store(slug: str) -> list[str]:
    """Generate store-facing slug variants for a canonical avatar id.

    Stores or historical docs have used:
      - hyphens:  queen-bee
      - underscores: queen_bee
      - compact: queenbee (rare but exists in docs for Super Bee → superbee)
      - special cases: sea-bee appears as 'seabea' in some legacy materials
    """
    if not slug:
        return []
    base = slug.strip().lower()
    variants = {base}
    if '-' in base:
        variants.add(base.replace('-', '_'))
        variants.add(base.replace('-', ''))
    if '_' in base:
        variants.add(base.replace('_', '-'))
        variants.add(base.replace('_', ''))
    # Known legacy oddity: 'sea-bee' sometimes documented as 'seabea'
    if base == 'sea-bee':
        variants.add('seabea')
    return sorted(variants)


def sku_for_slug(avatar_slug: str) -> str:
    """Build SKU for a given avatar slug"""
    prefix = _sku_prefix()
    # Ensure slug is safe - use underscores to match App Store Connect format
    # App Store Connect Product IDs use: beesmart.avatar.brother_bee (not brother-bee)
    safe = re.sub(r"[^a-z0-9_]", "_", (avatar_slug or '').lower())
    safe = re.sub(r"_+", "_", safe).strip('_')
    # New App Store Connect IDs append .v2
    if prefix == 'beesmart.avatar':
        return f"{prefix}.{safe}.v2"
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
        # Catalog product_id is legacy (pre-v2). SKU generation is canonical.
        # Be explicit about the two newest/pain-point avatars so they're always
        # included even if catalog shape changes.
        if slug in {'fairy-bee', 'gamer-bee'}:
            mapping[slug] = sku_for_slug(slug)
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

    prefixes = _sku_prefix_aliases()
    for slug, _pid in merged.items():
        target_slug = slug
        if catalog_ids and slug not in catalog_ids:
            alias = ALIASES.get(slug)
            if alias and alias in catalog_ids:
                target_slug = alias

        # Accept multiple SKU spellings/prefixes for the same canonical avatar id.
        # For the current App Store Connect scheme, the canonical product id is:
        #   beesmart.avatar.<store_slug>.v2
        for prefix in prefixes:
            for store_slug in _slug_variants_for_store(target_slug):
                if prefix == 'beesmart.avatar':
                    entitlements[f"{prefix}.{store_slug}.v2"] = { 'type': 'avatar', 'avatar_id': target_slug }
                    # Also accept pre-v2 ids for restores/upgrades from old builds.
                    entitlements[f"{prefix}.{store_slug}"] = { 'type': 'avatar', 'avatar_id': target_slug }
                else:
                    entitlements[f"{prefix}.{store_slug}"] = { 'type': 'avatar', 'avatar_id': target_slug }

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
