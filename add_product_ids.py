#!/usr/bin/env python3
"""
Add product_id field to all avatars in avatar_catalog.py for IAP integration.
Format: beesmart.avatar.{id_with_underscores}
"""

import re

# Read the current catalog
with open('avatar_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Product ID mapping for all 30 avatars
product_id_map = {
    "al-bee": "beesmart.avatar.al_bee",
    "brother-bee": "beesmart.avatar.brother_bee",
    "buda-bee": "beesmart.avatar.buda_bee",
    "builder-bee": "beesmart.avatar.builder_bee",
    "buzz-bee": "beesmart.avatar.buzz_bee",
    "cool-bee": "beesmart.avatar.cool_bee",
    "cutie-bee": "beesmart.avatar.cutie_bee",
    "detective-bee": "beesmart.avatar.detective_bee",
    "diva-bee": "beesmart.avatar.diva_bee",
    "doc-bee": "beesmart.avatar.doc_bee",
    "explorer-bee": "beesmart.avatar.explorer_bee",
    "franken-bee": "beesmart.avatar.franken_bee",
    "honey-comb": "beesmart.avatar.honey_comb",
    "j-rock-bee": "beesmart.avatar.j_rock_bee",
    "knight-bee": "beesmart.avatar.knight_bee",
    "mascot-bee": "beesmart.avatar.mascot_bee",
    "motor-bee": "beesmart.avatar.motor_bee",
    "o-bee": "beesmart.avatar.o_bee",
    "professor-bee": "beesmart.avatar.professor_bee",
    "queen-bee": "beesmart.avatar.queen_bee",
    "robo-bee": "beesmart.avatar.robo_bee",
    "rocker-bee": "beesmart.avatar.rocker_bee",
    "sea-bee": "beesmart.avatar.sea_bee",
    "selfie-bee": "beesmart.avatar.selfie_bee",
    "singer-bee": "beesmart.avatar.singer_bee",
    "space-bee": "beesmart.avatar.space_bee",
    "super-bee": "beesmart.avatar.super_bee",
    "vamp-bee": "beesmart.avatar.vamp_bee",
    "ware-bee": "beesmart.avatar.ware_bee",
    "zom-bee": "beesmart.avatar.zom_bee",
}

# Find and replace each avatar entry
count_added = 0
for avatar_id, product_id in product_id_map.items():
    # Look for this avatar's dictionary entry
    # Pattern: "id": "avatar-id", ... followed by either "price": X, or is_purchasable
    # We'll insert product_id right after the "id" field
    
    # Match the specific avatar entry and add product_id after the id field
    pattern = rf'("id":\s*"{re.escape(avatar_id)}",)'
    replacement = rf'\1\n        "product_id": "{product_id}",'
    
    old_content = content
    content = re.sub(pattern, replacement, content)
    
    if content != old_content:
        count_added += 1
        print(f"✓ Added product_id to {avatar_id}: {product_id}")

# Write the updated catalog
with open('avatar_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Successfully added product_id field to {count_added}/30 avatars")
print(f"Updated avatar_catalog.py")
