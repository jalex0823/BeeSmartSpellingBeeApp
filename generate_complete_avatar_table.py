#!/usr/bin/env python3
"""
Generate complete avatar validation table with all fields for Railway deployment
"""

from avatar_catalog import AVATAR_CATALOG

print("=" * 120)
print("🐝 COMPLETE AVATAR CATALOG - RAILWAY DEPLOYMENT TABLE (39 Avatars)")
print("=" * 120)
print()

# Table header
print(f"{'#':<4} {'SKU':<20} {'Product ID':<35} {'Name':<25} {'Tier':<15} {'Price':<8} {'Description':<50}")
print("=" * 120)

# Sort by name for alphabetical order
sorted_avatars = sorted(AVATAR_CATALOG, key=lambda x: x['name'])

for i, avatar in enumerate(sorted_avatars, 1):
    sku = avatar['product_id'].replace('beesmart.avatar.', '')
    product_id = avatar['product_id']
    name = avatar['name'].replace(' Avatar', '')  # Remove "Avatar" suffix for cleaner display
    tier = avatar['tier']
    price = f"${avatar['price']:.2f}"
    desc = avatar['description'][:47] + "..." if len(avatar['description']) > 50 else avatar['description']
    
    print(f"{i:<4} {sku:<20} {product_id:<35} {name:<25} {tier:<15} {price:<8} {desc:<50}")

print("=" * 120)
print(f"\nTotal Avatars: {len(AVATAR_CATALOG)}")
print()

# Summary by tier
tier_summary = {}
for avatar in AVATAR_CATALOG:
    tier = avatar['tier']
    tier_summary[tier] = tier_summary.get(tier, 0) + 1

print("📊 TIER SUMMARY:")
print("-" * 60)
for tier, count in sorted(tier_summary.items()):
    print(f"  {tier:<20} {count:>3} avatars")

# Summary by price
price_summary = {}
for avatar in AVATAR_CATALOG:
    price = avatar['price']
    price_summary[price] = price_summary.get(price, 0) + 1

print()
print("💰 PRICE SUMMARY:")
print("-" * 60)
for price, count in sorted(price_summary.items()):
    print(f"  ${price:>6.2f}             {count:>3} avatars")

print()
print("=" * 120)

# Generate CSV export for Railway database
print("\n📄 CSV EXPORT (for Railway database import):")
print("=" * 120)
print("sku,product_id,name,tier,price,description")

for avatar in sorted_avatars:
    sku = avatar['product_id'].replace('beesmart.avatar.', '')
    product_id = avatar['product_id']
    name = avatar['name']
    tier = avatar['tier']
    price = f"{avatar['price']:.2f}"
    desc = avatar['description'].replace('"', '""')  # Escape quotes for CSV
    
    print(f'{sku},{product_id},"{name}",{tier},{price},"{desc}"')

print()
print("=" * 120)
print("✅ Ready for Railway database sync!")
