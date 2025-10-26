"""
Avatar Diagnostic Tool - Compare Working vs Non-Working Avatar
Isolates issues by comparing one failing avatar against MascotBee
"""

import os
import json
from models import db, Avatar
from AjaSpellBApp import app

def check_avatar_files(avatar_slug):
    """Check file system presence and database records for an avatar"""
    print(f"\n{'='*70}")
    print(f"🔍 DIAGNOSTIC REPORT: {avatar_slug.upper()}")
    print(f"{'='*70}\n")
    
    with app.app_context():
        avatar = Avatar.query.filter_by(slug=avatar_slug).first()
        
        if not avatar:
            print(f"❌ Avatar '{avatar_slug}' not found in database!")
            return None
            
        print(f"📊 DATABASE RECORD:")
        print(f"   ID: {avatar.id}")
        print(f"   Name: {avatar.name}")
        print(f"   Slug: {avatar.slug}")
        print(f"   Folder: {avatar.folder_path}")
        print(f"   OBJ File: {avatar.obj_file}")
        print(f"   MTL File: {avatar.mtl_file}")
        print(f"   Texture: {avatar.texture_file}")
        print(f"   Thumbnail: {avatar.thumbnail_file}")
        
        # Check if binary data exists in DB
        print(f"\n📦 BINARY DATA IN DATABASE:")
        print(f"   OBJ Data: {'✅ YES' if avatar.obj_data else '❌ NO'}")
        print(f"   MTL Data: {'✅ YES' if avatar.mtl_data else '❌ NO'}")
        print(f"   Texture Data: {'✅ YES' if avatar.texture_data else '❌ NO'}")
        print(f"   Thumbnail Data: {'✅ YES' if avatar.thumbnail_data else '❌ NO'}")
        
        # Check file system
        print(f"\n💾 FILE SYSTEM CHECK:")
        folder_full_path = os.path.join('static', 'assets', 'avatars', avatar.folder_path)
        print(f"   Looking in: {folder_full_path}")
        
        if not os.path.exists(folder_full_path):
            print(f"   ❌ Folder does NOT exist!")
            return avatar
            
        print(f"   ✅ Folder exists")
        
        # Check each file
        files_to_check = [
            ('OBJ', avatar.obj_file),
            ('MTL', avatar.mtl_file),
            ('Texture', avatar.texture_file),
            ('Thumbnail', avatar.thumbnail_file)
        ]
        
        print(f"\n   📁 Files in folder:")
        for file_type, filename in files_to_check:
            if filename:
                file_path = os.path.join(folder_full_path, filename)
                exists = os.path.exists(file_path)
                size = os.path.getsize(file_path) if exists else 0
                status = f"✅ EXISTS ({size:,} bytes)" if exists else "❌ MISSING"
                print(f"      {file_type:10} {filename:30} {status}")
        
        # List ALL files in folder
        print(f"\n   🗂️  All files in folder:")
        if os.path.exists(folder_full_path):
            all_files = os.listdir(folder_full_path)
            for f in sorted(all_files):
                full_path = os.path.join(folder_full_path, f)
                size = os.path.getsize(full_path)
                print(f"      - {f} ({size:,} bytes)")
        
        # Generate expected API URLs
        print(f"\n🌐 EXPECTED API URLS:")
        print(f"   OBJ:       /static/assets/avatars/{avatar.folder_path}/{avatar.obj_file}")
        print(f"   MTL:       /static/assets/avatars/{avatar.folder_path}/{avatar.mtl_file}")
        print(f"   Texture:   /static/assets/avatars/{avatar.folder_path}/{avatar.texture_file}")
        print(f"   Thumbnail: /static/assets/avatars/{avatar.folder_path}/{avatar.thumbnail_file}")
        
        # Check for naming consistency
        print(f"\n🧩 NAMING CONSISTENCY CHECK:")
        def get_base_name(filename):
            """Extract base name without extension"""
            if not filename:
                return None
            return os.path.splitext(filename)[0]
        
        obj_base = get_base_name(avatar.obj_file)
        mtl_base = get_base_name(avatar.mtl_file)
        tex_base = get_base_name(avatar.texture_file)
        
        print(f"   OBJ base:     {obj_base}")
        print(f"   MTL base:     {mtl_base}")
        print(f"   Texture base: {tex_base}")
        
        if obj_base == mtl_base:
            print(f"   ✅ OBJ and MTL names match")
        else:
            print(f"   ⚠️  OBJ and MTL names DO NOT MATCH!")
            
        if obj_base == tex_base or tex_base == f"{obj_base}_texture":
            print(f"   ✅ Texture name compatible with OBJ")
        else:
            print(f"   ⚠️  Texture name may not match OBJ reference in MTL!")
        
        return avatar

