#!/usr/bin/env python3
"""
Complete avatar database fix for Railway deployment
Fixes both OBJ/MTL filenames AND thumbnail filenames
"""
from AjaSpellBApp import app, db
from models import Avatar

# Complete mapping for all 24 avatars
AVATAR_FIXES = {
    'al-bee': {
        'obj_file': 'AlBee.obj',
        'mtl_file': 'AlBee.mtl',
        'texture_file': 'AlBee.png',
        'thumbnail_file': 'AlBee!.png'
    },
    'anxious-bee': {
        'obj_file': 'AnxiousBee.obj',
        'mtl_file': 'AnxiousBee.mtl',
        'texture_file': 'AnxiousBee.png',
        'thumbnail_file': 'AnxiousBee!.png'
    },
    'astro-bee': {
        'obj_file': 'AstroBee.obj',
        'mtl_file': 'AstroBee.mtl',
        'texture_file': 'SpaceBee_Explorer_1021171329.png',
        'thumbnail_file': 'AstroBee!.png'
    },
    'biker-bee': {
        'obj_file': 'BikerBee.obj',
        'mtl_file': 'BikerBee.mtl',
        'texture_file': 'Motorcycle_Buzz_Bee_1018234507.png',
        'thumbnail_file': 'BikerBee!.png'
    },
    'brother-bee': {
        'obj_file': 'BrotherBee.obj',
        'mtl_file': 'BrotherBee.mtl',
        'texture_file': 'Buzz_Hero_1022221450.png',
        'thumbnail_file': 'BrotherBee!.png'
    },
    'builder-bee': {
        'obj_file': 'BuilderBee.obj',
        'mtl_file': 'BuilderBee.mtl',
        'texture_file': 'Builder_Bee_1022223231.png',
        'thumbnail_file': 'BuilderBee!.png'
    },
    'cool-bee': {
        'obj_file': 'CoolBee.obj',
        'mtl_file': 'CoolBee.mtl',
        'texture_file': 'Cool_Bee_1022222744.png',
        'thumbnail_file': 'CoolBee!.png'
    },
    'detective-bee': {
        'obj_file': 'DetectiveBee.obj',
        'mtl_file': 'DetectiveBee.mtl',
        'texture_file': 'Detective_Bee_1022222906.png',
        'thumbnail_file': 'DetectiveBee!.png'
    },
    'diva-bee': {
        'obj_file': 'DivaBee.obj',
        'mtl_file': 'DivaBee.mtl',
        'texture_file': 'Bee_Diva_1018233351.png',
        'thumbnail_file': 'DivaBee!.png'
    },
    'doctor-bee': {
        'obj_file': 'DoctorBee.obj',
        'mtl_file': 'DoctorBee.mtl',
        'texture_file': 'Bee_Doctor_1018225148.png',
        'thumbnail_file': 'DoctorBee!.png'
    },
    'explorer-bee': {
        'obj_file': 'ExplorerBee.obj',
        'mtl_file': 'ExplorerBee.mtl',
        'texture_file': 'Explorer_Bee_1022223832.png',
        'thumbnail_file': 'ExplorerBee!.png'
    },
    'franken-bee': {
        'obj_file': 'FrankenBee.obj',
        'mtl_file': 'FrankenBee.mtl',
        'texture_file': 'Frankenbee_1021161641.png',
        'thumbnail_file': 'Frankenbee!.png'
    },
    'knight-bee': {
        'obj_file': 'KnightBee.obj',
        'mtl_file': 'KnightBee.mtl',
        'texture_file': 'Bee_Knight_1018184515.png',
        'thumbnail_file': 'KnightBee!.png'
    },
    'mascot-bee': {
        'obj_file': 'MascotBee.obj',
        'mtl_file': 'MascotBee.mtl',
        'texture_file': 'MascotBee.png',
        'thumbnail_file': 'MascotBee!.png'
    },
    'monster-bee': {
        'obj_file': 'MonsterBee.obj',
        'mtl_file': 'MonsterBee.mtl',
        'texture_file': 'MonsterBee.png',
        'thumbnail_file': 'MonsterBee!.png'
    },
    'professor-bee': {
        'obj_file': 'ProfessorBee.obj',
        'mtl_file': 'ProfessorBee.mtl',
        'texture_file': 'ProfessorBee.png',
        'thumbnail_file': 'ProfessorBee!.png'
    },
    'queen-bee': {
        'obj_file': 'QueenBee.obj',
        'mtl_file': 'QueenBee.mtl',
        'texture_file': 'Queen_Bee_Majesty_1022222156.png',
        'thumbnail_file': 'QueenBee!.png'
    },
    'robo-bee': {
        'obj_file': 'RoboBee.obj',
        'mtl_file': 'RoboBee.mtl',
        'texture_file': 'Buzzbot_Bee_1022222436.png',
        'thumbnail_file': 'RoboBee!.png'
    },
    'rocker-bee': {
        'obj_file': 'RockerBee.obj',
        'mtl_file': 'RockerBee.mtl',
        'texture_file': 'RockerBee.png',
        'thumbnail_file': 'RockerBee!.png'
    },
    'seabea': {
        'obj_file': 'Seabea.obj',
        'mtl_file': 'Seabea.mtl',
        'texture_file': 'SeaBee_1019002514.png',
        'thumbnail_file': 'Seabea!.png'
    },
    'superbee': {
        'obj_file': 'Superbee.obj',
        'mtl_file': 'Superbee.mtl',
        'texture_file': 'Super_Bee_Hero_1018233012.png',
        'thumbnail_file': 'Superbee!.png'
    },
    'vamp-bee': {
        'obj_file': 'VampBee.obj',
        'mtl_file': 'VampBee.mtl',
        'texture_file': 'VampBee.png',
        'thumbnail_file': 'VampBee!.png'
    },
    'ware-bee': {
        'obj_file': 'WareBee.obj',
        'mtl_file': 'WareBee.mtl',
        'texture_file': 'WareBee.png',
        'thumbnail_file': 'WareBee!.png'
    },
    'zom-bee': {
        'obj_file': 'ZomBee.obj',
        'mtl_file': 'ZomBee.mtl',
        'texture_file': 'ZomBee.png',
        'thumbnail_file': 'ZomBee!.png'
    }
}

def fix_avatars():
    """Fix all avatar file references in database"""
    with app.app_context():
        print("🔧 Starting complete avatar database fix...")
        print("=" * 60)
        
        updated_count = 0
        for slug, fixes in AVATAR_FIXES.items():
            avatar = Avatar.query.filter_by(slug=slug).first()
            
            if not avatar:
                print(f"⚠️  Avatar not found: {slug}")
                continue
            
            # Update all file fields
            avatar.obj_file = fixes['obj_file']
            avatar.mtl_file = fixes['mtl_file']
            avatar.texture_file = fixes['texture_file']
            avatar.thumbnail_file = fixes['thumbnail_file']
            
            print(f"✅ {avatar.name} ({slug})")
            print(f"   OBJ: {fixes['obj_file']}")
            print(f"   MTL: {fixes['mtl_file']}")
            print(f"   TEX: {fixes['texture_file']}")
            print(f"   THUMB: {fixes['thumbnail_file']}")
            
            updated_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print("=" * 60)
        print(f"✅ Successfully updated {updated_count} avatars!")
        print("=" * 60)

if __name__ == '__main__':
    fix_avatars()
