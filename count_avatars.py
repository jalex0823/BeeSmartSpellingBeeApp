from avatar_catalog import AVATAR_CATALOG

tiers = {}
for av in AVATAR_CATALOG:
    tier = av['tier']
    tiers[tier] = tiers.get(tier, 0) + 1

print(f'Total: {len(AVATAR_CATALOG)}')
print('By tier:')
for k, v in sorted(tiers.items()):
    print(f'  {k}: {v}')

print('\nAll avatars:')
for av in sorted(AVATAR_CATALOG, key=lambda x: (x['tier'], x['name'])):
    print(f"{av['tier']:<15} | {av['name']}")
