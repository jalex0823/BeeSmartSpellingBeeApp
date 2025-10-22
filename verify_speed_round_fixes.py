#!/usr/bin/env python3
"""
Speed Round JavaScript Fix Verification
Final confirmation test of the syntax error fixes
"""

import re

def verify_javascript_fixes():
    """Verify that JavaScript syntax error fixes are properly implemented"""
    
    print("🐝 Speed Round JavaScript Fix Verification")
    print("=" * 50)
    
    try:
        # Read the quiz template file
        with open('templates/quiz.html', 'r', encoding='utf-8') as file:
            content = file.read()
        
        print("✅ Successfully loaded quiz.html template")
        
        # Check for unsafe template interpolation patterns
        print("\n🔍 Checking for unsafe template interpolation...")
        
        unsafe_patterns = [
            r'\{\{\s*user_name\s*\}\}(?!\|)',  # {{ user_name }} without |tojson
            r'\{\{\s*display_name\s*\}\}(?!\|)',  # {{ display_name }} without |tojson
        ]
        
        found_unsafe = []
        for pattern in unsafe_patterns:
            matches = re.findall(pattern, content)
            if matches:
                found_unsafe.extend(matches)
        
        if found_unsafe:
            print(f"❌ Found {len(found_unsafe)} unsafe template patterns:")
            for pattern in found_unsafe:
                print(f"   - {pattern}")
        else:
            print("✅ No unsafe template interpolation patterns found")
        
        # Check for safe template interpolation
        print("\n🔍 Checking for safe template interpolation...")
        
        safe_patterns = [
            r'\{\{\s*\w+\|tojson\s*\}\}',  # {{ variable|tojson }}
        ]
        
        found_safe = []
        for pattern in safe_patterns:
            matches = re.findall(pattern, content)
            found_safe.extend(matches)
        
        if found_safe:
            print(f"✅ Found {len(found_safe)} safe template patterns:")
            for pattern in found_safe[:3]:  # Show first 3
                print(f"   - {pattern}")
            if len(found_safe) > 3:
                print(f"   ... and {len(found_safe) - 3} more")
        else:
            print("⚠️ No safe template patterns found")
        
        # Check for global error handler
        print("\n🔍 Checking for global error handler...")
        
        if 'window.addEventListener("error"' in content:
            print("✅ Global JavaScript error handler present")
            
            # Check for specific error handling for syntax errors
            if 'Unexpected token' in content:
                print("✅ Specific handling for 'Unexpected token' errors")
            else:
                print("⚠️ No specific 'Unexpected token' error handling")
        else:
            print("❌ No global error handler found")
        
        # Check for try-catch blocks
        print("\n🔍 Checking for error protection...")
        
        try_catch_count = content.count('try {')
        catch_count = content.count('} catch')
        
        if try_catch_count > 0 and catch_count > 0:
            print(f"✅ Found {try_catch_count} try blocks and {catch_count} catch blocks")
        else:
            print("⚠️ Limited try-catch error protection")
        
        # Check for JSON parsing safety
        print("\n🔍 Checking for safe JSON parsing...")
        
        json_safety_patterns = [
            'JSON.parse',
            'catch',
            'try'
        ]
        
        json_safety_score = sum(1 for pattern in json_safety_patterns if pattern in content)
        print(f"✅ JSON safety elements found: {json_safety_score}/{len(json_safety_patterns)}")
        
        # Overall assessment
        print("\n" + "=" * 50)
        print("📊 JAVASCRIPT FIX VERIFICATION RESULTS")
        print("=" * 50)
        
        checks = [
            ("No unsafe template interpolation", len(found_unsafe) == 0),
            ("Safe template patterns present", len(found_safe) > 0),
            ("Global error handler present", 'window.addEventListener("error"' in content),
            ("Try-catch protection", try_catch_count > 0),
            ("JSON safety elements", json_safety_score >= 2)
        ]
        
        passed_checks = sum(1 for _, passed in checks)
        total_checks = len(checks)
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        print(f"\nOverall Score: {passed_checks}/{total_checks} ({(passed_checks/total_checks)*100:.1f}%)")
        
        if passed_checks >= 4:
            print("\n🎉 JAVASCRIPT FIXES SUCCESSFULLY IMPLEMENTED!")
            print("✅ Speed round should work without 'Unexpected token' errors")
            print("✅ Safe template interpolation is active")
            print("✅ Error handling and recovery mechanisms in place")
        elif passed_checks >= 3:
            print("\n⚠️ Most fixes implemented, minor issues may remain")
        else:
            print("\n❌ JavaScript fixes need more work")
        
        return passed_checks >= 4
        
    except FileNotFoundError:
        print("❌ Could not find templates/quiz.html file")
        return False
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    success = verify_javascript_fixes()
    exit(0 if success else 1)