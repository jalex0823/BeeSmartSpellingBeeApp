from AjaSpellBApp import app

with app.app_context():
    with app.test_client() as client:
        response = client.get('/api/avatars')
        data = response.get_json()
        
        # Count Knight Bee occurrences
        knight_bees = [a for a in data if 'Knight' in a.get('name', '')]
        
        print('='*80)
        print(f'API /api/avatars returns {len(data)} total avatars')
        print(f'Knight Bee appears {len(knight_bees)} time(s) in API')
        print('='*80)
        
        if len(knight_bees) > 1:
            print('\n⚠️  DUPLICATE KNIGHT BEE FOUND IN API!')
            for kb in knight_bees:
                print(f'  - ID: {kb.get("id")} | Name: {kb.get("name")} | Slug: {kb.get("slug")}')
        elif len(knight_bees) == 1:
            print('\n✅ Only ONE Knight Bee in API (correct)')
            kb = knight_bees[0]
            print(f'  - ID: {kb.get("id")} | Name: {kb.get("name")} | Slug: {kb.get("slug")}')
        else:
            print('\n❌ NO Knight Bee found in API!')
        
        print('\n' + '='*80)
        print('ALL AVATARS IN API:')
        print('='*80)
        for i, avatar in enumerate(data, 1):
            name = avatar.get('name', 'Unknown')
            slug = avatar.get('slug', 'unknown')
            print(f'{i:2}. {name:25} | {slug}')
