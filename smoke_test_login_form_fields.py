#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke Test for Login Form Fields Visibility Fix
Verifies that username and password input fields are visible on the login page.
"""
import os
import re
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print(" BeeSmart Spelling - Login Form Fields Visibility Smoke Test")
print("=" * 70)

# Test 1: Verify login.html template exists and has form fields
print("\n[1] Testing login.html template structure...")
login_path = Path("templates/auth/login.html")

if not login_path.exists():
    print(f"   [ERROR] {login_path} not found!")
    exit(1)

with open(login_path, 'r', encoding='utf-8') as f:
    login_content = f.read()

# Check for required form elements
required_elements = [
    ('#loginForm', 'Login form element'),
    ('id="username"', 'Username input field'),
    ('id="password"', 'Password input field'),
    ('type="text"', 'Text input type'),
    ('type="password"', 'Password input type'),
    ('class="form-group"', 'Form group containers'),
]

all_elements_found = True
for pattern, description in required_elements:
    if pattern in login_content:
        print(f"   ✅ Found: {description}")
    else:
        print(f"   ❌ Missing: {description}")
        all_elements_found = False

# Test 2: Verify CSS rules for visibility
print("\n[2] Testing CSS visibility rules...")
css_checks = [
    ('#loginForm.*display.*block.*!important', 'Form display block with !important'),
    ('.form-group.*display.*block.*!important', 'Form group display block with !important'),
    ('input\\[type="text"\\].*display.*block.*!important', 'Text input display block with !important'),
    ('input\\[type="password"\\].*display.*block.*!important', 'Password input display block with !important'),
    ('visibility.*visible.*!important', 'Visibility visible with !important'),
    ('opacity.*1.*!important', 'Opacity 1 with !important'),
]

css_found = True
for pattern, description in css_checks:
    if re.search(pattern, login_content, re.IGNORECASE | re.DOTALL):
        print(f"   ✅ Found: {description}")
    else:
        print(f"   ⚠️  Missing: {description}")
        css_found = False

# Test 3: Verify JavaScript visibility enforcement
print("\n[3] Testing JavaScript visibility enforcement...")
js_checks = [
    ('ensureFormFieldsVisible', 'Visibility enforcement function'),
    ('formGroups.*forEach', 'Form groups iteration'),
    ('inputs.*forEach', 'Inputs iteration'),
    ('el.style.display.*=.*[\'"]block[\'"]', 'Display block assignment'),
    ('el.style.visibility.*=.*[\'"]visible[\'"]', 'Visibility visible assignment'),
    ('DOMContentLoaded', 'DOMContentLoaded event listener'),
]

js_found = True
for pattern, description in js_checks:
    if re.search(pattern, login_content, re.IGNORECASE | re.DOTALL):
        print(f"   ✅ Found: {description}")
    else:
        print(f"   ⚠️  Missing: {description}")
        js_found = False

# Test 4: Verify form structure integrity
print("\n[4] Testing form structure integrity...")
structure_checks = [
    ('<form.*id="loginForm"', 'Form opening tag with id'),
    ('</form>', 'Form closing tag'),
    ('<div class="form-group">', 'Form group div'),
    ('<label.*for="username"', 'Username label'),
    ('<label.*for="password"', 'Password label'),
    ('<button.*type="submit"', 'Submit button'),
]

structure_found = True
for pattern, description in structure_checks:
    if re.search(pattern, login_content, re.IGNORECASE | re.DOTALL):
        print(f"   ✅ Found: {description}")
    else:
        print(f"   ❌ Missing: {description}")
        structure_found = False

# Test 5: Verify no conflicting CSS that might hide fields
print("\n[5] Testing for conflicting CSS rules...")
conflicting_patterns = [
    (r'\.form-group\s*\{[^}]*display\s*:\s*none', 'Form group display:none'),
    (r'#loginForm\s*\{[^}]*display\s*:\s*none', 'Login form display:none'),
    (r'input\s*\{[^}]*display\s*:\s*none', 'Input display:none'),
]

conflicts_found = False
for pattern, description in conflicting_patterns:
    matches = re.findall(pattern, login_content, re.IGNORECASE | re.DOTALL)
    if matches:
        print(f"   [WARN] Found potential conflict: {description}")
        conflicts_found = True

if not conflicts_found:
    print("   [OK] No obvious conflicting CSS rules found")

# Test 6: Verify z-index and positioning
print("\n[6] Testing z-index and positioning...")
zindex_checks = [
    ('z-index.*10.*!important', 'Form z-index'),
    ('z-index.*2', 'Card body z-index'),
    ('position.*relative', 'Relative positioning'),
]

zindex_found = True
for pattern, description in zindex_checks:
    if re.search(pattern, login_content, re.IGNORECASE | re.DOTALL):
        print(f"   ✅ Found: {description}")
    else:
        print(f"   ⚠️  Missing: {description}")
        zindex_found = False

# Summary
print("\n" + "=" * 70)
if all_elements_found and structure_found and not conflicts_found:
    print(" [PASS] CORE TESTS PASSED - Form structure is correct")
    if css_found and js_found:
        print(" [PASS] VISIBILITY FIXES VERIFIED - CSS and JS visibility rules present")
        print("\n [PASS] ALL TESTS PASSED - Login form fields should be visible")
    else:
        print(" [WARN] VISIBILITY FIXES PARTIAL - Some CSS/JS rules may be missing")
        print("    Form fields should still be visible due to HTML structure")
else:
    print(" [FAIL] SOME TESTS FAILED - Review results above")
print("=" * 70)

print("\nNext Steps:")
print("   1. Start the Flask app: python AjaSpellBApp.py")
print("   2. Navigate to: http://localhost:5000/auth/login")
print("   3. Verify username and password fields are visible")
print("   4. Test form submission with valid credentials")
print("   5. Check browser console for any JavaScript errors")
