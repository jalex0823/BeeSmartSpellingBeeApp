#!/usr/bin/env python3
"""Test the avatars API endpoint"""
import requests

try:
    response = requests.get('http://localhost:5000/api/avatars', timeout=5)
    avatars = response.json()
    
    print(f'✅ /api/avatars endpoint working!')
    print(f'📊 Total avatars: {len(avatars)}\n')
    
    print('OBJ Avatars (9):')
    obj_avatars = [a for a in avatars if a.get('folder_path') != 'glb_files']
    for a in sorted(obj_avatars, key=lambda x: x['sort_order']):
        print(f'  ✓ {a["slug"]}: {a["name"]}')
    
    print(f'\nGLB Avatars (17):')
    glb_avatars = [a for a in avatars if a.get('folder_path') == 'glb_files']
    for a in sorted(glb_avatars, key=lambda x: x['sort_order']):
        thumbnail = a.get('thumbnail_file', 'N/A').split('/')[-1] if a.get('thumbnail_file') else 'N/A'
        print(f'  ✓ {a["slug"]}: {a["name"]} → {thumbnail}')
    
except Exception as e:
    print(f'❌ Error: {e}')
