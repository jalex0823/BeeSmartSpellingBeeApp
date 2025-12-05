"""
Quiz Diagnostic Tool - Check for common quiz issues
"""

import os
import json
from pathlib import Path

def check_quiz_files():
    """Check if all required quiz files exist and are accessible"""
    print("=" * 70)
    print("🔍 QUIZ FILE DIAGNOSTIC")
    print("=" * 70)
    
    issues_found = []
    
    # Check templates
    quiz_template = Path("templates/quiz.html")
    if not quiz_template.exists():
        issues_found.append("❌ Missing quiz.html template")
    else:
        print(f"✅ Quiz template found: {quiz_template}")
        # Check file size
        size = quiz_template.stat().st_size
        print(f"   File size: {size:,} bytes ({size / 1024:.1f} KB)")
        if size == 0:
            issues_found.append("❌ Quiz template is empty!")
    
    # Check main app file
    app_file = Path("AjaSpellBApp.py")
    if not app_file.exists():
        issues_found.append("❌ Missing AjaSpellBApp.py")
    else:
        print(f"✅ Main app found: {app_file}")
    
    # Check for quiz routes
    if app_file.exists():
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            routes = [
                ('/quiz', '@app.route("/quiz"'),
                ('/api/next', '@app.route(\'/api/next\''),
                ('/api/answer', '@app.route("/api/answer"'),
            ]
            for route_name, route_pattern in routes:
                if route_pattern in content:
                    print(f"✅ Route found: {route_name}")
                else:
                    issues_found.append(f"❌ Missing route: {route_name}")
    
    # Check static files
    static_files = [
        "static/css/BeeSmart.css",
        "static/js/avatar-intro-fx.js",
    ]
    
    for static_file in static_files:
        path = Path(static_file)
        if path.exists():
            print(f"✅ Static file found: {static_file}")
        else:
            print(f"⚠️ Optional file missing: {static_file}")
    
    print("\n" + "=" * 70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    if issues_found:
        print(f"\n❌ {len(issues_found)} CRITICAL ISSUES FOUND:")
        for issue in issues_found:
            print(f"   {issue}")
        print("\n⚠️ These issues may prevent the quiz from working properly.")
    else:
        print("\n✅ All critical files found. Quiz structure appears intact.")
        print("\n💡 If quiz is still malfunctioning, check:")
        print("   1. Browser console for JavaScript errors (F12)")
        print("   2. Server logs for Python exceptions")
        print("   3. Network tab for failed API calls (F12 > Network)")
        print("   4. Session/cookie issues (try clearing browser data)")
        print("   5. Database connectivity (if using Railway)")
    
    return len(issues_found) == 0


def check_common_quiz_issues():
    """Check for common quiz configuration issues"""
    print("\n" + "=" * 70)
    print("🔧 CHECKING COMMON QUIZ ISSUES")
    print("=" * 70)
    
    issues = []
    
    # Check if there's a data directory for dictionary cache
    data_dir = Path("data")
    if not data_dir.exists():
        print("⚠️ 'data' directory not found - dictionary cache may not work")
        issues.append("Create 'data' directory for dictionary caching")
    else:
        print(f"✅ Data directory exists: {data_dir}")
        
        # Check dictionary cache
        dict_cache = data_dir / "dictionary.json"
        if dict_cache.exists():
            print(f"✅ Dictionary cache found: {dict_cache}")
            try:
                with open(dict_cache, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    print(f"   Cached definitions: {len(cache)}")
            except Exception as e:
                issues.append(f"Dictionary cache corrupted: {e}")
        else:
            print("ℹ️ Dictionary cache not yet created (will be generated on first use)")
    
    # Check for temp/upload directory
    upload_dir = Path("uploads")
    if upload_dir.exists():
        print(f"✅ Uploads directory exists: {upload_dir}")
    else:
        print("ℹ️ Uploads directory not found (will be created when needed)")
    
    if issues:
        print(f"\n⚠️ {len(issues)} potential issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ No common issues detected")
    
    return len(issues) == 0


if __name__ == "__main__":
    print("\n🐝 BeeSmart Quiz Diagnostic Tool\n")
    
    files_ok = check_quiz_files()
    config_ok = check_common_quiz_issues()
    
    print("\n" + "=" * 70)
    print("🎯 FINAL VERDICT")
    print("=" * 70)
    
    if files_ok and config_ok:
        print("\n✅ Quiz appears to be properly configured!")
        print("\n📋 Next steps if quiz still doesn't work:")
        print("   1. Start the Flask app: python AjaSpellBApp.py")
        print("   2. Open browser and go to: http://localhost:5000/quiz")
        print("   3. Open browser console (F12) and check for errors")
        print("   4. Check terminal/server logs for Python errors")
        print("   5. Provide specific error messages for targeted help")
    else:
        print("\n⚠️ Issues detected that may affect quiz functionality")
        print("   Please address the issues listed above.")
    
    print("\n" + "=" * 70 + "\n")
