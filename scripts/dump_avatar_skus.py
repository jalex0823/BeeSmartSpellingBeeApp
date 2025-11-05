#!/usr/bin/env python3
"""
Dump avatar SKUs for store setup (CSV)

Outputs columns:
product_id,avatar_id,display_name,price_usd,purchasable,tier,source

- product_id: store product id (SKU)
- avatar_id: internal slug used by the app
- display_name: user-facing name
- price_usd: suggested price (if known from catalog)
- purchasable: whether the avatar is marked as purchasable in catalog (defaults True for extras)
- tier: catalog tier if available
- source: 'catalog' or 'extra'

Usage:
  python scripts/dump_avatar_skus.py > store/avatar_skus.csv

You can change the SKU prefix via env:
  AVATAR_SKU_PREFIX=com.beesmart.avatar

"""
import os
import csv
from pathlib import Path

try:
    from avatar_skus import AVATAR_SKUS, build_skus_from_names
except Exception as e:
    print(f"ERROR: cannot import avatar_skus: {e}")
    raise

# Optional: include extra PNG-based names to guarantee coverage
EXTRA_PNG_NAMES = [
    'AlBee!.png','BeeKnight!.png','BrotherBee!.png','BudaBee!.png','BuilderBee!.png',
    'BuzzBee!.png','CoolBee!.png','CutieBee!.png','DetectiveBee!.png','DivaBee!.png',
    'DocBee!.png','ExplorerBee!.png','FrankenBee!.png','HoneyComb!.png','JRockBee!.png',
    'MascotBee!.png','MotorBee!.png','OBee!.png','ProfessorBee!.png','QueenBee!.png',
    'RoboBee!.png','RockerBee!.png','SeaBee!.png','SelfieBee!.png','SingerBee!.png',
    'SpaceBee!.png','SuperBee!.png','VampBee!.png','WareBee!.png','ZomBee!.png'
]

# Load catalog if present
CATALOG = []
try:
    from avatar_catalog import AVATAR_CATALOG  # type: ignore
    if isinstance(AVATAR_CATALOG, list):
        CATALOG = AVATAR_CATALOG
except Exception:
    pass

catalog_by_id = { (a.get('id') or '').strip(): a for a in CATALOG if a.get('id') }

# Merge SKUs: catalog-derived plus extras
extras_map = build_skus_from_names(EXTRA_PNG_NAMES)
merged = dict(AVATAR_SKUS)  # slug -> sku
merged.update(extras_map)

rows = []
for slug, product_id in sorted(merged.items(), key=lambda kv: kv[0]):
    cat = catalog_by_id.get(slug)
    if cat:
        display_name = (cat.get('name') or slug).strip()
        price = cat.get('price')
        purch = bool(cat.get('is_purchasable', True))
        tier = (cat.get('tier') or '').strip()
        source = 'catalog'
    else:
        # Fallbacks for extras not in catalog
        display_name = ' '.join([p.capitalize() for p in slug.replace('-', ' ').split()])
        price = ''
        purch = True
        tier = ''
        source = 'extra'
    rows.append({
        'product_id': product_id,
        'avatar_id': slug,
        'display_name': display_name,
        'price_usd': price,
        'purchasable': purch,
        'tier': tier,
        'source': source,
    })

# Write to stdout as CSV
writer = csv.DictWriter(
    f=__import__('sys').stdout,
    fieldnames=['product_id','avatar_id','display_name','price_usd','purchasable','tier','source']
)
writer.writeheader()
for r in rows:
    writer.writerow(r)
