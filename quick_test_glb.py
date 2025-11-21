"""Simple test for GLB URLs"""
import requests

response = requests.get("http://localhost:5000/api/avatars")
if response.status_code == 200:
    data = response.json()
    avatars = data['avatars']
    
    glb_count = 0
    obj_count = 0
    
    print(f"\nTotal avatars: {len(avatars)}\n")
    
    for avatar in avatars:
        if 'urls' in avatar and 'glb' in avatar['urls']:
            glb_url = avatar['urls']['glb']
            if '.glb' in glb_url.lower():
                glb_count += 1
            elif '.obj' in glb_url.lower():
                obj_count += 1
                print(f"ERROR - {avatar['name']}: {glb_url}")
    
    print(f"\nGLB avatars: {glb_count}")
    print(f"OBJ avatars: {obj_count}\n")
    
    # Check mascot-bee specifically
    mascot = next((a for a in avatars if a.get('id') == 'mascot-bee'), None)
    if mascot:
        print(f"Mascot Bee GLB URL: {mascot['urls']['glb']}")
        print(f"Mascot Bee model_url: {mascot.get('model_url', 'N/A')}\n")
    
    if obj_count == 0:
        print("SUCCESS! All avatars use GLB format!")
    else:
        print(f"FAILED! {obj_count} avatars still use OBJ format")
else:
    print(f"API Error: {response.status_code}")
