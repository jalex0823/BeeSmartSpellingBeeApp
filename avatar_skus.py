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

import json
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
    # Remove '!' anywhere. Many source render files end with '!' (e.g. AlBee!.png)
    # and some shells treat '!' specially (history expansion).
    base = base.replace('!', '')
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
    # Always include underscore and compact variants; some store ids were created
    # with underscores even when our canonical ids use kebab-case.
    variants.add(base.replace('-', '_'))
    variants.add(base.replace('_', '-'))
    variants.add(base.replace('-', '').replace('_', ''))
    # Known legacy oddity: 'sea-bee' sometimes documented as 'seabea'
    if base == 'sea-bee':
        variants.add('seabea')
    return sorted(variants)


def sku_for_slug(avatar_slug: str) -> str:
    """Build SKU for a given avatar slug"""
    prefix = _sku_prefix()
    # Ensure slug is safe - treat input as canonical kebab-case id, then convert
    # to underscores to match App Store Connect format.
    # App Store Connect Product IDs use: beesmart.avatar.brother_bee (not brother-bee)
    canonical = (avatar_slug or '').strip().lower().replace('_', '-')
    canonical = re.sub(r"[^a-z0-9-]+", "-", canonical)
    canonical = re.sub(r"-+", "-", canonical).strip('-')
    safe = canonical.replace('-', '_')
    # App Store Connect IDs append .v3 (v2 kept for legacy restore)
    if prefix == 'beesmart.avatar':
        return f"{prefix}.{safe}.v3"
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
    # Always seed from our known render-name list to guarantee coverage even when
    # avatar_catalog import isn't available (or is configured off).
    seeded = build_skus_from_names(_PNG_NAMES)
    extras = build_skus_from_names(extra_names or [])
    merged: Dict[str, str] = {**catalog, **seeded, **extras}

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
    # IMPORTANT: Iterate over canonical avatar ids (dict keys), not SKU values.
    # We generate multiple acceptable product id spellings per avatar below.
    for slug in merged.keys():
        target_slug = slug
        if catalog_ids and slug not in catalog_ids:
            alias = ALIASES.get(slug)
            if alias and alias in catalog_ids:
                target_slug = alias

        # Accept multiple SKU spellings/prefixes for the same canonical avatar id.
        # Canonical product id: beesmart.avatar.<store_slug>.v3
        for prefix in prefixes:
            for store_slug in _slug_variants_for_store(target_slug):
                if prefix == 'beesmart.avatar':
                    entitlements[f"{prefix}.{store_slug}.v3"] = { 'type': 'avatar', 'avatar_id': target_slug }
                    entitlements[f"{prefix}.{store_slug}.v2"] = { 'type': 'avatar', 'avatar_id': target_slug }  # legacy
                    entitlements[f"{prefix}.{store_slug}"] = { 'type': 'avatar', 'avatar_id': target_slug }
                else:
                    entitlements[f"{prefix}.{store_slug}"] = { 'type': 'avatar', 'avatar_id': target_slug }

    return entitlements


# Seed with the provided filenames to guarantee coverage today
_PNG_NAMES = [
    'AlBee.png', 'BeeKnight.png', 'BrotherBee.png', 'BudaBee.png', 'BuilderBee.png',
    'BuzzBee.png', 'CoolBee.png', 'CutieBee.png', 'DetectiveBee.png', 'DivaBee.png',
    'DocBee.png', 'ExplorerBee.png', 'FrankenBee.png', 'HoneyComb.png', 'JRockBee.png',
    # These two are in App Store Connect as legacy non-v2 IDs.
    'FairyBee.png', 'GamerBee.png',
    'MascotBee.png', 'MotorBee.png', 'OBee.png', 'ProfessorBee.png', 'QueenBee.png',
    'RoboBee.png', 'RockerBee.png', 'SeaBee.png', 'SelfieBee.png', 'SingerBee.png',
    'SpaceBee.png', 'SuperBee.png', 'VampBee.png', 'WareBee.png', 'ZomBee.png'
]

def build_product_entitlements_from_catalog() -> Dict[str, dict]:
    """Return product_id -> entitlement for every avatar in data/avatars.catalog.json.
    Use this as the canonical source for PRODUCT_MAP so purchase verification matches
    store product IDs exactly. Also registers Purchase option ID (hyphens format) so
    backend can verify when Google returns that.
    """
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, 'data', 'avatars.catalog.json')
        if not os.path.isfile(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return {}
    avatars = data.get('avatars') if isinstance(data, dict) else []
    out: Dict[str, dict] = {}
    for a in avatars if isinstance(avatars, list) else []:
        pid = (a.get('iapProductId') or '').strip()
        key = (a.get('avatarKey') or '').strip().lower().replace('_', '-')
        if pid and key:
            out[pid] = {'type': 'avatar', 'avatar_id': key}
            # Purchase option ID (step 2) uses hyphens only; register for verification
            po_id = _ios_to_google_play_purchase_option_id(pid)
            if po_id and po_id != pid:
                out[po_id] = {'type': 'avatar', 'avatar_id': key}
    return out


# Single source of truth: data/avatars.catalog.json (avatarKey, iapProductId).
# Load from file so UI and backend use exact Apple-approved product IDs; fallback to built-in if missing.
def _load_app_store_ids_from_catalog() -> Dict[str, str]:
    """Build product_id -> avatar_key from data/avatars.catalog.json. No hardcoded IDs in UI."""
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, 'data', 'avatars.catalog.json')
        if not os.path.isfile(path):
            return _APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG_FALLBACK
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        avatars = data.get('avatars') if isinstance(data, dict) else []
        out: Dict[str, str] = {}
        for a in avatars if isinstance(avatars, list) else []:
            pid = (a.get('iapProductId') or '').strip()
            key = (a.get('avatarKey') or '').strip().lower().replace('_', '-')
            if pid and key:
                out[pid] = key
        return out if out else _APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG_FALLBACK
    except Exception:
        return _APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG_FALLBACK


