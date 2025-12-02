#!/usr/bin/env python3
"""
Verify Final 30 Avatars - Official List
"""

from avatar_catalog import AVATAR_CATALOG
import json

print("=" * 80)
print("🐝 OFFICIAL 30 AVATARS - FINAL VERIFICATION")
print("=" * 80)
print()

# Count by tier
free_starter = [av for av in AVATAR_CATALOG if av.get('tier') == 'default_free' or av.get('is_default_free')]
standard_tier = [av for av in AVATAR_CATALOG if av.get('tier') == 'earn_or_buy']
premium_tier = [av for av in AVATAR_CATALOG if av.get('tier') == 'premium']
mascot = [av for av in AVATAR_CATALOG if av.get('tier') == 'mascot']
special = [av for av in AVATAR_CATALOG if av.get('tier') == 'special' or av.get('tier') == 'anxious']

print(f"TOTAL AVATARS IN CATALOG: {len(AVATAR_CATALOG)}")
print()

print("FREE STARTER (should be 6):")
print("-" * 80)
for av in sorted(free_starter, key=lambda x: x['name']):
    print(f"  ✅ {av['name']:<35} (ID: {av['id']})")
print(f"  Count: {len(free_starter)}")
print()

print("STANDARD TIER - earn_or_buy (should be 11):")
print("-" * 80)
for av in sorted(standard_tier, key=lambda x: x['name']):
    points = av.get('unlock_points', 0)
    print(f"  ✅ {av['name']:<35} ({points:,} points)")
print(f"  Count: {len(standard_tier)}")
print()

print("PREMIUM TIER (should be 13):")
print("-" * 80)
for av in sorted(premium_tier, key=lambda x: x['name']):
    points = av.get('unlock_points', 0)
    print(f"  ✅ {av['name']:<35} ({points:,} points)")
print(f"  Count: {len(premium_tier)}")
print()

if mascot:
    print("MASCOT (special default):")
    for av in mascot:
        print(f"  📍 {av['name']}")
    print()

if special:
    print("SPECIAL TIER:")
    for av in special:
        print(f"  ⚠️ {av['name']}")
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Free Starter:  {len(free_starter)} (target: 6)")
print(f"Standard Tier: {len(standard_tier)} (target: 11)")
print(f"Premium Tier:  {len(premium_tier)} (target: 13)")
print(f"Mascot:        {len(mascot)}")
print(f"Special:       {len(special)}")
print(f"TOTAL:         {len(AVATAR_CATALOG)} (target: 30)")
print()

if len(AVATAR_CATALOG) == 30:
    print("✅ PERFECT! Catalog has exactly 30 avatars!")
else:
    print(f"⚠️ Count mismatch: Have {len(AVATAR_CATALOG)}, need 30")
    print(f"   Difference: {len(AVATAR_CATALOG) - 30:+d}")

# Check for removed duplicates
removed_ids = ['bee-knight', 'doc-bee', 'sea-bee', 'honey-comb', 'cutie-bee', 'buda-bee', 'frankenbee', 'j-rock-bee']
still_present = [rid for rid in removed_ids if any(av['id'] == rid for av in AVATAR_CATALOG)]

if still_present:
    print()
    print("⚠️ WARNING: These duplicates are still in catalog:")
    for rid in still_present:
        print(f"  • {rid}")
else:
    print()
    print("✅ All duplicates successfully removed!")

print()
