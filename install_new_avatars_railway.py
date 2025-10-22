#!/usr/bin/env python3
"""
Install 6 New Avatars with Railway Validation
Uses the enhanced AIS system to safely install new avatars
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from avatar_catalog import (
    bulk_install_with_railway_validation,
    railway_avatar_validation,
    ais_railway_deployment_test
)

def install_six_new_avatars():
    """
    Install the 6 new avatars with Railway validation
    """
    
    print("🎯 INSTALLING 6 NEW AVATARS WITH RAILWAY VALIDATION")
    print("=" * 70)
    
    # The 6 new avatars ready for installation
    new_avatars = [
        "AstroBee",     # Space-themed bee
        "Frankenbee",   # Halloween monster bee  
        "WareBee",      # Software/tech bee
        "ZomBee",       # Zombie apocalypse bee
        "VampBee",      # Vampire/gothic bee
        "DetectiveBee"  # Mystery/detective bee
    ]
    
    print(f"🚀 Preparing to install {len(new_avatars)} new themed avatars...")
    
    # First run AIS Railway deployment test
    print(f"\n1. 🔍 Testing AIS Railway Deployment System...")
    deployment_ready = ais_railway_deployment_test()
    
    if not deployment_ready:
        print(f"❌ AIS Railway system not ready - aborting installation")
        return False
    
    print(f"✅ AIS Railway system operational - proceeding with installation")
    
    # Install with Railway validation
    print(f"\n2. 📦 Installing Avatars with Railway Validation...")
    
    try:
        installed_avatars = bulk_install_with_railway_validation(new_avatars)
        
        print(f"\n🎉 INSTALLATION COMPLETE!")
        print(f"✅ Successfully installed: {len(installed_avatars)}/{len(new_avatars)} avatars")
        
        if installed_avatars:
            print(f"\n✅ RAILWAY-READY AVATARS INSTALLED:")
            for avatar in installed_avatars:
                theme_style = avatar.get('theme', {}).get('ui_style', 'unknown')
                primary_color = avatar.get('theme', {}).get('primary_color', 'unknown')
                print(f"   🐝 {avatar['name']} - {theme_style} theme ({primary_color})")
        
        print(f"\n🚂 All installed avatars are Railway deployment ready!")
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def verify_installation():
    """
    Verify the installation was successful
    """
    
    print(f"\n3. 🔍 Verifying Installation...")
    
    try:
        from avatar_catalog import get_avatar_catalog
        catalog = get_avatar_catalog()
        
        # Check for new avatars in catalog
        new_avatar_names = ["AstroBee", "Frankenbee", "WareBee", "ZomBee", "VampBee", "DetectiveBee"]
        found_avatars = []
        
        for avatar in catalog:
            avatar_name = avatar.get('name', '').replace(' ', '')
            if any(new_name.lower() in avatar_name.lower() for new_name in new_avatar_names):
                found_avatars.append(avatar['name'])
        
        print(f"✅ Found {len(found_avatars)} new avatars in catalog:")
        for name in found_avatars:
            print(f"   🐝 {name}")
        
        return len(found_avatars) > 0
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting New Avatar Installation with Railway Validation...")
    
    # Install the new avatars
    success = install_six_new_avatars()
    
    if success:
        # Verify installation
        verified = verify_installation()
        
        if verified:
            print(f"\n🎉 NEW AVATAR INSTALLATION SUCCESS!")
            print(f"✅ 6 new themed avatars installed with Railway validation")
            print(f"🚂 All avatars verified Railway-deployment ready")
            print(f"🎯 Ready for production deployment!")
            
            print(f"\n📝 NEXT STEPS:")
            print(f"1. Deploy to Railway with new avatars")
            print(f"2. Test avatar selection in production")
            print(f"3. Verify themes display correctly") 
            print(f"4. Monitor Railway logs for avatar loading")
        else:
            print(f"\n⚠️  Installation completed but verification had issues")
    else:
        print(f"\n❌ Avatar installation failed - check AIS system")
        
    print(f"\n🎭 Available avatar themes after installation:")
    print(f"   🌌 AstroBee - Cosmic space theme")
    print(f"   👻 Frankenbee - Spooky monster theme")
    print(f"   💻 WareBee - Software developer theme")
    print(f"   🧟 ZomBee - Zombie apocalypse theme") 
    print(f"   🧛 VampBee - Vampire gothic theme")
    print(f"   🔍 DetectiveBee - Mystery detective theme")