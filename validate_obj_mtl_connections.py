"""
OBJ/MTL/Texture Connection Validator
Checks if OBJ files properly reference MTL files and if MTL files reference correct textures
"""

import os
import re

def validate_avatar_connections(avatar_folder, verbose=True):
    """
    Validate that OBJ -> MTL -> Texture connections are correct
    """
    folder_path = os.path.join('static', 'assets', 'avatars', avatar_folder)
    
    print(f"\n{'='*70}")
    print(f"🔍 VALIDATING: {avatar_folder}")
    print(f"{'='*70}\n")
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        return False
    
    # Find all files
    files = os.listdir(folder_path)
    obj_files = [f for f in files if f.endswith('.obj')]
    mtl_files = [f for f in files if f.endswith('.mtl')]
    texture_files = [f for f in files if f.endswith('.png') and '!' not in f]  # Exclude thumbnails
    
    print(f"📁 Files found:")
    print(f"   OBJ files: {obj_files}")
    print(f"   MTL files: {mtl_files}")
    print(f"   Texture files: {texture_files}")
    
    if not obj_files:
        print(f"\n❌ No OBJ file found!")
        return False
    
    if not mtl_files:
        print(f"\n❌ No MTL file found!")
        return False
        
    if not texture_files:
        print(f"\n❌ No texture file found!")
        return False
    
    # Use first OBJ file
    obj_file = obj_files[0]
    obj_path = os.path.join(folder_path, obj_file)
    
    print(f"\n{'='*70}")
    print(f"📄 STEP 1: Check OBJ file references")
    print(f"{'='*70}")
    print(f"Reading: {obj_file}")
    
    # Read OBJ file and look for mtllib reference
    mtl_references = []
    usemtl_references = []
    obj_line_count = 0
    
    with open(obj_path, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            obj_line_count = i
            line = line.strip()
            
            # Check for mtllib (material library reference)
            if line.startswith('mtllib '):
                mtl_ref = line.split('mtllib ')[1].strip()
                mtl_references.append((i, mtl_ref))
                if verbose:
                    print(f"   Line {i}: mtllib {mtl_ref}")
            
            # Check for usemtl (material usage)
            if line.startswith('usemtl '):
                mtl_name = line.split('usemtl ')[1].strip()
                usemtl_references.append((i, mtl_name))
                if verbose and i <= 100:  # Only show first few
                    print(f"   Line {i}: usemtl {mtl_name}")
            
            # Stop reading after first 1000 lines for performance
            if i > 1000 and mtl_references:
                break
    
    print(f"\n   Total lines in OBJ: ~{obj_line_count:,}")
    print(f"   MTL library references found: {len(mtl_references)}")
    print(f"   Material usage (usemtl) found: {len(usemtl_references)}")
    
    if not mtl_references:
        print(f"\n❌ CRITICAL: OBJ file does NOT reference any MTL file!")
        print(f"   Expected line like: mtllib {mtl_files[0]}")
        return False
    
    # Check if referenced MTL file exists
    referenced_mtl = mtl_references[0][1]
    referenced_mtl_path = os.path.join(folder_path, referenced_mtl)
    
    if referenced_mtl not in mtl_files:
        print(f"\n⚠️  WARNING: OBJ references '{referenced_mtl}' but file not found!")
        print(f"   Available MTL files: {mtl_files}")
        print(f"   This WILL cause rendering failure!")
        return False
    else:
        print(f"\n✅ OBJ correctly references: {referenced_mtl}")
    
    # Now check MTL file
    print(f"\n{'='*70}")
    print(f"📄 STEP 2: Check MTL file references")
    print(f"{'='*70}")
    print(f"Reading: {referenced_mtl}")
    
    texture_references = []
    materials_defined = []
    
    with open(referenced_mtl_path, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            
            # Check for material definitions
            if line.startswith('newmtl '):
                mat_name = line.split('newmtl ')[1].strip()
                materials_defined.append((i, mat_name))
                print(f"   Line {i}: newmtl {mat_name}")
            
            # Check for texture map references
            if line.startswith('map_Kd '):
                tex_ref = line.split('map_Kd ')[1].strip()
                texture_references.append((i, tex_ref))
                print(f"   Line {i}: map_Kd {tex_ref}")
            
            # Also check for other texture types
            if line.startswith('map_Ka '):
                tex_ref = line.split('map_Ka ')[1].strip()
                print(f"   Line {i}: map_Ka {tex_ref} (ambient)")
            
            if line.startswith('map_Ks '):
                tex_ref = line.split('map_Ks ')[1].strip()
                print(f"   Line {i}: map_Ks {tex_ref} (specular)")
    
    print(f"\n   Materials defined: {len(materials_defined)}")
    print(f"   Texture references (map_Kd): {len(texture_references)}")
    
    if not materials_defined:
        print(f"\n⚠️  WARNING: No materials defined in MTL file!")
        return False
    
    if not texture_references:
        print(f"\n⚠️  WARNING: No texture map (map_Kd) defined in MTL file!")
        print(f"   Model will render without textures (plain color only)")
        return False
    
    # Check if referenced texture exists
    referenced_texture = texture_references[0][1]
    
    if referenced_texture not in texture_files:
        print(f"\n❌ CRITICAL: MTL references texture '{referenced_texture}' but file not found!")
        print(f"   Available texture files: {texture_files}")
        print(f"   This WILL cause texture loading failure!")
        return False
    else:
        print(f"\n✅ MTL correctly references texture: {referenced_texture}")
    
    # Verify material names match
    print(f"\n{'='*70}")
    print(f"📄 STEP 3: Cross-validate material names")
    print(f"{'='*70}")
    
    mtl_material_names = [mat[1] for mat in materials_defined]
    obj_material_names = list(set([mat[1] for mat in usemtl_references]))
    
    print(f"Materials defined in MTL: {mtl_material_names}")
    print(f"Materials used in OBJ: {obj_material_names[:5]}{'...' if len(obj_material_names) > 5 else ''}")
    
    # Check if OBJ uses materials that are defined in MTL
    missing_materials = [m for m in obj_material_names if m not in mtl_material_names]
    
    if missing_materials:
        print(f"\n⚠️  WARNING: OBJ uses materials not defined in MTL:")
        for mat in missing_materials[:5]:
            print(f"   - {mat}")
        print(f"   This may cause rendering issues!")
    else:
        print(f"\n✅ All OBJ materials are defined in MTL")
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"📊 VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"✅ OBJ file: {obj_file} ({os.path.getsize(obj_path):,} bytes)")
    print(f"✅ MTL file: {referenced_mtl} ({os.path.getsize(referenced_mtl_path):,} bytes)")
    print(f"✅ Texture: {referenced_texture} ({os.path.getsize(os.path.join(folder_path, referenced_texture)):,} bytes)")
    print(f"\n🔗 Connection chain:")
    print(f"   {obj_file} → (mtllib) → {referenced_mtl} → (map_Kd) → {referenced_texture}")
    
    if missing_materials:
        print(f"\n⚠️  Status: PARTIAL SUCCESS (material name mismatch)")
        return True
    else:
        print(f"\n✅ Status: ALL CONNECTIONS VALID")
        return True

def compare_two_avatars(working_folder, failing_folder):
    """Compare working vs failing avatar"""
    print(f"\n{'#'*70}")
    print(f"🔬 COMPARING AVATARS")
    print(f"{'#'*70}")
    
    print(f"\n📗 WORKING AVATAR: {working_folder}")
    working_valid = validate_avatar_connections(working_folder, verbose=False)
    
    print(f"\n📕 FAILING AVATAR: {failing_folder}")
    failing_valid = validate_avatar_connections(failing_folder, verbose=True)
    
    print(f"\n{'#'*70}")
    print(f"COMPARISON RESULT")
    print(f"{'#'*70}")
    print(f"Working avatar ({working_folder}): {'✅ VALID' if working_valid else '❌ INVALID'}")
    print(f"Failing avatar ({failing_folder}): {'✅ VALID' if failing_valid else '❌ INVALID'}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 2:
        # Single avatar validation
        avatar_folder = sys.argv[1]
        validate_avatar_connections(avatar_folder)
    elif len(sys.argv) == 3:
        # Compare two avatars
        working = sys.argv[1]
        failing = sys.argv[2]
        compare_two_avatars(working, failing)
    else:
        # Default: validate knight-bee (one of the non-working ones)
        print("🔧 Validating Knight Bee OBJ/MTL/Texture connections...")
        validate_avatar_connections('beeknight')
