from avatar_catalog import AVATAR_CATALOG

honey_points = 11500

print(f"Avatars unlockable with {honey_points:,} Honey Points:\n")

default_free = [a for a in AVATAR_CATALOG if a.get('tier') in ['default_free', 'mascot_free'] or a.get('is_default_free')]
earn_or_buy = [a for a in AVATAR_CATALOG if a.get('tier') == 'earn_or_buy' and (a.get('unlock_points') or 0) <= honey_points]

unlocked = default_free + earn_or_buy

print(f"Total Unlocked: {len(unlocked)}\n")

print(f"DEFAULT FREE ({len(default_free)}):")
for a in default_free:
    print(f"  ✅ {a['name']}")

print(f"\nEARNED via POINTS ({len(earn_or_buy)}):")
for a in sorted(earn_or_buy, key=lambda x: x.get('unlock_points', 0)):
    print(f"  ✅ {a['name']} - {a.get('unlock_points', 0):,} points")

print(f"\nLOCKED EARN-OR-BUY:")
locked_earn = [a for a in AVATAR_CATALOG if a.get('tier') == 'earn_or_buy' and (a.get('unlock_points') or 0) > honey_points]
for a in sorted(locked_earn, key=lambda x: x.get('unlock_points', 0)):
    needed = (a.get('unlock_points', 0) - honey_points)
    print(f"  🔒 {a['name']} - Need {needed:,} more points (total: {a.get('unlock_points', 0):,})")
