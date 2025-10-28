#!/usr/bin/env python3
"""
Avatar Migration Tool: OBJ to GLB Conversion
Helps manage the transition from broken OBJ avatars to GLB models
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

AVATARS_PATH = Path("static/assets/avatars")

# 9 Working OBJ-based avatars (NO MIGRATION NEEDED - these work!)
# This list is now just for reference/documentation purposes
WORKING_AVATARS = [
    "al-bee",           # Al Bee
    "anxious-bee",      # Anxious Bee
    "mascot-bee",       # Mascot Bee
    "monster-bee",      # Monster Bee
    "professor-bee",    # Professor Bee
    "rocker-bee",       # Rocker Bee
    "vamp-bee",         # Vamp Bee
    "ware-bee",         # Ware Bee
    "zom-bee",          # Zom Bee
]

# Broken avatars that have been REMOVED (for reference only)
# These rendered as white blobs and have been deleted from the system
REMOVED_AVATARS = [
    "builder-bee",           # Builder Bee - REMOVED
    "buzzbot-bee",           # Buzzbot Bee - REMOVED
    "buzzhero-bee",          # Buzzhero Bee - REMOVED
    "detective-bee",         # Detective Bee - REMOVED
    "doctor-bee",            # Doctor Bee - REMOVED
    "explorer-bee",          # Explorer Bee - REMOVED
    "franken-bee",           # Franken Bee - REMOVED
    "knight-bee",            # Knight Bee - REMOVED
    "motorcyclebuzz-bee",    # Motorcyclebuzz Bee - REMOVED
    "queen-bee",             # Queen Bee Majesty - REMOVED
    "sea-bee",               # Sea Bee - REMOVED
    "space-bee",             # Space Bee Explorer - REMOVED
    "super-bee",             # Super Bee Hero - REMOVED
    "bee-diva",              # Bee Diva - REMOVED
]

def create_backup():
    """Create backup of current avatars folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"avatars_backup_{timestamp}"
    backup_path = Path("backups") / backup_name
    
    print(f"\n📦 Creating backup: {backup_path}")
    if AVATARS_PATH.exists():
        shutil.copytree(AVATARS_PATH, backup_path, dirs_exist_ok=True)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    else:
        print(f"❌ Avatar path not found: {AVATARS_PATH}")
        return None

def analyze_avatars():
    """Analyze current avatar folder structure"""
    print("\n" + "="*70)
    print("AVATAR STRUCTURE ANALYSIS")
    print("="*70)
    
    analysis = {
        "total_folders": 0,
        "to_migrate": [],
        "working": [],
        "problematic": []
    }
    
    if not AVATARS_PATH.exists():
        print(f"❌ Path not found: {AVATARS_PATH}")
        return analysis
    
    for folder in sorted(AVATARS_PATH.iterdir()):
        if not folder.is_dir():
            continue
        
        analysis["total_folders"] += 1
        files = list(folder.glob("*"))
        file_names = [f.name for f in files]
        
        # Check file types
        has_obj = any(f.endswith('.obj') for f in file_names)
        has_mtl = any(f.endswith('.mtl') for f in file_names)
        has_glb = any(f.endswith('.glb') for f in file_names)
        has_texture = any(f.endswith('.png') and 'texture' not in f for f in file_names)
        
        folder_name = folder.name
        
        # Categorize - all current avatars are working OBJ-based models
        if folder_name in WORKING_AVATARS:
            status = "� WORKING OBJ"
            analysis["working"].append(folder_name)
        elif folder_name in REMOVED_AVATARS:
            status = "🔴 SHOULD BE REMOVED"
            analysis["problematic"].append(folder_name)
        elif has_glb:
            status = "� GLB FORMAT"
            analysis["working"].append(folder_name)
        elif has_obj and has_mtl:
            status = "⚠️ UNKNOWN OBJ"
            analysis["problematic"].append(folder_name)
        else:
            status = "❌ INCOMPLETE"
            analysis["problematic"].append(folder_name)
        
        print(f"\n{status}")
        print(f"  Folder: {folder_name}")
        print(f"    Files: {len(files)}")
        print(f"    OBJ: {has_obj}, MTL: {has_mtl}, GLB: {has_glb}, PNG: {has_texture}")
        if files:
            print(f"    Contents: {', '.join([f.name for f in files[:5]])}")
            if len(files) > 5:
                print(f"             ... and {len(files)-5} more")
    
    print("\n" + "="*70)
    print(f"SUMMARY: {analysis['total_folders']} total folders")
    print(f"  To Migrate: {len(analysis['to_migrate'])}")
    print(f"  Working: {len(analysis['working'])}")
    print(f"  Problematic: {len(analysis['problematic'])}")
    print("="*70 + "\n")
    
    return analysis

