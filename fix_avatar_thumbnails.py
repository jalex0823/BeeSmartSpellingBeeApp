#!/usr/bin/env python3
"""
Fix Avatar Thumbnails - Update database to use correct !.png filenames
"""
from AjaSpellBApp import app, db
from models import Avatar

# Correct thumbnail mappings
THUMBNAIL_MAPPINGS = {
    'al-bee': 'AlBee!.png',
    'anxious-bee': 'AnxiousBee!.png',
    'astro-bee': 'AstroBee!.png',
    'biker-bee': 'BikerBee!.png',
    'brother-bee': 'BrotherBee!.png',
    'builder-bee': 'BuilderBee!.png',
    'cool-bee': 'CoolBee!.png',
    'detective-bee': 'DetectiveBee!.png',
    'diva-bee': 'DivaBee!.png',
    'doctor-bee': 'DoctorBee!.png',
    'explorer-bee': 'ExplorerBee!.png',
    'franken-bee': 'Frankenbee!.png',
    'knight-bee': 'KnightBee!.png',
    'mascot-bee': 'MascotBee!.png',
    'monster-bee': 'MonsterBee!.png',
    'professor-bee': 'ProfessorBee!.png',
    'queen-bee': 'QueenBee!.png',
    'robo-bee': 'RoboBee!.png',
    'rocker-bee': 'RockerBee!.png',
    'seabea': 'Seabea!.png',
    'superbee': 'Superbee!.png',
    'vamp-bee': 'VampBee!.png',
    'ware-bee': 'WareBee!.png',
    'zom-bee': 'ZomBee!.png'
}

def main():
    print("🔧 Fixing Avatar Thumbnails...")
    
    with app.app_context():
        updated_count = 0
        
        for slug, correct_thumbnail in THUMBNAIL_MAPPINGS.items():
            avatar = Avatar.query.filter_by(slug=slug).first()
            
            if not avatar:
                print(f"⚠️  Avatar '{slug}' not found in database")
                continue
            
            if avatar.thumbnail_file != correct_thumbnail:
                print(f"📝 {avatar.name} ({slug}):")
                print(f"   Current: {avatar.thumbnail_file}")
                print(f"   Correct: {correct_thumbnail}")
                
                avatar.thumbnail_file = correct_thumbnail
                db.session.add(avatar)
                updated_count += 1
                print(f"   ✅ Updated!")
            else:
                print(f"✅ {avatar.name} ({slug}): Already correct ({correct_thumbnail})")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"✅ Successfully updated {updated_count} avatar thumbnails")
            print(f"{'='*60}")
            print("\n🚀 All avatars now use correct !.png thumbnail files!")
            
        except Exception as e:
            print(f"\n❌ Failed to commit changes: {e}")
            db.session.rollback()
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
