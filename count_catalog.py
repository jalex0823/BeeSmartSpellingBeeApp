from avatar_catalog import AVATARS

print(f'Total avatars in catalog: {len(AVATARS)}')
active = [a for a in AVATARS if a.get('is_active', True)]
print(f'Active in catalog: {len(active)}')

print('\nAll avatar slugs in catalog:')
for i, avatar in enumerate(sorted(AVATARS, key=lambda x: x['slug']), 1):
    status = "✅" if avatar.get('is_active', True) else "❌"
    print(f'{i:2d}. {status} {avatar["slug"]}')
