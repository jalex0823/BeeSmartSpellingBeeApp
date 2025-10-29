import os
import sqlite3
from pathlib import Path

# --- Configuration ---
WORKSPACE_ROOT = Path(__file__).parent
DB_PATH = WORKSPACE_ROOT / 'instance' / 'spellbee.db'
AVATARS_ASSETS_PATH = WORKSPACE_ROOT / 'static' / 'assets' / 'avatars'
AVATAR_SLUGS_TO_CHECK = ['astro-bee', 'obee']

def query_db(query, params=()):
    """Executes a query against the SQLite database and returns results."""
    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH}")
        return None
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        columns = [description[0] for description in cur.description]
        con.close()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return None

def check_avatar_files(folder_path, files_to_check):
    """Checks for the existence of files within a specific avatar's asset folder."""
    avatar_folder = AVATARS_ASSETS_PATH / folder_path
    if not avatar_folder.is_dir():
        print(f"  - 📂 Folder: '{avatar_folder.relative_to(WORKSPACE_ROOT)}' (MISSING)")
        return False
    
    print(f"  - 📂 Folder: '{avatar_folder.relative_to(WORKSPACE_ROOT)}' (Exists)")
    all_found = True
    for file_key, filename in files_to_check.items():
        if not filename:
            print(f"    - ✅ {file_key}: (Not set in DB, skipping)")
            continue
        
        file_path = avatar_folder / filename
        if file_path.exists():
            print(f"    - ✅ {file_key}: '{filename}' (Found)")
        else:
            print(f"    - ❌ {file_key}: '{filename}' (MISSING)")
            all_found = False
    return all_found

def main():
    """Main diagnostic function."""
    print("--- Avatar Sanity Check ---")
    
    for slug in AVATAR_SLUGS_TO_CHECK:
        print(f"\n🔍 Checking avatar: '{slug}'")
        
        # 1. Check database record
        avatars_data = query_db("SELECT * FROM avatars WHERE slug = ?", (slug,))
        
        if not avatars_data:
            print(f"  - 📄 DB Record: MISSING. Avatar '{slug}' is not in the database.")
            continue
            
        avatar_data = avatars_data[0]
        print(f"  - 📄 DB Record: Found (ID: {avatar_data['id']}, Name: {avatar_data['name']})")
        
        # 2. Check associated files
        folder = avatar_data.get('folder_path')
        if not folder:
            print("  - 📂 File Check: SKIPPED (folder_path not set in database).")
            continue

        files = {
            'model': avatar_data.get('obj_file'),
            'material': avatar_data.get('mtl_file'),
            'texture': avatar_data.get('texture_file'),
            'thumbnail': avatar_data.get('thumbnail_file')
        }
        
        check_avatar_files(folder, files)

    print("\n--- Sanity Check Complete ---")

if __name__ == "__main__":
    main()
