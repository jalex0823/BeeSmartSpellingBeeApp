"""
Register missing GLB avatars: Reactivate MotorBee and add HoneyComb
"""
from AjaSpellBApp import app, db
from models import Avatar

with app.app_context():
    print("=== Avatar Registration Script ===\n")
    
    # 1. Reactivate MotorBee
    print("1. Checking motorcycle-bee...")
    motor = Avatar.query.filter_by(slug='motorcycle-bee').first()
    if motor:
        # Ensure canonical display name
        if motor.name != 'MotorBee':
            old_name = motor.name
            motor.name = 'MotorBee'
            print(f"   ✓ Renamed '{old_name}' → 'MotorBee'")
        if not motor.is_active:
            motor.is_active = True
            print(f"   ✓ Reactivated MotorBee (was inactive)")
        else:
            print(f"   ✓ MotorBee already active")
    else:
        # Create if doesn't exist
        motor = Avatar(
            slug='motorcycle-bee',
            name='MotorBee',
            folder_path='glb_files',
            obj_file='MotorBee.glb',
            mtl_file=None,
            thumbnail_file='MotorBee!.png',
            is_active=True
        )
        db.session.add(motor)
        print(f"   ✓ Created new MotorBee record")
    
    # 2. Add HoneyComb
    print("2. Checking honeycomb...")
    honeycomb = Avatar.query.filter_by(slug='honeycomb').first()
    if not honeycomb:
        honeycomb = Avatar(
            slug='honeycomb',
            name='HoneyComb',
            folder_path='glb_files',
            obj_file='HoneyComb.glb',
            mtl_file=None,
            thumbnail_file='HoneyComb!.png',
            is_active=True
        )
        db.session.add(honeycomb)
        print(f"   ✓ Created new HoneyComb record")
    else:
        if not honeycomb.is_active:
            honeycomb.is_active = True
            print(f"   ✓ Reactivated HoneyComb (was inactive)")
        else:
            print(f"   ✓ HoneyComb already active")
    
    # Commit changes
    db.session.commit()
    print("\n=== Database Updated ===")
    
    # Verify final counts
    print("\nFinal Avatar Counts:")
    glb_avatars = Avatar.query.filter_by(folder_path='glb_files', is_active=True).all()
    obj_avatars = Avatar.query.filter(Avatar.folder_path != 'glb_files', Avatar.is_active == True).all()
    
    print(f"  GLB Avatars: {len(glb_avatars)}")
    print(f"  OBJ Avatars: {len(obj_avatars)}")
    print(f"  TOTAL ACTIVE: {len(glb_avatars) + len(obj_avatars)}")
    
    print("\nGLB Avatars:")
    for avatar in sorted(glb_avatars, key=lambda x: x.name):
        print(f"  - {avatar.name} ({avatar.obj_file})")
