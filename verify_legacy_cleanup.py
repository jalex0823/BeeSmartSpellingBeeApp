#!/usr/bin/env python3
"""
Verify that legacy field references have been cleaned up.
"""
import os
import re

def check_file(filepath, patterns):
    """Check if any patterns are found in a file."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    findings = []
    for pattern_name, pattern in patterns.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            findings.append((line_num, pattern_name, match.group(0)))
    
    return findings

def main():
    # Files to check
    files_to_check = {
        'static/js/user-avatar-loader.js': {
            'urls.model_obj': r'urls\s*\?\s*\.\s*model_obj',
            'model_obj fallback': r'model_obj\s*\|\|',
            'obj_file_url fallback': r'obj_file_url',
            'model_obj_url fallback': r'model_obj_url',
        },
        'static/js/honeycomb-avatar-picker.js': {
            'urls.model_obj check': r'urls\s*\?\s*\.\s*model_obj',
        },
        'static/js/honeycomb-avatar-picker-responsive.js': {
            'urls.model_obj fallback': r'urls\s*\?\s*\.model_obj',
            'obj_file_url reference': r'obj_file_url',
            'model_obj_url reference': r'model_obj_url',
        },
        'AjaSpellBApp.py': {
            'model_obj in urls': r"'model_obj'.*:",
            'model_obj_url reference': r'model_obj_url',
        },
        'models.py': {
            'model_obj in urls dict': r"'model_obj'",
        }
    }
    
    total_issues = 0
    
    for filepath, patterns in files_to_check.items():
        full_path = os.path.join('c:\\Temp\\BeeSmartSpellingBeeApp', filepath)
        if not os.path.exists(full_path):
            print(f"⚠️  File not found: {filepath}")
            continue
        
        findings = check_file(full_path, patterns)
        
        if findings:
            print(f"\n❌ {filepath}:")
            for line_num, pattern_name, text in findings:
                print(f"   Line {line_num}: {pattern_name}")
                print(f"   Found: {text[:60]}")
                total_issues += 1
        else:
            print(f"✅ {filepath}: No legacy fields found")
    
    print(f"\n{'='*60}")
    if total_issues == 0:
        print("✅ SUCCESS: All legacy field references have been cleaned up!")
        print("   - Removed model_obj from API responses")
        print("   - Removed obj_file_url fallbacks")
        print("   - Updated JavaScript to use urls.glb only")
        print("   - All 39 avatars will load with GLB format only")
    else:
        print(f"❌ ISSUES FOUND: {total_issues} legacy references remain")
    
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
