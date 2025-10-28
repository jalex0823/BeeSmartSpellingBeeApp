#!/usr/bin/env python3
"""
Real Avatar Analysis - Shows actual file data from your avatar files
"""

from pathlib import Path
import json

avatar_base = Path(r"C:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\static\Avatars\3D Avatar Files")

def analyze_avatar(avatar_name):
    """Analyze a single avatar and return real data"""
    avatar_path = avatar_base / avatar_name
    
    if not avatar_path.exists():
        return None
    
    result = {
        "name": avatar_name,
        "files": {},
        "mesh": {
            "vertices": 0,
            "faces": 0,
            "normals": 0,
            "texture_coords": 0
        },
        "materials": [],
        "textures": [],
        "file_sizes": {}
    }
    
    # List all files
    for file in avatar_path.iterdir():
        result["files"][file.name] = str(file.stat().st_size) + " bytes"
        result["file_sizes"][file.name] = file.stat().st_size
    
    # Parse OBJ file
    obj_files = list(avatar_path.glob("*.obj"))
    if obj_files:
        obj_file = obj_files[0]
        try:
            with open(obj_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.startswith('v '):
                        result["mesh"]["vertices"] += 1
                    elif line.startswith('vn '):
                        result["mesh"]["normals"] += 1
                    elif line.startswith('vt '):
                        result["mesh"]["texture_coords"] += 1
                    elif line.startswith('f '):
                        result["mesh"]["faces"] += 1
        except Exception as e:
            result["errors"] = [str(e)]
    
    # Parse MTL file
    mtl_files = list(avatar_path.glob("*.mtl"))
    if mtl_files:
        mtl_file = mtl_files[0]
        try:
            with open(mtl_file, 'r', encoding='utf-8', errors='ignore') as f:
                current_mat = None
                for line in f:
                    if line.startswith('newmtl '):
                        current_mat = line.split(maxsplit=1)[1].strip()
                        result["materials"].append(current_mat)
                    elif line.startswith('map_Kd ') and current_mat:
                        tex_path = line.split(maxsplit=1)[1].strip()
                        result["textures"].append(tex_path)
        except Exception as e:
            pass
    
    return result

# Analyze real avatars
print("=" * 80)
print("REAL AVATAR ANALYSIS")
print("=" * 80)
print()

working_avatars = ["AlBee", "AnxiousBee", "BikerBee"]
broken_avatars = ["BitterBee", "BlissfulBee"]

print("✓ WORKING AVATARS:")
print("-" * 80)
for avatar in working_avatars:
    data = analyze_avatar(avatar)
    if data:
        print(f"\n{avatar}:")
        print(f"  Vertices:  {data['mesh']['vertices']:,}")
        print(f"  Faces:     {data['mesh']['faces']:,}")
        print(f"  Normals:   {data['mesh']['normals']:,}")
        print(f"  Tex Coords: {data['mesh']['texture_coords']:,}")
        print(f"  Materials: {len(data['materials'])}")
        print(f"  Textures:  {len(data['textures'])}")
        print(f"  Files:     {len(data['files'])}")
        print(f"  Total Size: {sum(data['file_sizes'].values()) / 1024 / 1024:.2f} MB")
        if data['materials']:
            print(f"  Materials: {', '.join(data['materials'])}")
        if data['textures']:
            print(f"  Texture Maps: {', '.join(data['textures'])}")

print("\n")
print("✗ BROKEN AVATARS:")
print("-" * 80)
for avatar in broken_avatars:
    data = analyze_avatar(avatar)
    if data:
        print(f"\n{avatar}:")
        print(f"  Vertices:  {data['mesh']['vertices']:,}")
        print(f"  Faces:     {data['mesh']['faces']:,}")
        print(f"  Normals:   {data['mesh']['normals']:,}")
        print(f"  Tex Coords: {data['mesh']['texture_coords']:,}")
        print(f"  Materials: {len(data['materials'])}")
        print(f"  Textures:  {len(data['textures'])}")
        print(f"  Files:     {len(data['files'])}")
        print(f"  Total Size: {sum(data['file_sizes'].values()) / 1024 / 1024:.2f} MB")
        if data['materials']:
            print(f"  Materials: {', '.join(data['materials'])}")
        if data['textures']:
            print(f"  Texture Maps: {', '.join(data['textures'])}")

print("\n")
print("=" * 80)
print("DELTA COMPARISON: AnxiousBee (working) vs BitterBee (broken)")
print("=" * 80)

anxious = analyze_avatar("AnxiousBee")
bitter = analyze_avatar("BitterBee")

if anxious and bitter:
    print(f"\nMesh Geometry:")
    print(f"  Vertices:  {anxious['mesh']['vertices']:,} → {bitter['mesh']['vertices']:,} ({bitter['mesh']['vertices'] - anxious['mesh']['vertices']:+,})")
    print(f"  Faces:     {anxious['mesh']['faces']:,} → {bitter['mesh']['faces']:,} ({bitter['mesh']['faces'] - anxious['mesh']['faces']:+,})")
    print(f"  Normals:   {anxious['mesh']['normals']:,} → {bitter['mesh']['normals']:,} ({bitter['mesh']['normals'] - anxious['mesh']['normals']:+,})")
    print(f"  Tex Coords: {anxious['mesh']['texture_coords']:,} → {bitter['mesh']['texture_coords']:,} ({bitter['mesh']['texture_coords'] - anxious['mesh']['texture_coords']:+,})")
    
    print(f"\nMaterials:")
    print(f"  Count:     {len(anxious['materials'])} → {len(bitter['materials'])}")
    print(f"  Working:   {anxious['materials']}")
    print(f"  Broken:    {bitter['materials']}")
    
    print(f"\nTexture Maps:")
    print(f"  Count:     {len(anxious['textures'])} → {len(bitter['textures'])}")
    print(f"  Working:   {anxious['textures']}")
    print(f"  Broken:    {bitter['textures']}")
    
    print(f"\nFile Count:")
    print(f"  Working:   {len(anxious['files'])} files")
    print(f"  Broken:    {len(bitter['files'])} files")

print("\n")
