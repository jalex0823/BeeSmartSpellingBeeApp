#!/usr/bin/env python3
"""
Test the new avatars in the BeeSmart app
"""

import requests
import json

def test_avatar_api():
    """Test that all new avatars are accessible via the API."""
    try:
        # Test the avatar API
        response = requests.get('http://localhost:5000/api/avatars')
        response.raise_for_status()
        avatars = response.json()
        
        print(f'✅ API responded with {len(avatars)} avatars')
        print('\n🆕 New avatars found in API response:')
        
        new_avatar_slugs = [
            'beedoctor', 'beeknight', 'builderbee', 'buzzbotbee', 'buzzhero',
            'detectivebee', 'explorerbee', 'frankenbee', 'motorcyclebuzzbee',
            'queenbeemajesty', 'seabee', 'spacebeeexplorer', 'superbeehero'
        ]
        
        found_avatars = []
        for avatar in avatars:
            if avatar['slug'] in new_avatar_slugs:
                name = avatar['name']
                slug = avatar['slug']
                thumbnail = avatar['thumbnailUrl']
                print(f'  ✅ {name} ({slug})')
                print(f'     📷 Thumbnail: {thumbnail}')
                found_avatars.append(slug)th
        
        print(f'\n🎉 Found {len(found_avatars)}/{len(new_avatar_slugs)} new avatars in API!')
        
        # Check for missing avatars
        missing = set(new_avatar_slugs) - set(found_avatars)
        if missing:
            print(f'\n⚠️  Missing avatars: {", ".join(missing)}')
        
        return len(found_avatars) == len(new_avatar_slugs)
        
    except requests.exceptions.ConnectionError:
        print('❌ Could not connect to Flask server. Make sure it\'s running on localhost:5000')
        return False
    except Exception as e:
        print(f'❌ Error testing API: {e}')
        return False

if __name__ == "__main__":
    success = test_avatar_api()
    if success:
        print('\n🎊 All new avatars are successfully integrated!')
    else:
        print('\n❌ Some issues found with avatar integration.')