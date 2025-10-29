import requests
import json

r = requests.get('http://localhost:5000/api/avatars')
print(f'API Status: {r.status_code}')

data = r.json()
avatars = data.get('avatars', [])
print(f'Total: {len(avatars)}')

obj = [a for a in avatars if a.get('obj_file', '').endswith('.obj')]
glb = [a for a in avatars if a.get('obj_file', '').endswith('.glb')]

print(f'OBJ: {len(obj)}, GLB: {len(glb)}')

if glb:
    print(f'\nFirst GLB: {glb[0]["name"]}')
    print(f'  URL: {glb[0]["urls"]["model_obj"]}')
    print(f'  Thumbnail: {glb[0]["urls"]["thumbnail"]}')
