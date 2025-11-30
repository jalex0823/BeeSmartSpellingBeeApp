"""
Test that Fairy Bee appears in the avatar API
"""
from avatar_catalog import AVATAR_CATALOG

# Check if Fairy Bee is in the catalog
fairy = next((a for a in AVATAR_CATALOG if a['id'] == 'fairy-bee'), None)

if fairy:
    print("✅ Fairy Bee found in AVATAR_CATALOG")
    print(f"   Name: {fairy['name']}")
    print(f"   ID: {fairy['id']}")
    print(f"   Tier: {fairy['tier']}")
    print(f"   GLB: {fairy['obj_file']}")
    print(f"\n📊 Total avatars in catalog: {len(AVATAR_CATALOG)}")
else:
    print("❌ Fairy Bee NOT found in AVATAR_CATALOG")
    print(f"📊 Total avatars in catalog: {len(AVATAR_CATALOG)}")
