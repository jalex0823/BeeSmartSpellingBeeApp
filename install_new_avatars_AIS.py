#!/usr/bin/env python3
"""
AIS (Avatar Installation System) - Install New Avatars
Installing the 6 new avatars discovered in the 3D Avatar Files directory
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from avatar_catalog import (
    install_new_avatar,
    bulk_install_avatars,
    generate_theme_from_title
)

def install_new_avatars():
    """Install the 6 new avatars using AIS (Avatar Installation System)"""
    
    print("🚀 AIS (Avatar Installation System) - Installing New Avatars")
    print("=" * 70)
    
    # The 6 new avatars from the screenshot
    new_avatars = [
        "AstroBee",
        "Frankenbee", 
        "WareBee",
        "ZomBee",
        "VampBee",
        "DetectiveBee",
        "MascotBee",  # This might be existing, but let's check
        "QueenBee"    # This might be existing, but let's check
    ]
    
    # Check which ones are actually new (not in existing catalog)
    existing_avatars = [
        "AlBee", "AnxiousBee", "BikerBee", "BrotherBee", "BuilderBee", 
        "CoolBee", "DivaBee", "DoctorBee", "ExplorerBee", "KnightBee",
        "MascotBee", "MonsterBee", "ProfessorBee", "QueenBee", "RoboBee",
        "RockerBee", "Seabea", "Superbee"
    ]
    
    truly_new_avatars = []
    for avatar in new_avatars:
        if avatar not in existing_avatars:
            truly_new_avatars.append(avatar)
    
    print(f"🎯 Found {len(truly_new_avatars)} new avatars to install:")
    for avatar in truly_new_avatars:
        display_name = avatar.replace('_', ' ').replace('-', ' ')
        theme = generate_theme_from_title(display_name)
        print(f"   • {display_name} ({theme['ui_style']} theme)")
    
    print(f"\n📦 Installing {len(truly_new_avatars)} new avatars using AIS...")
    
    # Install each new avatar
    installed_avatars = []
    for folder_name in truly_new_avatars:
        print(f"\n🔧 AIS Installing: {folder_name}")
        
        avatar_config = install_new_avatar(folder_name)
        
        if avatar_config:
            installed_avatars.append(avatar_config)
            print(f"✅ {avatar_config['name']} installed successfully!")
            print(f"   Theme: {avatar_config['theme']['ui_style']} ({avatar_config['theme']['primary_color']})")
            print(f"   Category: {avatar_config['category']}")
            print(f"   Personality: {', '.join(avatar_config['theme']['personality'])}")
        else:
            print(f"❌ Failed to install {folder_name}")
    
    print(f"\n🎉 AIS Installation Complete!")
    print(f"✅ {len(installed_avatars)}/{len(truly_new_avatars)} avatars installed successfully")
    
    if installed_avatars:
        print(f"\n📋 New Avatar Summary:")
        for avatar in installed_avatars:
            print(f"   🐝 {avatar['name']} - {avatar['theme']['ui_style']} theme - {avatar['category']} category")
    
    return installed_avatars

if __name__ == "__main__":
    # First, let's check what folders actually exist
    avatar_files_path = "static/Avatars/3D Avatar Files"
    
    if os.path.exists(avatar_files_path):
        print("🔍 Checking available avatar folders...")
        folders = [f for f in os.listdir(avatar_files_path) if os.path.isdir(os.path.join(avatar_files_path, f))]
        folders.sort()
        
        print(f"📁 Found {len(folders)} avatar folders:")
        for folder in folders:
            print(f"   • {folder}")
        
        # Check for new ones not in our catalog
        existing_catalog_folders = [
            "AlBee", "AnxiousBee", "BikerBee", "BrotherBee", "BuilderBee", 
            "CoolBee", "DivaBee", "DoctorBee", "ExplorerBee", "KnightBee",
            "MascotBee", "MonsterBee", "ProfessorBee", "QueenBee", "RoboBee",
            "RockerBee", "Seabea", "Superbee"
        ]
        
        new_folders = [f for f in folders if f not in existing_catalog_folders]
        
        if new_folders:
            print(f"\n🆕 Found {len(new_folders)} new avatar folders:")
            for folder in new_folders:
                print(f"   • {folder}")
            
            print(f"\n🚀 Starting AIS installation for {len(new_folders)} new avatars...")
            installed = []
            
            for folder in new_folders:
                print(f"\n📦 AIS Installing: {folder}")
                result = install_new_avatar(folder)
                if result:
                    installed.append(result)
            
            print(f"\n🎉 AIS Installation Summary:")
            print(f"✅ Successfully installed: {len(installed)} avatars")
            
            for avatar in installed:
                print(f"   🐝 {avatar['name']} - {avatar['theme']['ui_style']} theme")
        else:
            print(f"\n💡 No new avatars found. All folders are already in the catalog.")
    else:
        print(f"❌ Avatar files directory not found: {avatar_files_path}")