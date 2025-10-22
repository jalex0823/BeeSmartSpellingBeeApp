#!/usr/bin/env python3
"""
Railway Avatar Generation Fix
Addresses avatar generation issues specifically for Railway deployment environment
"""

import os
import sys
import traceback
from datetime import datetime

def diagnose_railway_avatar_issues():
    """
    Comprehensive diagnosis of avatar issues on Railway
    """
    
    print("🔧 Railway Avatar Generation Diagnosis")
    print("=" * 60)
    
    issues_found = []
    fixes_applied = []
    
    # Check 1: Import Issues
    print("\n1. 📦 Testing Avatar Catalog Import...")
    try:
        from avatar_catalog import (
            AVATAR_CATALOG, 
            get_avatar_catalog, 
            get_avatar_info,
            validate_avatar,
            generate_theme_from_title
        )
        print("   ✅ Avatar catalog imports successful")
        
        # Test catalog access
        catalog = get_avatar_catalog()
        print(f"   ✅ Avatar catalog loaded: {len(catalog)} avatars")
        
    except ImportError as e:
        issues_found.append(f"Import Error: {e}")
        print(f"   ❌ Import failed: {e}")
    except Exception as e:
        issues_found.append(f"Catalog Error: {e}")
        print(f"   ❌ Catalog access failed: {e}")
    
    # Check 2: File Path Issues
    print("\n2. 📁 Testing File Path Access...")
    try:
        base_path = "static/Avatars/3D Avatar Files"
        avatar_path = os.path.join(base_path, "CoolBee")
        
        print(f"   Testing path: {avatar_path}")
        
        if os.path.exists(base_path):
            print("   ✅ Base avatar directory exists")
        else:
            issues_found.append("Avatar base directory missing")
            print("   ❌ Base avatar directory not found")
        
        if os.path.exists(avatar_path):
            print("   ✅ Sample avatar folder exists")
            
            # Check files
            test_files = ["CoolBee.obj", "CoolBee.mtl", "CoolBee.png", "CoolBee!.png"]
            for file in test_files:
                file_path = os.path.join(avatar_path, file)
                if os.path.exists(file_path):
                    print(f"   ✅ {file} found")
                else:
                    issues_found.append(f"Missing file: {file}")
                    print(f"   ❌ {file} missing")
        else:
            issues_found.append("Sample avatar folder missing")
            print("   ❌ Sample avatar folder not found")
            
    except Exception as e:
        issues_found.append(f"File system error: {e}")
        print(f"   ❌ File system error: {e}")
    
    # Check 3: Avatar API Functions
    print("\n3. 🔧 Testing Avatar API Functions...")
    try:
        # Test get_avatar_info
        avatar_info = get_avatar_info('cool-bee')
        if avatar_info:
            print("   ✅ get_avatar_info() working")
        else:
            issues_found.append("get_avatar_info() returns None")
            print("   ❌ get_avatar_info() failed")
        
        # Test validate_avatar
        is_valid, message = validate_avatar('cool-bee')
        if is_valid:
            print("   ✅ validate_avatar() working")
        else:
            issues_found.append(f"validate_avatar() failed: {message}")
            print(f"   ❌ validate_avatar() failed: {message}")
        
        # Test theme generation
        theme = generate_theme_from_title('Cool Bee')
        if theme and 'ui_style' in theme:
            print("   ✅ generate_theme_from_title() working")
        else:
            issues_found.append("Theme generation failed")
            print("   ❌ Theme generation failed")
            
    except Exception as e:
        issues_found.append(f"API function error: {e}")
        print(f"   ❌ API function error: {e}")
    
    # Check 4: Railway Environment
    print("\n4. 🚂 Railway Environment Check...")
    try:
        # Check environment variables
        railway_env = os.getenv('RAILWAY_ENVIRONMENT')
        if railway_env:
            print(f"   ✅ Railway environment: {railway_env}")
        else:
            print("   ℹ️  Not in Railway environment (local dev)")
        
        # Check current working directory
        cwd = os.getcwd()
        print(f"   📁 Working directory: {cwd}")
        
        # List avatar directory contents if it exists
        if os.path.exists("static/Avatars"):
            contents = os.listdir("static/Avatars")
            print(f"   📂 Avatar directory contents: {contents}")
            
            if "3D Avatar Files" in contents:
                avatar_folders = os.listdir("static/Avatars/3D Avatar Files")
                print(f"   📂 Avatar folders: {len(avatar_folders)} found")
                for folder in avatar_folders[:5]:  # Show first 5
                    print(f"       • {folder}")
                if len(avatar_folders) > 5:
                    print(f"       ... and {len(avatar_folders) - 5} more")
            else:
                issues_found.append("3D Avatar Files subdirectory missing")
                print("   ❌ 3D Avatar Files subdirectory not found")
        else:
            issues_found.append("static/Avatars directory missing")
            print("   ❌ static/Avatars directory not found")
    
    except Exception as e:
        issues_found.append(f"Environment check error: {e}")
        print(f"   ❌ Environment check error: {e}")
    
    # Summary and Recommendations
    print("\n" + "=" * 60)
    print("📊 RAILWAY AVATAR DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if not issues_found:
        print("🎉 NO ISSUES FOUND!")
        print("   Avatar generation should be working properly.")
        return True
    else:
        print(f"❌ {len(issues_found)} ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print("\n💡 RECOMMENDED FIXES:")
        
        if any("Import" in issue for issue in issues_found):
            print("   • Check Python path and module imports")
            print("   • Ensure avatar_catalog.py is in the same directory")
        
        if any("directory" in issue or "folder" in issue for issue in issues_found):
            print("   • Verify static/Avatars/3D Avatar Files directory exists")
            print("   • Check Railway deployment includes avatar assets")
            print("   • Ensure proper file permissions on Railway")
        
        if any("file" in issue.lower() for issue in issues_found):
            print("   • Upload missing avatar files (.obj, .mtl, .png)")
            print("   • Check file naming conventions (case sensitivity)")
        
        if any("API" in issue for issue in issues_found):
            print("   • Add error handling to avatar API endpoints")
            print("   • Implement fallback avatar loading")
        
        return False

def create_railway_avatar_fix():
    """
    Create a robust Railway-compatible avatar system
    """
    
    fix_content = '''
# Railway Avatar Generation Fix
# Add this to your AjaSpellBApp.py to handle Railway deployment issues

import os
import logging
from functools import wraps

# Setup logging for Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def railway_safe_avatar(func):
    """Decorator to make avatar functions Railway-safe"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ImportError as e:
            logger.error(f"Avatar import error: {e}")
            return None
        except FileNotFoundError as e:
            logger.error(f"Avatar file not found: {e}")
            return None
        except Exception as e:
            logger.error(f"Avatar error: {e}")
            return None
    return wrapper

@railway_safe_avatar
def safe_get_avatar_catalog():
    """Railway-safe avatar catalog getter"""
    try:
        from avatar_catalog import get_avatar_catalog
        return get_avatar_catalog()
    except:
        # Fallback minimal catalog
        return [
            {
                "id": "cool-bee",
                "name": "Cool Bee",
                "folder": "CoolBee",
                "description": "A cool bee avatar",
                "variants": ["default"],
                "category": "classic"
            }
        ]

@railway_safe_avatar  
def safe_get_avatar_info(avatar_id, variant='default'):
    """Railway-safe avatar info getter"""
    try:
        from avatar_catalog import get_avatar_info
        return get_avatar_info(avatar_id, variant)
    except:
        # Fallback avatar info
        if avatar_id == "cool-bee":
            return {
                "id": "cool-bee",
                "name": "Cool Bee", 
                "folder": "CoolBee",
                "description": "Default avatar",
                "category": "classic"
            }
        return None

# Add error handling to existing avatar routes
# Replace your existing /api/avatars route with this:
@app.route("/api/avatars", methods=["GET"])
def api_get_avatars_safe():
    """Railway-safe avatar catalog API"""
    try:
        avatars = safe_get_avatar_catalog()
        if not avatars:
            # Return minimal fallback
            avatars = [{
                "id": "cool-bee",
                "name": "Cool Bee",
                "description": "Default avatar",
                "category": "classic"
            }]
        
        return jsonify({
            'status': 'success',
            'avatars': avatars,
            'total': len(avatars),
            'environment': 'railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'local'
        })
    
    except Exception as e:
        logger.error(f"Avatar API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Avatar system temporarily unavailable',
            'fallback': True
        }), 500
    '''
    
    print("\n🔧 RAILWAY AVATAR FIX GENERATED")
    print("=" * 50)
    print("Add the above code to your AjaSpellBApp.py to handle Railway issues.")
    
    return fix_content

if __name__ == "__main__":
    # Run diagnosis
    success = diagnose_railway_avatar_issues()
    
    if not success:
        print(f"\n🔧 Generating Railway-specific fix...")
        fix = create_railway_avatar_fix()
        
        # Save fix to file
        with open("railway_avatar_fix.py", "w") as f:
            f.write(fix)
        
        print(f"\n💾 Railway fix saved to: railway_avatar_fix.py")
    
    print(f"\n✅ Railway Avatar Diagnosis Complete!")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")