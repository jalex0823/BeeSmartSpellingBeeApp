#!/usr/bin/env python3
"""
Identify Avatar File Mismatches
Checks all avatar folders and identifies naming mismatches
"""

import os
import re
from pathlib import Path

def extract_avatar_name_from_filename(filename):
    """Extract avatar name from filename like 'Professor_Bee_1019002841_texture.obj'"""
    # Remove extension
    base = filename.rsplit('.', 1)[0]
    
    # Remove timestamp pattern like _1019002841_texture or _1019002841
    base = re.sub(r'_\d{10}(_texture)?$', '', base)
    
    # Convert to lowercase and replace underscores with hyphens for ID format
    avatar_id = base.lower().replace('_', '-')
    
    return avatar_id, base  # Return both ID format and original name

def check_avatar_folders():
    """Check all avatar folders for naming mismatches"""
    
    base_path = Path("static/assets/avatars")
    
    if not base_path.exists():
        print("❌ Avatar path not found:", base_path)
        return
    
    print("=" * 80)
    print("🔍 AVATAR FILE MISMATCH CHECKER")
    print("=" * 80)
    print()
    
    mismatches = []
    correct_matches = []
    
    # Get all avatar folders
    avatar_folders = [f for f in base_path.iterdir() if f.is_dir()]
    
    print(f"📁 Found {len(avatar_folders)} avatar folders")
    print()
    
    for folder in sorted(avatar_folders):
        folder_name = folder.name
        print(f"\n🐝 Checking: {folder_name}/")
        print("-" * 80)
        
        # Check for model files
        obj_files = list(folder.glob("*.obj"))
        mtl_files = list(folder.glob("*.mtl"))
        texture_files = list(folder.glob("*.png"))
        
        if not obj_files:
            print("   ⚠️  No .obj file found")
            continue
            
        # Check the main model.obj file
        model_obj = folder / "model.obj"
        if model_obj.exists():
            # Read first 50 lines to find comment with original filename
            with open(model_obj, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = [f.readline() for _ in range(50)]
                
            # Look for original filename in comments
            original_name = None
            for line in first_lines:
                if 'mtllib' in line:
                    # Extract MTL filename which often has the original name
                    mtl_match = re.search(r'mtllib\s+(.+\.mtl)', line)
                    if mtl_match:
                        mtl_filename = mtl_match.group(1)
                        original_name = mtl_filename
                        break
            
            # Also check actual OBJ files with original names
            for obj_file in obj_files:
                if obj_file.name != "model.obj":
                    original_name = obj_file.name
                    break
        
        # Check MTL file
        model_mtl = folder / "model.mtl"
        mtl_original_name = None
        if model_mtl.exists():
            with open(model_mtl, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Look for comments or original names
                for line in content.split('\n')[:20]:
                    if '.mtl' in line.lower() and '#' in line:
                        mtl_original_name = line
                        break
        
        # Also check for non-model files that might have original names
        for mtl_file in mtl_files:
            if mtl_file.name != "model.mtl":
                mtl_original_name = mtl_file.name
                break
        
        # Extract avatar ID from any original filename found
        extracted_id = None
        extracted_name = None
        
        if original_name:
            extracted_id, extracted_name = extract_avatar_name_from_filename(original_name)
        elif mtl_original_name:
            extracted_id, extracted_name = extract_avatar_name_from_filename(mtl_original_name)
        
        # Check texture file for clues
        for texture in texture_files:
            if texture.name != "model.png" and texture.name != "texture.png" and texture.name != "thumbnail.png" and texture.name != "preview.png":
                tex_id, tex_name = extract_avatar_name_from_filename(texture.name)
                if not extracted_id:
                    extracted_id = tex_id
                    extracted_name = tex_name
        
        # Compare folder name with extracted name
        if extracted_id and extracted_id != folder_name:
            mismatch = {
                'folder': folder_name,
                'actual_content': extracted_name or extracted_id,
                'extracted_id': extracted_id,
                'evidence': original_name or mtl_original_name or 'texture filename'
            }
            mismatches.append(mismatch)
            print(f"   ❌ MISMATCH DETECTED!")
            print(f"      Folder name: '{folder_name}'")
            print(f"      Actual content: '{extracted_name}' (ID: {extracted_id})")
            print(f"      Evidence from: {mismatch['evidence']}")
        else:
            if extracted_id:
                correct_matches.append(folder_name)
                print(f"   ✅ Correct: {folder_name} = {extracted_id}")
            else:
                print(f"   ⚠️  Could not verify (no original filename found)")
        
        # List files
        print(f"   Files:")
        print(f"      OBJ: {len(obj_files)} file(s) - {', '.join([f.name for f in obj_files])}")
        print(f"      MTL: {len(mtl_files)} file(s) - {', '.join([f.name for f in mtl_files])}")
        print(f"      PNG: {len(texture_files)} file(s)")
    
    # Summary
    print("\n")
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"✅ Correct matches: {len(correct_matches)}")
    print(f"❌ Mismatches found: {len(mismatches)}")
    print()
    
    if mismatches:
        print("🚨 MISMATCHES THAT NEED FIXING:")
        print()
        for i, mismatch in enumerate(mismatches, 1):
            print(f"{i}. Folder: '{mismatch['folder']}'")
            print(f"   → Contains: '{mismatch['actual_content']}'")
            print(f"   → Should be in: '{mismatch['extracted_id']}/' folder")
            print()
        
        print("💡 RECOMMENDED ACTIONS:")
        print()
        for mismatch in mismatches:
            old_folder = mismatch['folder']
            new_folder = mismatch['extracted_id']
            print(f"   mv static/assets/avatars/{old_folder}/ static/assets/avatars/{new_folder}/")
        print()
    else:
        print("✅ No mismatches found! All avatars are correctly named.")
    
    print("=" * 80)

if __name__ == "__main__":
    check_avatar_folders()
