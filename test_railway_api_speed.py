import requests
import json

print("Testing Railway API after optimization...\n")

try:
    r = requests.get('https://beesmart.up.railway.app/api/avatars', timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Response time: ~{r.elapsed.total_seconds():.2f}s\n")
    
    if r.status_code == 200:
        data = r.json()
        avatars = data.get('avatars', data if isinstance(data, list) else [])
        total = data.get('total', len(avatars))
        
        print(f"Total avatars returned: {total}\n")
        
        # Check new avatars
        new_slugs = ['beedoctor', 'beeknight', 'builderbee', 'buzzbotbee', 'buzzhero',
                     'detectivebee', 'explorerbee', 'frankenbee', 'motorcyclebuzzbee',
                     'queenbeemajesty', 'seabee', 'spacebeeexplorer', 'superbeehero']
        
        new_avatars = [a for a in avatars if a.get('id', '') in new_slugs]
        
        print(f"New avatars in API: {len(new_avatars)}/13\n")
        
        if new_avatars:
            print("Sample new avatar URLs:")
            for avatar in new_avatars[:3]:
                print(f"\n  {avatar.get('name')} ({avatar.get('id')})")
                urls = avatar.get('urls', {})
                print(f"    OBJ: {urls.get('model_obj', 'MISSING')}")
                print(f"    MTL: {urls.get('model_mtl', 'MISSING')}")
                print(f"    Texture: {urls.get('texture', 'MISSING')}")
                print(f"    Thumbnail: {urls.get('thumbnail', 'MISSING')}")
        else:
            print("❌ No new avatars found in API response!")
            
    else:
        print(f"Error: {r.text[:500]}")
        
except Exception as e:
    print(f"ERROR: {e}")
