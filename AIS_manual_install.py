#!/usr/bin/env python3
"""
AIS (Avatar Installation System) - Manual Installation Mode
For installing specific new avatars by folder name
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from avatar_catalog import (
    install_new_avatar,
    generate_theme_from_title
)

def install_specific_avatars(folder_names):
    """
    Install specific avatars using AIS (Avatar Installation System)
    
    Args:
        folder_names (list): List of folder names to install
    """
    
    print("🚀 AIS (Avatar Installation System) - Manual Installation Mode")
    print("=" * 70)
    print(f"🎯 Installing {len(folder_names)} specific avatars...")
    
    installed_avatars = []
    
    for folder_name in folder_names:
        print(f"\n📦 AIS Installing: {folder_name}")
        
        # Show what theme would be generated
        display_name = folder_name.replace('_', ' ').replace('-', ' ')
        theme = generate_theme_from_title(display_name)
        
        print(f"   Display Name: {display_name}")
        print(f"   Generated Theme: {theme['ui_style']}")
        print(f"   Primary Color: {theme['primary_color']}")
        print(f"   Personality: {', '.join(theme['personality'])}")
        
        # Attempt installation
        try:
            avatar_config = install_new_avatar(folder_name)
            
            if avatar_config:
                installed_avatars.append(avatar_config)
                print(f"   ✅ Successfully installed {avatar_config['name']}!")
                print(f"   📁 Files validated in folder: {folder_name}")
                print(f"   🎨 Theme applied: {avatar_config['theme']['ui_style']}")
                print(f"   📂 Category: {avatar_config['category']}")
            else:
                print(f"   ❌ Installation failed - folder/files not found")
                
        except Exception as e:
            print(f"   ❌ Installation error: {str(e)}")
    
    print(f"\n🎉 AIS Installation Summary")
    print("=" * 50)
    print(f"✅ Successfully installed: {len(installed_avatars)}/{len(folder_names)} avatars")
    
    if installed_avatars:
        print(f"\n📋 New Avatars Added to Catalog:")
        for i, avatar in enumerate(installed_avatars, 1):
            print(f"   {i}. 🐝 {avatar['name']}")
            print(f"      Theme: {avatar['theme']['ui_style']} ({avatar['theme']['primary_color']})")
            print(f"      Category: {avatar['category']}")
            print(f"      ID: {avatar['id']}")
            print(f"      Folder: {avatar['folder']}")
            print()
    
    return installed_avatars

def demo_new_avatar_themes():
    """Demonstrate themes for the 6 new avatars from screenshot"""
    
    print("🎨 AIS Theme Preview for New Avatars")
    print("=" * 50)
    
    new_avatar_names = [
        "AstroBee",     # Space theme
        "Frankenbee",   # Monster/Halloween theme  
        "WareBee",      # Tech/Software theme
        "ZomBee",       # Monster/Halloween theme
        "VampBee",      # Monster/Vampire theme
        "DetectiveBee"  # Professional/Mystery theme
    ]
    
    for name in new_avatar_names:
        display_name = name.replace('_', ' ').replace('-', ' ')
        theme = generate_theme_from_title(display_name)
        
        print(f"\n🐝 {display_name}")
        print(f"   Theme Style: {theme['ui_style']}")
        print(f"   Colors: {theme['primary_color']} / {theme['secondary_color']}")
        print(f"   Personality: {', '.join(theme['personality'])}")
        print(f"   Keywords: {', '.join(theme['description_keywords'])}")
        print(f"   Animation: {theme['animation_style']}")

if __name__ == "__main__":
    print("🔍 AIS (Avatar Installation System) Ready!")
    print()
    
    # First show theme preview
    demo_new_avatar_themes()
    
    print(f"\n" + "=" * 70)
    print("💡 To install these avatars, ensure folders exist in:")
    print("   static/Avatars/3D Avatar Files/[FolderName]/")
    print("   with required files: .obj, .mtl, .png, and !.png")
    print()
    print("🚀 When folders are ready, run:")
    print("   python -c \"from install_new_avatars_AIS import install_specific_avatars;")
    print("   install_specific_avatars(['AstroBee', 'Frankenbee', 'WareBee', 'ZomBee', 'VampBee', 'DetectiveBee'])\"")
    print()
    
    # Check if folders exist and install if they do
    avatar_files_path = "static/Avatars/3D Avatar Files"
    new_avatars = ["AstroBee", "Frankenbee", "WareBee", "ZomBee", "VampBee", "DetectiveBee"]
    
    existing_new = []
    for avatar in new_avatars:
        folder_path = os.path.join(avatar_files_path, avatar)
        if os.path.exists(folder_path):
            existing_new.append(avatar)
    
    if existing_new:
        print(f"🎯 Found {len(existing_new)} new avatar folders ready for installation!")
        response = input(f"Install {len(existing_new)} avatars now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            install_specific_avatars(existing_new)
    else:
        print("📁 New avatar folders not yet detected in directory.")
        print("   They may need to be copied/synced to the 3D Avatar Files folder first.")