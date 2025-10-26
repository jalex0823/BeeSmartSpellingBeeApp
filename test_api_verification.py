"""Test API endpoint to verify all 23 avatars are correctly served"""
from AjaSpellBApp import app

with app.test_client() as client:
    response = client.get('/api/avatars')
    data = response.get_json()
    
    print(f"✅ API Status: {data['status']}")
    print(f"✅ Total Avatars: {data['total']}")
    print()
    
    # Check a working avatar (Al Bee)
    working = [a for a in data['avatars'] if a['id'] == 'al-bee']
    if working:
        w = working[0]
        print(f"WORKING AVATAR (Al Bee):")
        print(f"  ID: {w['id']}")
        print(f"  Name: {w['name']}")
        print(f"  Thumbnail: {w['thumbnail']}")
        print(f"  OBJ URL: {w['urls']['model_obj']}")
    print()
    
    # Check all 13 new avatars
    new_slugs = ['beedoctor', 'beeknight', 'builderbee', 'buzzbotbee', 'buzzhero',
                 'detectivebee', 'explorerbee', 'frankenbee', 'motorcyclebuzzbee',
                 'queenbeemajesty', 'seabee', 'spacebeeexplorer', 'superbeehero']
    
    new_avatars = [a for a in data['avatars'] if a['id'] in new_slugs]
    
    print(f"NEW AVATARS: Found {len(new_avatars)} of 13")
    if len(new_avatars) == 13:
        print("✅ All 13 new avatars are in the API!")
        for avatar in new_avatars[:3]:  # Show first 3
            print(f"  - {avatar['name']}: {avatar['thumbnail']}")
    else:
        print(f"❌ Missing {13 - len(new_avatars)} avatars!")
        found_slugs = [a['id'] for a in new_avatars]
        missing = [s for s in new_slugs if s not in found_slugs]
        print(f"  Missing: {missing}")
    
    print()
    print(f"TOTAL CHECK: {len(data['avatars'])} avatars (should be 23)")