# Fallback when data/avatars.catalog.json is missing (e.g. tests).
_APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG_FALLBACK: Dict[str, str] = {
    'beesmart.avatar.firefighter_bee.v3': 'firefighter-bee',
    'beesmart.avatar.bk_bee.v3': 'bk-bee',
    'beesmart.avatar.franken_bee.v3': 'franken-bee',
    'beesmart.avatar.yeti_bee.v3': 'yeti-bee',
    'beesmart.avatar.al_bee.v3': 'al-bee',
    'beesmart.avatar.knight_bee.v3': 'knight-bee',
    'beesmart.avatar.inventor_bee.v3': 'inventor-bee',
    'beesmart.avatar.vamp_bee.v3': 'vamp-bee',
    'beesmart.avatar.doc_bee.v3': 'doc-bee',
    'beesmart.avatar.o_bee.v3': 'o-bee',
    'beesmart.avatar.xray_bee.v3': 'xray-bee',
    'beesmart.avatar.fairy_bee.v3': 'fairy-bee',
    'beesmart.avatar.buda_bee.v3': 'buda-bee',
    'beesmart.avatar.j_rock_bee.v3': 'j-rock-bee',
    'beesmart.avatar.super_bee.v3': 'super-bee',
    'beesmart.avatar.nurse_bee.v3': 'nurse-bee',
    'beesmart.avatar.motor_bee.v3': 'motor-bee',
    'beesmart.avatar.honey_comb.v3': 'honey-comb',
    'beesmart.avatar.gamer_bee.v3': 'gamer-bee',
    'beesmart.avatar.selfie_bee.v3': 'selfie-bee',
    'beesmart.avatar.umpire_bee.v3': 'umpire-bee',
    'beesmart.avatar.lumberjack_bee.v3': 'lumberjack-bee',
    'beesmart.avatar.cutie_bee.v3': 'cutie-bee',
    'beesmart.avatar.singer_bee.v3': 'singer-bee',
    'beesmart.avatar.sea_bee.v3': 'sea-bee',
    'beesmart.avatar.professor_bee.v3': 'professor-bee',
    'beesmart.avatar.plumber_bee.v3': 'plumber-bee',
    'beesmart.avatar.space_bee.v3': 'space-bee',
    'beesmart.avatar.robo_bee.v3': 'robo-bee',
    'beesmart.avatar.zom_bee.v3': 'zom-bee',
    'beesmart.avatar.ware_bee.v3': 'ware-bee',
    'beesmart.avatar.rocker_bee.v3': 'rocker-bee',
    'beesmart.avatar.diva_bee.v3': 'diva-bee',
    'beesmart.avatar.techno_bee.v3': 'techno-bee',
    'beesmart.avatar.queen_bee.v3': 'queen-bee',
    'beesmart.avatar.buzz_bee.v3': 'buzz-bee',
}

APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG: Dict[str, str] = _load_app_store_ids_from_catalog()

# Reverse: catalog slug -> exact App Store product ID (for API response so picker sends correct product_id).
AVATAR_SLUG_TO_APP_STORE_PRODUCT_ID: Dict[str, str] = {v: k for k, v in APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG.items()}


def app_store_product_id_for_avatar(avatar_slug: str) -> str | None:
    """Return the exact App Store product ID for this avatar slug, or None."""
    if not avatar_slug:
        return None
    slug = (avatar_slug or '').strip().lower().replace('_', '-')
    return AVATAR_SLUG_TO_APP_STORE_PRODUCT_ID.get(slug)


def _ios_to_google_play_purchase_option_id(ios_id: str) -> str:
    """Convert Product ID (periods, underscores) to Purchase option ID format.
    Purchase option ID allows only: lowercase letters, numbers, hyphens.
    """
    if not ios_id:
        return ''
    return (ios_id or '').replace('.', '-').replace('_', '-').lower()


def google_play_product_id_for_avatar(avatar_slug: str) -> str | None:
    """Return the Google Play product ID for this avatar slug (step 1).
    Same as iOS: beesmart.avatar.<slug>.v2 (periods and underscores allowed).
    """
    return app_store_product_id_for_avatar(avatar_slug)


def google_play_purchase_option_id_for_avatar(avatar_slug: str) -> str | None:
    """Return the Google Play Purchase option ID (step 2 - hyphens only).
    Use for Availability and pricing → Purchase option ID field.
    """
    ios_id = app_store_product_id_for_avatar(avatar_slug)
    return _ios_to_google_play_purchase_option_id(ios_id) if ios_id else None


# Public: avatars → product IDs (fallback when not in App Store map; prefer app_store_product_id_for_avatar for API).
AVATAR_SKUS: Dict[str, str] = {
    **{slug: pid for pid, slug in APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG.items()},
    **build_skus_from_catalog(),
    **build_skus_from_names(_PNG_NAMES),
}
