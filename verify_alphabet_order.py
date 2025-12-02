#!/usr/bin/env python3
"""
Verify that all 38 avatars will appear in correct alphabetical order
and that all 26 letters of the alphabet are covered.
"""

from avatar_catalog import AVATAR_CATALOG

# Extract all avatar names and their first letters
avatars = []
for avatar in AVATAR_CATALOG:
    name = avatar['name']
    # Extract first letter (handle "Al Bee" -> A, "Ice Bee" -> I, etc.)
    first_word = name.split()[0]
    first_letter = first_word[0].upper()
    avatars.append({
        'name': name,
        'id': avatar['id'],
        'letter': first_letter,
        'tier': avatar['tier']
    })

# Sort alphabetically by name
avatars.sort(key=lambda x: x['name'])

print("=" * 80)
print("🐝 AVATAR ALPHABETICAL ORDER (38 Total)")
print("=" * 80)

current_letter = None
for i, avatar in enumerate(avatars, 1):
    if avatar['letter'] != current_letter:
        current_letter = avatar['letter']
        print(f"\n--- {current_letter} ---")
    
    tier_emoji = {
        'default_free': '🆓',
        'earn_or_buy': '⭐',
        'premium': '💎',
        'mascot': '🏆'
    }
    emoji = tier_emoji.get(avatar['tier'], '❓')
    
    print(f"{i:2}. {emoji} {avatar['name']:<25} ({avatar['id']})")

# Check alphabet coverage
print("\n" + "=" * 80)
print("📊 ALPHABET COVERAGE CHECK")
print("=" * 80)

letters_covered = sorted(set(a['letter'] for a in avatars))
all_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
missing_letters = sorted(all_letters - set(letters_covered))

print(f"\n✅ Letters Covered ({len(letters_covered)}/26): {', '.join(letters_covered)}")

if missing_letters:
    print(f"❌ Missing Letters ({len(missing_letters)}): {', '.join(missing_letters)}")
else:
    print("🎉 ALL 26 LETTERS COVERED!")

print("\n" + "=" * 80)
print(f"Total Avatars: {len(avatars)}")
print("=" * 80)
