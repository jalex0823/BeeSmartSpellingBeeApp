#!/usr/bin/env python3
"""
Railway Database Fix - Update broken avatar filenames
Run this on Railway using: railway run python railway_db_fix.py
"""
import os
import sys

# Inline catalog data (no imports needed)
BROKEN_AVATARS_FIX = {
    'astro-bee': {
        'obj_file': 'AstroBee.obj',
        'mtl_file': 'AstroBee.mtl',
        'texture_file': 'SpaceBee_Explorer_1021171329.png'
    },
    'biker-bee': {
        'obj_file': 'BikerBee.obj',
        'mtl_file': 'BikerBee.mtl',
        'texture_file': 'Motorcycle_Buzz_Bee_1018234507.png'
    },
    'brother-bee': {
        'obj_file': 'BrotherBee.obj',
        'mtl_file': 'BrotherBee.mtl',
        'texture_file': 'Buzz_Hero_1022221450.png'
    },
    'builder-bee': {
        'obj_file': 'BuilderBee.obj',
        'mtl_file': 'BuilderBee.mtl',
        'texture_file': 'Builder_Bee_1022223231.png'
    },
    'cool-bee': {
        'obj_file': 'CoolBee.obj',
        'mtl_file': 'CoolBee.mtl',
        'texture_file': 'Cool_Bee_1022222744.png'
    },
    'detective-bee': {
        'obj_file': 'DetectiveBee.obj',
        'mtl_file': 'DetectiveBee.mtl',
        'texture_file': 'Detective_Bee_1022222906.png'
    },
    'diva-bee': {
        'obj_file': 'DivaBee.obj',
        'mtl_file': 'DivaBee.mtl',
        'texture_file': 'Bee_Diva_1018233351.png'
    },
    'doctor-bee': {
        'obj_file': 'DoctorBee.obj',
        'mtl_file': 'DoctorBee.mtl',
        'texture_file': 'Bee_Doctor_1018225148.png'
    },
    'explorer-bee': {
        'obj_file': 'ExplorerBee.obj',
        'mtl_file': 'ExplorerBee.mtl',
        'texture_file': 'Explorer_Bee_1022223832.png'
    },
    'franken-bee': {
        'obj_file': 'FrankenBee.obj',
        'mtl_file': 'FrankenBee.mtl',
        'texture_file': 'Frankenbee_1021161641.png'
    },
    'knight-bee': {
        'obj_file': 'KnightBee.obj',
        'mtl_file': 'KnightBee.mtl',
        'texture_file': 'Bee_Knight_1018184515.png'
    },
    'queen-bee': {
        'obj_file': 'QueenBee.obj',
        'mtl_file': 'QueenBee.mtl',
        'texture_file': 'Queen_Bee_Majesty_1022222156.png'
    },
    'robo-bee': {
        'obj_file': 'RoboBee.obj',
        'mtl_file': 'RoboBee.mtl',
        'texture_file': 'Buzzbot_Bee_1022222436.png'
    },
    'seabea': {
        'obj_file': 'SeaBea.obj',
        'mtl_file': 'SeaBea.mtl',
        'texture_file': 'SeaBee_1019002514.png'
    },
    'superbee': {
        'obj_file': 'SuperBee.obj',
        'mtl_file': 'SuperBee.mtl',
        'texture_file': 'Super_Bee_Hero_1018233012.png'
    }
}

def main():
    print("🔧 Railway Database Fix - Updating broken avatars...")
    print(f"📍 Working directory: {os.getcwd()}")
    
    # Import Flask app and database
    try:
        from AjaSpellBApp import app, db
        from models import Avatar
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        sys.exit(1)
    
    updated_count = 0
    error_count = 0
    
    with app.app_context():
        for slug, file_info in BROKEN_AVATARS_FIX.items():
            try:
                avatar = Avatar.query.filter_by(slug=slug).first()
                
                if not avatar:
                    print(f"⚠️  Avatar '{slug}' not found in database")
                    error_count += 1
                    continue
                
                print(f"\n📝 {avatar.name} ({slug}):")
                print(f"   Current OBJ: {avatar.obj_file}")
                print(f"   New OBJ:     {file_info['obj_file']}")
                
                # Update fields
                avatar.obj_file = file_info['obj_file']
                avatar.mtl_file = file_info['mtl_file']
                avatar.texture_file = file_info['texture_file']
                
                db.session.add(avatar)
                updated_count += 1
                print(f"   ✅ Updated!")
                
            except Exception as e:
                print(f"❌ Error updating {slug}: {e}")
                error_count += 1
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"✅ Successfully updated {updated_count} broken avatars")
            if error_count > 0:
                print(f"⚠️  {error_count} avatars had errors")
            print(f"{'='*60}")
            print("\n🚀 Railway deployment should now serve correct avatar files!")
            print("   Test at: https://beesmart.up.railway.app/parent/avatar-manager")
            
        except Exception as e:
            print(f"\n❌ Failed to commit changes: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    main()
