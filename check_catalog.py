from avatar_catalog import AVATAR_CATALOG

print(f'Total avatars in catalog: {len(AVATAR_CATALOG)}')

mascot = [a for a in AVATAR_CATALOG if a.get('tier') == 'mascot_free']
print(f'\nMascot tier avatars: {len(mascot)}')
for a in mascot:
    print(f"  - {a['name']} (tier: {a.get('tier')})")

default_free = [a for a in AVATAR_CATALOG if a.get('tier') == 'default_free']
print(f'\nDefault free avatars: {len(default_free)}')
for a in default_free:
    print(f"  - {a['name']} (tier: {a.get('tier')})")
