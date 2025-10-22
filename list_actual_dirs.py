"""
Sync avatar_catalog.py folder names with actual directory structure
"""

import os
from pathlib import Path

# Get all actual avatar directories
AVATAR_BASE_PATH = Path("static/assets/avatars")
actual_dirs = sorted([d.name for d in AVATAR_BASE_PATH.iterdir() if d.is_dir()])

print("=" * 80)
print("🐝 ACTUAL AVATAR DIRECTORIES ON DISK")
print("=" * 80)
for dir_name in actual_dirs:
    print(f"  - {dir_name}")

print(f"\nTotal: {len(actual_dirs)} directories")
print("=" * 80)
