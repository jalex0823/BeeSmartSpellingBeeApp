from AjaSpellBApp import app, db
from models import Avatar

with app.app_context():
    avatars = Avatar.query.filter_by(is_active=True).all()
    print(f"\n✅ Found {len(avatars)} active avatars:\n")
    
    for a in avatars[:10]:
        is_glb = a.obj_file.lower().endswith('.glb') if a.obj_file else False
        file_type = "GLB" if is_glb else "OBJ"
        print(f"  {a.slug:20} | {file_type:3} | {a.obj_file:30} | {a.folder_path}")
