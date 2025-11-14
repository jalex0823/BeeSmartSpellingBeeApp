#!/usr/bin/env python3
"""
Standardize Avatar Display Names with 'Avatar' Suffix
Purpose: Update all avatar display names to include 'Avatar' suffix for App Store compliance.

Example:
  "Knight Bee" → "Knight Bee Avatar"
  "Astro Bee" → "Astro Bee Avatar"
  "SuperBee" → "SuperBee Avatar"

Why: Apple requires clear naming that reflects what the user receives.
Adding 'Avatar' suffix clarifies this is a character unlock, preventing rejections.

Files updated:
1. avatar_catalog.py - AVATAR_CATALOG display names
2. store/avatar_skus.csv - display_name column
3. BEESMART_PRICING_TABLE.csv - Title column
4. PRICING_TABLE_CORRECTED.csv - Title column
"""

import re
import csv
from pathlib import Path

# Get repo root
REPO_ROOT = Path(__file__).resolve().parent.parent


def add_avatar_suffix(name: str) -> str:
    """Add ' Avatar' suffix to name if not already present."""
    if not name or name.endswith(' Avatar'):
        return name
    return f"{name} Avatar"


def update_avatar_catalog():
    """Update avatar_catalog.py AVATAR_CATALOG names."""
    catalog_path = REPO_ROOT / 'avatar_catalog.py'
    
    print(f"\n📝 Updating {catalog_path.name}...")
    
    with open(catalog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match "name": "Some Name", lines in AVATAR_CATALOG
    pattern = r'(\s+"name":\s+")([^"]+)(",)'
    
    def replace_name(match):
        prefix = match.group(1)
        original_name = match.group(2)
        suffix = match.group(3)
        new_name = add_avatar_suffix(original_name)
        if new_name != original_name:
            print(f"  ✓ {original_name} → {new_name}")
        return f"{prefix}{new_name}{suffix}"
    
    updated_content = re.sub(pattern, replace_name, content)
    
    with open(catalog_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"  ✅ Updated {catalog_path.name}")


def update_avatar_skus_csv():
    """Update store/avatar_skus.csv display_name column."""
    csv_path = REPO_ROOT / 'store' / 'avatar_skus.csv'
    
    if not csv_path.exists():
        print(f"  ⚠️  {csv_path.name} not found, skipping")
        return
    
    print(f"\n📝 Updating {csv_path.name}...")
    
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            original_name = row['display_name']
            new_name = add_avatar_suffix(original_name)
            if new_name != original_name:
                print(f"  ✓ {original_name} → {new_name}")
            row['display_name'] = new_name
            rows.append(row)
    
    # Write back
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"  ✅ Updated {csv_path.name}")


def update_pricing_csv(filename):
    """Update pricing CSV files (Title column for Avatar rows)."""
    csv_path = REPO_ROOT / filename
    
    if not csv_path.exists():
        print(f"  ⚠️  {filename} not found, skipping")
        return
    
    print(f"\n📝 Updating {filename}...")
    
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only update rows where Type is 'Avatar'
            if row.get('Type') == 'Avatar':
                original_title = row['Title']
                new_title = add_avatar_suffix(original_title)
                if new_title != original_title:
                    print(f"  ✓ {original_title} → {new_title}")
                row['Title'] = new_title
            rows.append(row)
    
    # Write back
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"  ✅ Updated {filename}")


def main():
    print("=" * 60)
    print("🐝 BeeSmart Avatar Name Standardization")
    print("=" * 60)
    print("\nAdding ' Avatar' suffix to all avatar display names...")
    print("This ensures App Store Connect compliance.\n")
    
    # Update all files
    update_avatar_catalog()
    update_avatar_skus_csv()
    update_pricing_csv('BEESMART_PRICING_TABLE.csv')
    update_pricing_csv('PRICING_TABLE_CORRECTED.csv')
    
    print("\n" + "=" * 60)
    print("✅ ALL FILES UPDATED SUCCESSFULLY")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Review changes with git diff")
    print("2. Update App Store Connect Display Names:")
    print("   - Keep Product IDs unchanged")
    print("   - Only update Display Name field")
    print("   - Example: 'Astro Bee' → 'Astro Bee Avatar'")
    print("3. Keep Reference Names with Avatar suffix")
    print("   - Example: 'Astro Bee Avatar'")
    print("\n💡 This naming standard:")
    print("   ✓ Tells Apple exactly what it is (character unlock)")
    print("   ✓ Keeps naming consistent across 30+ avatars")
    print("   ✓ Makes App Store browsing clean and readable")
    print("   ✓ Avoids rejection for misleading naming")
    print()


if __name__ == '__main__':
    main()