def compare_avatars(working_slug, failing_slug):
    """Side-by-side comparison of working vs failing avatar"""
    print(f"\n{'='*70}")
    print(f"🔬 SIDE-BY-SIDE COMPARISON")
    print(f"{'='*70}\n")
    
    working = check_avatar_files(working_slug)
    failing = check_avatar_files(failing_slug)
    
    if not working or not failing:
        print("\n❌ Cannot compare - one or both avatars not found")
        return
    
    print(f"\n{'='*70}")
    print(f"🎯 KEY DIFFERENCES")
    print(f"{'='*70}\n")
    
    with app.app_context():
        working_avatar = Avatar.query.filter_by(slug=working_slug).first()
        failing_avatar = Avatar.query.filter_by(slug=failing_slug).first()
        
        # Compare binary data storage
        print("📦 Binary Data Storage:")
        print(f"   {working_slug:20} OBJ: {'YES' if working_avatar.obj_data else 'NO':3}  MTL: {'YES' if working_avatar.mtl_data else 'NO':3}  TEX: {'YES' if working_avatar.texture_data else 'NO':3}")
        print(f"   {failing_slug:20} OBJ: {'YES' if failing_avatar.obj_data else 'NO':3}  MTL: {'YES' if failing_avatar.mtl_data else 'NO':3}  TEX: {'YES' if failing_avatar.texture_data else 'NO':3}")
        
        # Compare file paths
        print(f"\n📁 Folder Structure:")
        print(f"   {working_slug:20} {working_avatar.folder_path}")
        print(f"   {failing_slug:20} {failing_avatar.folder_path}")
        
        # Compare file naming
        print(f"\n🏷️  File Naming:")
        print(f"   {working_slug:20} OBJ: {working_avatar.obj_file}")
        print(f"   {failing_slug:20} OBJ: {failing_avatar.obj_file}")
        print(f"   {working_slug:20} MTL: {working_avatar.mtl_file}")
        print(f"   {failing_slug:20} MTL: {failing_avatar.mtl_file}")
        print(f"   {working_slug:20} TEX: {working_avatar.texture_file}")
        print(f"   {failing_slug:20} TEX: {failing_avatar.texture_file}")
        
        print(f"\n{'='*70}")
        print(f"💡 RECOMMENDATIONS")
        print(f"{'='*70}\n")
        
        # Analyze and provide recommendations
        recommendations = []
        
        if not failing_avatar.obj_data and not failing_avatar.mtl_data and not failing_avatar.texture_data:
            recommendations.append("⚠️  No binary data in DB - Avatar relies purely on file system paths")
            
        failing_folder = os.path.join('static', 'assets', 'avatars', failing_avatar.folder_path)
        if not os.path.exists(failing_folder):
            recommendations.append("❌ CRITICAL: Avatar folder does not exist on file system")
            recommendations.append(f"   Create folder: {failing_folder}")
            
        # Check naming pattern
        obj_base = os.path.splitext(failing_avatar.obj_file)[0] if failing_avatar.obj_file else None
        mtl_base = os.path.splitext(failing_avatar.mtl_file)[0] if failing_avatar.mtl_file else None
        
        if obj_base and mtl_base and obj_base != mtl_base:
            recommendations.append(f"⚠️  OBJ/MTL name mismatch: '{obj_base}' vs '{mtl_base}'")
            recommendations.append(f"   MTL file references '{obj_base}.mtl' but file is '{failing_avatar.mtl_file}'")
            
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("✅ No obvious issues detected - may be a Three.js loading problem")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 2:
        # Single avatar diagnostic
        avatar_slug = sys.argv[1]
        check_avatar_files(avatar_slug)
    elif len(sys.argv) == 3:
        # Compare two avatars
        working = sys.argv[1]
        failing = sys.argv[2]
        compare_avatars(working, failing)
    else:
        # Default: compare mascot-bee (working) vs beeknight (failing)
        print("🔧 Running default diagnostic: MascotBee (working) vs BeeKnight (failing)")
        compare_avatars('mascot-bee', 'beeknight')
