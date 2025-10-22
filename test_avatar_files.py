#!/usr/bin/env python3
"""
Test avatar loading system and file availability
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_avatar_files():
    """Check if avatar files exist on the filesystem"""
    base_path = os.path.join(os.path.dirname(__file__), 'static')
    
    avatar_paths = [
        '3DFiles/Avatars',
        'models',
        'images/avatars'
    ]
    
    print("🐝 Avatar File System Check")
    print("=" * 50)
    
    for path in avatar_paths:
        full_path = os.path.join(base_path, path)
        exists = os.path.exists(full_path)
        
        print(f"📁 {path}: {'✅ EXISTS' if exists else '❌ MISSING'}")
        
        if exists:
            files = os.listdir(full_path)
            print(f"   📄 Files found: {len(files)}")
            
            # Show first few files as examples
            for i, file in enumerate(files[:3]):
                print(f"      - {file}")
            if len(files) > 3:
                print(f"      ... and {len(files) - 3} more")
        print()
    
    # Check specific critical files
    critical_files = [
        'models/MascotBee_1019174653_texture.obj',
        'models/MascotBee_1019174653_texture.mtl', 
        'models/MascotBee_1019174653_texture.png',
        'BeeSmartBee.png'
    ]
    
    print("🔍 Critical Default Avatar Files")
    print("=" * 50)
    
    for file_path in critical_files:
        full_path = os.path.join(base_path, file_path)
        exists = os.path.exists(full_path)
        
        print(f"{'✅' if exists else '❌'} {file_path}")
        
        if exists:
            size = os.path.getsize(full_path)
            print(f"    Size: {size:,} bytes")

if __name__ == "__main__":
    check_avatar_files()