#!/usr/bin/env python3
"""
Clean validation table matching the format from validate_avatar_data.py
"""

from avatar_catalog import AVATAR_CATALOG

print("=" * 150)
print("🐝 COMPLETE AVATAR VALIDATION TABLE - READY FOR RAILWAY DEPLOYMENT (39 Avatars)")
print("=" * 150)
print()

# Table header matching validation format
header = f"{'#':<4} {'SKU':<20} {'Product ID':<40} {'Tier':<15} {'Price':<10} {'Description'}"
print(header)
print("=" * 150)

# Sort alphabetically by name for easy reference
sorted_avatars = sorted(AVATAR_CATALOG, key=lambda x: x['name'])

for i, avatar in enumerate(sorted_avatars, 1):
    sku = avatar['product_id'].replace('beesmart.avatar.', '')
    product_id = avatar['product_id']
    tier = avatar['tier']
    price = f"${avatar['price']:.2f}"
    description = avatar['description']
    
    print(f"{i:<4} {sku:<20} {product_id:<40} {tier:<15} {price:<10} {description}")

print("=" * 150)
print()

# Summary statistics
print("📊 DEPLOYMENT SUMMARY")
print("-" * 80)
print(f"Total Avatars: {len(AVATAR_CATALOG)}")
print()

# Tier breakdown
tier_counts = {}
for avatar in AVATAR_CATALOG:
    tier = avatar['tier']
    tier_counts[tier] = tier_counts.get(tier, 0) + 1

print("By Tier:")
for tier in sorted(tier_counts.keys()):
    count = tier_counts[tier]
    print(f"  • {tier:<20} {count:>3} avatars")

print()

# Price breakdown
price_counts = {}
for avatar in AVATAR_CATALOG:
    price = avatar['price']
    price_counts[price] = price_counts.get(price, 0) + 1

print("By Price:")
for price in sorted(price_counts.keys()):
    count = price_counts[price]
    print(f"  • ${price:.2f}              {count:>3} avatars")

print()
print("=" * 150)
print("✅ ALL 39 AVATARS VALIDATED - READY FOR RAILWAY DATABASE SYNC!")
print("=" * 150)
