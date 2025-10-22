"""
Generate corrected folder names for avatar_catalog.py
This script will output the necessary replacements
"""

from pathlib import Path
import re

# Get all actual avatar directories
AVATAR_BASE_PATH = Path("static/assets/avatars")
actual_dirs = {d.name: d.name for d in AVATAR_BASE_PATH.iterdir() if d.is_dir()}

# Current catalog folder mappings (PascalCase -> kebab-case)
catalog_fixes = {
    "AlBee": "al-bee",
    "AnxiousBee": "anxious-bee",
    "BikerBee": "biker-bee",
    # "BrotherBee": "brother-bee",  # Already fixed
    "BuilderBee": "builder-bee",
    "CoolBee": "cool-bee",
    "DivaBee": "diva-bee",
    "DoctorBee": "doctor-bee",
    "ExplorerBee": "explorer-bee",
    "KnightBee": "knight-bee",
    "MascotBee": "mascot-bee",
    "MonsterBee": "monster-bee",
    "ProfessorBee": "professor-bee",
    "QueenBee": "queen-bee",
    "RoboBee": "robo-bee",
    "RockerBee": "rocker-bee",
    # "Seabea": "seabea",  # Already correct
    # "superbee": "superbee",  # Already correct
    "AstroBee": "astro-bee",
    "DetectiveBee": "detective-bee",
    "Frankenbee": "franken-bee",
    "VampBee": "vamp-bee",
    "WareBee": "ware-bee",
    "ZomBee": "zom-bee",
}

print("=" * 80)
print("🐝 FOLDER NAME CORRECTIONS NEEDED")
print("=" * 80)

for old_name, new_name in catalog_fixes.items():
    if new_name in actual_dirs:
        print(f"✅ {old_name:20s} → {new_name:20s} (directory exists)")
    else:
        print(f"❌ {old_name:20s} → {new_name:20s} (directory NOT found)")

print("\n" + "=" * 80)
print("📁 DIRECTORIES WITHOUT CATALOG ENTRIES")
print("=" * 80)

catalog_dirs = set(catalog_fixes.values()) | {"brother-bee", "seabea", "superbee"}
for dir_name in sorted(actual_dirs.keys()):
    if dir_name not in catalog_dirs:
        print(f"  - {dir_name}")

print("\n" + "=" * 80)
