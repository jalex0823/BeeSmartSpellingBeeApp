"""Check mascot-bee database record"""
from AjaSpellBApp import app, db
from models import Avatar

with app.app_context():
    mascot = Avatar.query.filter_by(slug='mascot-bee').first()
    if mascot:
        print(f'✅ Found mascot-bee:')
        print(f'  ID: {mascot.id}')
        print(f'  folder_path: {mascot.folder_path}')
        print(f'  obj_file: {mascot.obj_file}')
        is_glb = mascot.obj_file.lower().endswith('.glb') if mascot.obj_file else False
        print(f'  is_glb: {is_glb}')
        
        # Get avatar data to see what API returns
        data = mascot.get_avatar_data()
        print(f'\n📊 API Response:')
        print(f'  glb URL: {data.get("urls", {}).get("glb", "NOT FOUND")}')
        print(f'  model_url: {data.get("model_url", "NOT FOUND")}')
    else:
        print('❌ mascot-bee NOT FOUND in database')
