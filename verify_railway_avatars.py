#!/usr/bin/env python3
"""
Verify Railway avatar fixes - Check if OBJ/MTL files are loading correctly
"""
import requests
import sys

# Base URL for Railway deployment
BASE_URL = "https://beesmart.up.railway.app"

# 15 avatars that were broken (should now be fixed)
FIXED_AVATARS = {
    'astro-bee': 'AstroBee',
    'biker-bee': 'BikerBee',
    'brother-bee': 'BrotherBee',
    'builder-bee': 'BuilderBee',
    'cool-bee': 'CoolBee',
    'detective-bee': 'DetectiveBee',
    'diva-bee': 'DivaBee',
    'doctor-bee': 'DoctorBee',
    'explorer-bee': 'ExplorerBee',
    'franken-bee': 'FrankenBee',
    'knight-bee': 'KnightBee',
    'queen-bee': 'QueenBee',
    'robo-bee': 'RoboBee',
    'seabea': 'SeaBea',
    'superbee': 'SuperBee'
}

def verify_avatar_files():
    """Check if OBJ and MTL files are accessible (200 OK)"""
    print("🔍 Verifying Railway Avatar Files...")
    print(f"🌐 Base URL: {BASE_URL}\n")
    
    success_count = 0
    error_count = 0
    
    for slug, simple_name in FIXED_AVATARS.items():
        print(f"📝 Testing {slug} ({simple_name})...")
        
        # Test OBJ file
        obj_url = f"{BASE_URL}/static/assets/avatars/{slug}/{simple_name}.obj"
        try:
            obj_response = requests.head(obj_url, timeout=5)
            if obj_response.status_code == 200:
                print(f"   ✅ OBJ: {simple_name}.obj (200 OK)")
                success_count += 1
            else:
                print(f"   ❌ OBJ: {simple_name}.obj ({obj_response.status_code})")
                error_count += 1
        except Exception as e:
            print(f"   ❌ OBJ: Error - {e}")
            error_count += 1
        
        # Test MTL file
        mtl_url = f"{BASE_URL}/static/assets/avatars/{slug}/{simple_name}.mtl"
        try:
            mtl_response = requests.head(mtl_url, timeout=5)
            if mtl_response.status_code == 200:
                print(f"   ✅ MTL: {simple_name}.mtl (200 OK)")
                success_count += 1
            else:
                print(f"   ❌ MTL: {simple_name}.mtl ({mtl_response.status_code})")
                error_count += 1
        except Exception as e:
            print(f"   ❌ MTL: Error - {e}")
            error_count += 1
        
        print()
    
    # Summary
    total_files = len(FIXED_AVATARS) * 2  # OBJ + MTL for each avatar
    print(f"\n{'='*60}")
    print(f"📊 Verification Results:")
    print(f"   ✅ Success: {success_count}/{total_files} files")
    print(f"   ❌ Errors:  {error_count}/{total_files} files")
    print(f"{'='*60}")
    
    if error_count == 0:
        print("\n🎉 All avatar files are accessible!")
        print("   Database fix was successful!")
        return 0
    else:
        print(f"\n⚠️  {error_count} files still have issues")
        print("   Check Railway logs for database update status")
        return 1

if __name__ == "__main__":
    sys.exit(verify_avatar_files())