def list_files_to_delete():
    """Show which files should be deleted (broken avatar folders)"""
    print("\n" + "="*70)
    print("FOLDERS TO DELETE (Broken Avatars)")
    print("="*70)
    
    deletion_plan = {}
    total_folders = 0
    
    for avatar in REMOVED_AVATARS:
        avatar_path = AVATARS_PATH / avatar
        if not avatar_path.exists():
            print(f"\n✅ {avatar}: Already removed")
            continue
        
        all_files = list(avatar_path.glob("*"))
        
        if all_files:
            deletion_plan[avatar] = {
                "files": [f.name for f in all_files],
                "count": len(all_files)
            }
            total_folders += 1
        
        if all_files:
            deletion_plan[avatar] = {
                "files": [f.name for f in all_files],
                "count": len(all_files)
            }
            total_folders += 1
            
            print(f"\n🗑️ {avatar}/ ({len(all_files)} files)")
            for file in all_files[:5]:
                print(f"   DELETE: {file.name}")
            if len(all_files) > 5:
                print(f"   ... and {len(all_files) - 5} more files")
    
    print(f"\n{'='*70}")
    print(f"TOTAL TO DELETE: {total_folders} avatar folders")
    print(f"{'='*70}\n")
    
    return deletion_plan

def show_migration_steps():
    """Display step-by-step migration process"""
    print("\n" + "="*70)
    print("MIGRATION STEPS")
    print("="*70)
    
    steps = [
        ("1. BACKUP", "Create backup of current avatars (DONE above)"),
        ("2. VERIFY", "Confirm you have all GLB files ready before deletion"),
        ("3. DELETE OBJ/MTL", "Remove old non-working files from 14 folders"),
        ("4. ADD GLB FILES", "Place new GLB files in each folder"),
        ("5. UPDATE CODE", "Modify quiz.html to support GLB loading"),
        ("6. TEST LOCALLY", "Test each avatar loads correctly"),
        ("7. GIT COMMIT", "Commit changes: 'Replace OBJ avatars with GLB models'"),
        ("8. DEPLOY", "Push to Railway and test in production"),
        ("9. MONITOR", "Watch for errors, rollback if needed"),
    ]
    
    for step, description in steps:
        print(f"\n{step}")
        print(f"  → {description}")
    
    print(f"\n{'='*70}\n")

def generate_cleanup_script():
    """Generate PowerShell script for file deletion"""
    script = """# PowerShell script to delete OBJ/MTL files from migration targets
# Run this ONLY after you have verified GLB files are in place

# Avatar folders with non-working OBJ files
$avatars = @(
    "beedoctor", "beeknight", "builderbee", "buzzbotbee", "buzzhero",
    "detectivebee", "explorerbee", "frankenbee", "motorcyclebuzzbee",
    "queenbeemajesty", "spacebeeexplorer", "superbeehero", "seabee"
)

$basePath = "static\\assets\\avatars"

foreach ($avatar in $avatars) {
    $folder = Join-Path $basePath $avatar
    if (Test-Path $folder) {
        Write-Host "Processing: $avatar"
        
        # Delete OBJ files
        Get-ChildItem $folder -Filter "*.obj" | Remove-Item -Force -Verbose
        
        # Delete MTL files  
        Get-ChildItem $folder -Filter "*.mtl" | Remove-Item -Force -Verbose
        
        Write-Host "✅ Cleaned: $avatar`n"
    } else {
        Write-Host "⚠️ Folder not found: $folder`n"
    }
}

Write-Host "Cleanup complete!"
"""
    
    script_path = Path("cleanup_obj_files.ps1")
    with open(script_path, 'w') as f:
        f.write(script)
    
    print(f"\n✅ Generated cleanup script: {script_path}")
    print(f"   Use this ONLY after placing all GLB files\n")
    return script_path

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🐝 BEESMART AVATAR MIGRATION TOOL")
    print("OBJ to GLB Conversion Helper")
    print("="*70)
    
    # Step 1: Analyze current state
    analysis = analyze_avatars()
    
    # Step 2: Show what will be deleted
    deletion_plan = list_files_to_delete()
    
    # Step 3: Show migration steps
    show_migration_steps()
    
    # Step 4: Offer to create backup
    user_input = input("Create backup of current avatars? (yes/no): ").strip().lower()
    if user_input in ['yes', 'y']:
        backup_path = create_backup()
    
    # Step 5: Generate cleanup script
    user_input = input("Generate PowerShell cleanup script? (yes/no): ").strip().lower()
    if user_input in ['yes', 'y']:
        generate_cleanup_script()
        print("\n⚠️ IMPORTANT: Only run cleanup script AFTER placing all GLB files!")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("1. Place GLB files in each avatar folder")
    print("2. Update Three.js loader to support GLB")
    print("3. Test locally")
    print("4. Run cleanup script")
    print("5. Commit and deploy")
    print("="*70 + "\n")
