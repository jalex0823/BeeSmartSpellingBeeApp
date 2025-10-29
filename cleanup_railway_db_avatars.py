"""
Remove broken OBJ avatars from Railway PostgreSQL database.
Run this script to clean up Railway production database.
"""
import os
import sys

# Set Railway DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway'

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from AjaSpellBApp import app, db
from models import Avatar

# Broken OBJ avatars that were replaced with GLB - REMOVE FROM DATABASE
BROKEN_OBJ_SLUGS = [
    'astro-bee',        # Replaced with GLB
    'biker-bee',        # Replaced with GLB
    'builder-bee',      # Replaced with GLB
    'cool-bee',         # Replaced with GLB (cutie-bee)
    'detective-bee',    # Replaced with GLB
    'diva-bee',         # Replaced with GLB
    'doctor-bee',       # Replaced with GLB
    'explorer-bee',     # Replaced with GLB
    'franken-bee',      # Replaced with GLB
    'knight-bee',       # Replaced with GLB
    'queen-bee',        # Replaced with GLB
    'robo-bee',         # Replaced with GLB (motorcycle-bee)
    'sea-bee',          # Replaced with GLB
    'super-bee',        # Replaced with GLB
    'space-bee',        # Replaced with GLB
    'motorcycle-bee',   # May be old version
    'brother-bee',      # Not in use
]

# Working OBJ avatars to KEEP
WORKING_OBJ_SLUGS = [
    'al-bee',
    'anxious-bee',
    'mascot-bee',
    'monster-bee',
    'professor-bee',
    'rocker-bee',
    'vamp-bee',
    'ware-bee',
    'zom-bee'
]

def main():
    with app.app_context():
        print("=" * 70)
        print("🚂 RAILWAY POSTGRESQL DATABASE CLEANUP")
        print("=" * 70)
        
        # Check database type
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'unknown')
        if 'postgresql' in db_uri:
            print("✅ Connected to: Railway PostgreSQL")
            print(f"   Database: {db_uri.split('@')[1] if '@' in db_uri else 'railway'}")
        else:
            print(f"❌ ERROR: Not connected to Railway PostgreSQL!")
            print(f"   Current: {db_uri[:50]}...")
            return
        
        print("\n🔍 Scanning database for broken OBJ avatars...")
        
        # Get all avatars
        try:
            all_avatars = Avatar.query.all()
            print(f"📊 Total avatars in database: {len(all_avatars)}")
        except Exception as e:
            print(f"❌ Error querying database: {e}")
            return
        
        # Find broken OBJ avatars to delete
        to_delete = []
        for avatar in all_avatars:
            if avatar.slug in BROKEN_OBJ_SLUGS:
                # Check if it's an OBJ file (not GLB)
                if avatar.obj_file and avatar.obj_file.endswith('.obj'):
                    to_delete.append(avatar)
        
        if not to_delete:
            print("\n✅ No broken OBJ avatars found in Railway database!")
            print("   All clean! 🎉")
            
            # Show current state
            print("\n📊 Current Database State:")
            obj_count = len([a for a in all_avatars if a.obj_file and a.obj_file.endswith('.obj')])
            glb_count = len([a for a in all_avatars if a.obj_file and a.obj_file.endswith('.glb')])
            print(f"   Total: {len(all_avatars)} avatars")
            print(f"   OBJ format: {obj_count}")
            print(f"   GLB format: {glb_count}")
            return
        
        print(f"\n⚠️  Found {len(to_delete)} broken OBJ avatars to DELETE:")
        print("-" * 70)
        for avatar in to_delete:
            print(f"   🗑️  {avatar.slug}: {avatar.name}")
            print(f"       File: {avatar.obj_file}")
            print(f"       Active: {avatar.is_active}")
            print()
        
        print("=" * 70)
        print("✅ KEEPING these avatars:")
        print("-" * 70)
        
        # Show what we're keeping
        keeping = [a for a in all_avatars if a.slug in WORKING_OBJ_SLUGS or 
                   (a.obj_file and a.obj_file.endswith('.glb'))]
        
        obj_count = len([a for a in keeping if a.obj_file and a.obj_file.endswith('.obj')])
        glb_count = len([a for a in keeping if a.obj_file and a.obj_file.endswith('.glb')])
        
        print(f"   ✓ {obj_count} working OBJ avatars:")
        for avatar in keeping:
            if avatar.obj_file and avatar.obj_file.endswith('.obj'):
                print(f"      - {avatar.slug}: {avatar.name}")
        
        print(f"\n   ✓ {glb_count} GLB avatars:")
        for avatar in keeping:
            if avatar.obj_file and avatar.obj_file.endswith('.glb'):
                print(f"      - {avatar.slug}: {avatar.name}")
        
        # Confirm deletion
        print("\n" + "=" * 70)
        print("⚠️  WARNING: This will modify the PRODUCTION Railway database!")
        response = input(f"\nDELETE {len(to_delete)} broken OBJ avatars from Railway? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("❌ Aborted - no changes made to Railway database")
            return
        
        # Delete avatars
        print("\n🗑️  Deleting broken OBJ avatars from Railway database...")
        deleted_count = 0
        
        for avatar in to_delete:
            try:
                db.session.delete(avatar)
                print(f"   ✓ Marked for deletion: {avatar.slug}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ Error marking {avatar.slug}: {e}")
        
        # Commit changes
        try:
            db.session.commit()
            print(f"\n✅ Successfully deleted {deleted_count} broken OBJ avatars from Railway!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing changes to Railway: {e}")
            return
        
        # Verify final state
        print("\n" + "=" * 70)
        print("📊 Final Railway Database State:")
        print("-" * 70)
        
        remaining = Avatar.query.all()
        obj_remaining = [a for a in remaining if a.obj_file and a.obj_file.endswith('.obj')]
        glb_remaining = [a for a in remaining if a.obj_file and a.obj_file.endswith('.glb')]
        
        print(f"   Total avatars: {len(remaining)}")
        print(f"   OBJ format: {len(obj_remaining)} (9 working)")
        print(f"   GLB format: {len(glb_remaining)} (17 new)")
        
        print("\n✅ Railway database cleanup complete! 🎉")
        print("   Your production app now has clean avatar data!")

if __name__ == '__main__':
    main()
