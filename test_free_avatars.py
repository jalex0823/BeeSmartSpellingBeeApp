#!/usr/bin/env python3
"""Quick test to verify free avatars are correctly unlocked"""

from avatar_catalog import AVATAR_CATALOG, check_avatar_unlocked

# Test as a registered user with 0 points (fresh account)
user_honey_points = 0
purchased_avatars = []
is_guest = False

print("=" * 60)
print("FREE AVATARS TEST (Registered User, 0 Points)")
print("=" * 60)

# Check mascot_free tier
mascot_avatars = [a for a in AVATAR_CATALOG if a.get('tier') == 'mascot_free']
print(f"\n🐝 MASCOT FREE ({len(mascot_avatars)}):")
for avatar in mascot_avatars:
    result = check_avatar_unlocked(avatar['id'], user_honey_points, purchased_avatars, is_guest=False)
    status = "✅ UNLOCKED" if result['unlocked'] else "🔒 LOCKED"
    print(f"  {status} - {avatar['name']} ({avatar['id']})")

# Check default_free tier
default_free = [a for a in AVATAR_CATALOG if a.get('tier') == 'default_free']
print(f"\n🆓 DEFAULT FREE ({len(default_free)}):")
for avatar in default_free:
    result = check_avatar_unlocked(avatar['id'], user_honey_points, purchased_avatars, is_guest=False)
    status = "✅ UNLOCKED" if result['unlocked'] else "🔒 LOCKED"
    print(f"  {status} - {avatar['name']} ({avatar['id']})")

# Check earn_or_buy tier (should be locked)
earn_or_buy = [a for a in AVATAR_CATALOG if a.get('tier') == 'earn_or_buy'][:3]  # Just first 3
print(f"\n💰 EARN OR BUY (sample):")
for avatar in earn_or_buy:
    result = check_avatar_unlocked(avatar['id'], user_honey_points, purchased_avatars, is_guest=False)
    status = "✅ UNLOCKED" if result['unlocked'] else "🔒 LOCKED"
    print(f"  {status} - {avatar['name']} ({avatar['id']}) - {avatar.get('unlock_points', 0)} points")

# Check premium tier (should be locked)
premium = [a for a in AVATAR_CATALOG if a.get('tier') == 'premium'][:3]  # Just first 3
print(f"\n👑 PREMIUM (sample):")
for avatar in premium:
    result = check_avatar_unlocked(avatar['id'], user_honey_points, purchased_avatars, is_guest=False)
    status = "✅ UNLOCKED" if result['unlocked'] else "🔒 LOCKED"
    print(f"  {status} - {avatar['name']} ({avatar['id']}) - ${avatar.get('price', 0)}")

print("\n" + "=" * 60)
total_free = len(mascot_avatars) + len(default_free)
print(f"TOTAL FREE AVATARS: {total_free}")
print(f"  - {len(mascot_avatars)} Mascot (all users)")
print(f"  - {len(default_free)} Default Free (registered users)")
print("=" * 60)
