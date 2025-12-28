#!/usr/bin/env python3
"""
Smoke Test for Apple Compliance Changes
Tests Terms/EULA content and pricing removal
"""
import os

print("=" * 70)
print(" BeeSmart Spelling - Apple Compliance Smoke Test")
print("=" * 70)

# Test 1: Verify Terms.html contains Apple minimum requirements
print("\n1️⃣ Testing Terms.html for Apple EULA requirements...")
terms_path = "templates/terms.html"
with open(terms_path, 'r', encoding='utf-8') as f:
    terms_content = f.read()

required_sections = [
    ("Scope of License", "1. Scope of License"),
    ("Maintenance and Support", "4. Maintenance and Support"),
    ("Warranty", "5. Warranty"),
    ("Product Claims", "6. Product Claims"),
    ("Intellectual Property Rights", "7. Intellectual Property Rights"),
    ("Legal Compliance", "8. Legal Compliance"),
    ("Third Party Terms", "9. Third Party Terms"),
    ("Third Party Beneficiary", "14. Third Party Beneficiary"),
    ("Developer Name and Contact", "20. Developer Name and Contact Information"),
]

all_sections_found = True
for name, heading in required_sections:
    if heading in terms_content:
        print(f"   ✅ Found: {name}")
    else:
        print(f"   ❌ Missing: {name}")
        all_sections_found = False

# Check for subscription disclosures
subscription_terms = [
    "auto-renewal",
    "24 hours before",
    "manage and cancel",
    "iOS Settings",
    "Payment is charged"
]

print("\n2️⃣ Testing subscription disclosures...")
for term in subscription_terms:
    if term.lower() in terms_content.lower():
        print(f"   ✅ Found: {term}")
    else:
        print(f"   ❌ Missing: {term}")
        all_sections_found = False

# Test 2: Verify no pricing in templates
print("\n3️⃣ Testing for pricing removal in templates...")
templates_to_check = [
    "templates/unified_menu.html",
]

pricing_patterns = ["$4.99", "$39.99", "$7.99", "4.49", "39.99", "7.99"]
pricing_found = False

for template in templates_to_check:
    if os.path.exists(template):
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for pattern in pricing_patterns:
            if pattern in content:
                print(f"   ❌ Found price '{pattern}' in {template}")
                pricing_found = True
        
        if not pricing_found:
            print(f"   ✅ No pricing in {template}")

# Test 3: Verify backend has no pricing
print("\n4️⃣ Testing for pricing removal in backend...")
backend_file = "AjaSpellBApp.py"
with open(backend_file, 'r', encoding='utf-8') as f:
    backend_content = f.read()

backend_pricing_patterns = ["'price': 4.99", "'price': 39.99", "'price': 7.99", "monthly_fee = 4.49"]
backend_pricing_found = False

for pattern in backend_pricing_patterns:
    if pattern in backend_content:
        print(f"   ❌ Found price pattern '{pattern}' in {backend_file}")
        backend_pricing_found = True

if not backend_pricing_found:
    print(f"   ✅ No hard-coded pricing in {backend_file}")

# Test 4: Check for "Pricing shown in the App Store" message
print("\n5️⃣ Testing for Apple-compliant pricing message...")
if "Pricing shown in the App Store" in content or "pricing shown in the app store" in content.lower():
    print("   ✅ Found Apple-compliant pricing message")
else:
    print("   ⚠️  Apple-compliant pricing message not found")

# Summary
print("\n" + "=" * 70)
if all_sections_found and not pricing_found and not backend_pricing_found:
    print(" ✅ ALL TESTS PASSED - Apple compliance changes verified")
else:
    print(" ⚠️  SOME TESTS FAILED - Review results above")
print("=" * 70)

print("\n📋 Next Steps:")
print("   1. Fill in missing contact info in terms.html Section 20:")
print("      - [Your Complete Mailing Address]")
print("      - [Your Support Phone Number]")
print("   2. Copy EULA text to App Store Connect Custom EULA field")
print("   3. Test /terms page loads correctly in browser")
print("   4. Verify in-app Terms link works from unified menu")
