"""
Avatar File Validation Script
Checks all 24 avatars for complete file sets and proper MTL texture references
"""
import os
import re
from pathlib import Path

# Source directory with original files
SOURCE_DIR = Path("Avatars/3D Avatar Files")
# Target directory where they should be deployed
TARGET_DIR = Path("static/assets/avatars")

# Expected avatars (24 total)
EXPECTED_AVATARS = [
    ("AlBee", "al-bee"),
    ("AnxiousBee", "anxious-bee"),
    ("AstroBee", "astro-bee"),
    ("BikerBee", "biker-bee"),
    ("BrotherBee", "brother-bee"),
    ("BuilderBee", "builder-bee"),
    ("CoolBee", "cool-bee"),
    ("DetectiveBee", "detective-bee"),
    ("DivaBee", "diva-bee"),
    ("DoctorBee", "doctor-bee"),
    ("ExplorerBee", "explorer-bee"),
    ("Frankenbee", "franken-bee"),
    ("KnightBee", "knight-bee"),
    ("MascotBee", "mascot-bee"),
    ("MonsterBee", "monster-bee"),
    ("ProfessorBee", "professor-bee"),
    ("QueenBee", "queen-bee"),
    ("RoboBee", "robo-bee"),
    ("RockerBee", "rocker-bee"),
    ("Seabea", "seabea"),
    ("Superbee", "superbee"),
    ("VampBee", "vamp-bee"),
    ("WareBee", "ware-bee"),
    ("ZomBee", "zom-bee"),
]

def check_avatar_files(folder_name, avatar_id):
    """Check if avatar has all required files"""
    results = {
        'folder_name': folder_name,
        'avatar_id': avatar_id,
        'source_exists': False,
        'target_exists': False,
        'files': {},
        'mtl_references': [],
        'issues': []
    }
    
    # Check source directory
    source_path = SOURCE_DIR / folder_name
    target_path = TARGET_DIR / avatar_id
    
    results['source_exists'] = source_path.exists()
    results['target_exists'] = target_path.exists()
    
    if not results['source_exists']:
        results['issues'].append(f"❌ Source folder missing: {source_path}")
        return results
    
    # Expected files
    expected_files = {
        'obj': f"{folder_name}.obj",
        'mtl': f"{folder_name}.mtl",
        'texture': f"{folder_name}.png",
        'thumbnail': f"{folder_name}!.png"
    }
    
    # Check each file in source
    for file_type, filename in expected_files.items():
        source_file = source_path / filename
        target_file = target_path / filename if results['target_exists'] else None
        
        source_exists = source_file.exists()
        source_size = source_file.stat().st_size if source_exists else 0
        target_exists = target_file.exists() if target_file else False
        target_size = target_file.stat().st_size if target_exists else 0
        
        results['files'][file_type] = {
            'filename': filename,
            'source_exists': source_exists,
            'source_size': source_size,
            'target_exists': target_exists,
            'target_size': target_size,
            'source_path': str(source_file),
            'target_path': str(target_file) if target_file else None
        }
        
        # Flag issues
        if not source_exists:
            results['issues'].append(f"❌ Missing {file_type}: {filename}")
        elif source_size < 100:
            results['issues'].append(f"⚠️  Suspiciously small {file_type}: {filename} ({source_size} bytes)")
        elif not target_exists:
            results['issues'].append(f"📋 Not deployed to target: {filename}")
        elif source_size != target_size:
            results['issues'].append(f"⚠️  Size mismatch {file_type}: source={source_size}, target={target_size}")
    
    # Parse MTL file for texture references
    mtl_file = source_path / expected_files['mtl']
    if mtl_file.exists():
        try:
            with open(mtl_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Find map_Kd (diffuse texture) references
                texture_refs = re.findall(r'map_Kd\s+(.+)', content, re.IGNORECASE)
                results['mtl_references'] = texture_refs
                
                # Validate texture references
                for ref in texture_refs:
                    ref = ref.strip()
                    # Check if referenced file exists
                    if ref.startswith('/') or ref.startswith('\\') or ':' in ref:
                        results['issues'].append(f"⚠️  MTL has absolute path: {ref}")
                    else:
                        ref_file = source_path / ref
                        if not ref_file.exists():
                            results['issues'].append(f"❌ MTL references missing file: {ref}")
        except Exception as e:
            results['issues'].append(f"⚠️  Could not parse MTL: {e}")
    
    return results

def format_size(bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"

def main():
    print("="*80)
    print("🐝 BeeSmart Avatar File Validation")
    print("="*80)
    print(f"\nChecking {len(EXPECTED_AVATARS)} avatars...")
    print(f"Source: {SOURCE_DIR}")
    print(f"Target: {TARGET_DIR}")
    print("="*80)
    
    all_results = []
    missing_count = 0
    warning_count = 0
    ok_count = 0
    
    for folder_name, avatar_id in EXPECTED_AVATARS:
        results = check_avatar_files(folder_name, avatar_id)
        all_results.append(results)
        
        # Categorize
        if not results['source_exists']:
            missing_count += 1
            status = "❌ MISSING"
        elif results['issues']:
            warning_count += 1
            status = "⚠️  ISSUES"
        else:
            ok_count += 1
            status = "✅ OK"
        
        print(f"\n{status} {folder_name} → {avatar_id}")
        
        # Show file details
        if results['source_exists']:
            for file_type, info in results['files'].items():
                if info['source_exists']:
                    size_str = format_size(info['source_size'])
                    deployed = "✅" if info['target_exists'] else "📋"
                    print(f"  {deployed} {file_type:10} {info['filename']:25} {size_str:>10}")
            
            # Show MTL references
            if results['mtl_references']:
                print(f"  📄 MTL references: {', '.join(results['mtl_references'])}")
        
        # Show issues
        for issue in results['issues']:
            print(f"  {issue}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Total avatars checked: {len(EXPECTED_AVATARS)}")
    print(f"✅ OK: {ok_count}")
    print(f"⚠️  Issues: {warning_count}")
    print(f"❌ Missing: {missing_count}")
    
    # Detailed issue report
    if warning_count > 0 or missing_count > 0:
        print("\n" + "="*80)
        print("🔍 DETAILED ISSUES")
        print("="*80)
        for results in all_results:
            if results['issues']:
                print(f"\n{results['folder_name']} ({results['avatar_id']}):")
                for issue in results['issues']:
                    print(f"  {issue}")
    
    # Files to copy
    print("\n" + "="*80)
    print("📋 FILES TO DEPLOY")
    print("="*80)
    
    need_copy = []
    for results in all_results:
        if results['source_exists']:
            for file_type, info in results['files'].items():
                if info['source_exists'] and not info['target_exists']:
                    need_copy.append(results)
                    break
    
    if need_copy:
        print(f"\n{len(need_copy)} avatars need to be copied to target directory:")
        for results in need_copy:
            print(f"  📋 {results['folder_name']} → {TARGET_DIR / results['avatar_id']}")
    else:
        print("✅ All avatars already deployed!")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
