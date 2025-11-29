"""
Verify Fairy Bee Avatar Installation
====================================
Checks that Fairy Bee is properly installed with all required files.
"""

import os
from pathlib import Path

def verify_installation():
    print("\n🐝 Fairy Bee Avatar Installation Check")
    print("=" * 60)
    
    checks = {
        "Catalog Entry": False,
        "GLB File": False,
        "Thumbnail": False,
        "Pricing": False
    }
    
    # Check 1: Catalog entry
    try:
        from avatar_catalog import AVATAR_CATALOG, PREMIUM_199_IDS
        fairy = next((a for a in AVATAR_CATALOG if a['id'] == 'fairy-bee'), None)
        if fairy:
            checks["Catalog Entry"] = True
            print("✅ Catalog Entry: Found in AVATAR_CATALOG")
            print(f"   - Name: {fairy['name']}")
            print(f"   - Tier: {fairy['tier']}")
            print(f"   - Price: ${fairy['price']:.2f}")
            print(f"   - Unlock Points: {fairy['unlock_points']:,}")
        else:
            print("❌ Catalog Entry: NOT FOUND in AVATAR_CATALOG")
    except Exception as e:
        print(f"❌ Catalog Entry: Error - {e}")
    
    # Check 2: GLB file
    glb_path = Path("static/assets/avatars/glb_files/FairyBee.glb")
    if glb_path.exists():
        checks["GLB File"] = True
        size_mb = glb_path.stat().st_size / (1024 * 1024)
        print(f"✅ GLB File: Found ({size_mb:.2f} MB)")
    else:
        print(f"❌ GLB File: NOT FOUND at {glb_path}")
        print("   → Place FairyBee.glb in static/assets/avatars/glb_files/")
    
    # Check 3: Thumbnail
    thumb_path = Path("static/assets/avatars/glb_files/AvatarThumbnails/FairyBee!.png")
    if thumb_path.exists():
        checks["Thumbnail"] = True
        from PIL import Image
        img = Image.open(thumb_path)
        print(f"✅ Thumbnail: Found ({img.width}x{img.height})")
    else:
        print(f"❌ Thumbnail: NOT FOUND at {thumb_path}")
        print("   → Create FairyBee!.png in static/assets/avatars/glb_files/AvatarThumbnails/")
    
    # Check 4: Pricing
    try:
        if 'fairy-bee' in PREMIUM_199_IDS:
            checks["Pricing"] = True
            print("✅ Pricing: Added to PREMIUM_199_IDS ($1.99 tier)")
        else:
            print("⚠️ Pricing: Not in PREMIUM_199_IDS (will use default $0.99)")
    except:
        print("❌ Pricing: Could not verify")
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(checks.values())
    total = len(checks)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Fairy Bee is fully installed and ready!")
    else:
        print("\n⚠️ Action Required:")
        for check, status in checks.items():
            if not status:
                print(f"   - {check}")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    verify_installation()
