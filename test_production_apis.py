"""
Test production API endpoints that are called by JavaScript
"""

import requests
import sys

BASE_URL = "https://beesmartspelling.app"

print("=" * 70)
print("Testing Production API Endpoints Called by JavaScript")
print("=" * 70)
print(f"Base URL: {BASE_URL}")
print("=" * 70)
print()

# API endpoints called by JavaScript on page load
endpoints = [
    ("/api/auth/status", "GET", "Auth status check"),
    ("/api/wordbank", "GET", "Wordbank API"),
    ("/api/avatars", "GET", "Avatars API"),
    ("/api/buzz-dust/info", "GET", "Buzz Dust API"),
    ("/api/quiz/state", "GET", "Quiz state API"),
    ("/api/content-filter-status", "GET", "Content filter status"),
    ("/api/saved-lists", "GET", "Saved lists API"),
    ("/api/iap/restore", "POST", "IAP restore (may require auth)"),
]

failed = []
passed = []
warnings = []

for path, method, name in endpoints:
    try:
        if method == "POST":
            r = requests.post(f"{BASE_URL}{path}", json={}, timeout=10, allow_redirects=False)
        else:
            r = requests.get(f"{BASE_URL}{path}", timeout=10, allow_redirects=False)
        
        if r.status_code == 500:
            print(f"[FAIL] [{r.status_code}] {name} ({path})")
            try:
                error_data = r.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                print(f"   Details: {error_data.get('details', 'No details')[:200]}")
            except:
                print(f"   Response: {r.text[:300]}")
            failed.append((path, name, r.status_code))
        elif r.status_code >= 200 and r.status_code < 300:
            print(f"[PASS] [{r.status_code}] {name} ({path})")
            passed.append((path, name))
        elif r.status_code == 401 or r.status_code == 403:
            print(f"[AUTH] [{r.status_code}] {name} ({path}) - Requires authentication (expected)")
            warnings.append((path, name, r.status_code))
        elif r.status_code == 404:
            print(f"[404]  [{r.status_code}] {name} ({path}) - Not found")
            warnings.append((path, name, r.status_code))
        else:
            print(f"[{r.status_code}] {name} ({path})")
            failed.append((path, name, r.status_code))
    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] {name} ({path})")
        failed.append((path, name, "Timeout"))
    except Exception as e:
        print(f"[ERROR] {name} ({path}): {str(e)[:100]}")
        failed.append((path, name, str(e)))

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Passed: {len(passed)}")
print(f"Failed (500): {len([f for f in failed if f[2] == 500])}")
print(f"Warnings (401/404): {len(warnings)}")
print(f"Other errors: {len([f for f in failed if f[2] != 500])}")
print()

if failed:
    print("FAILED ENDPOINTS:")
    for path, name, status in failed:
        print(f"  - {name} ({path}): {status}")
    print()

if warnings:
    print("WARNINGS (may be expected):")
    for path, name, status in warnings:
        print(f"  - {name} ({path}): Status {status}")
    print()

print("=" * 70)
print("Next Steps:")
if failed:
    print("1. Check Railway logs for the failing endpoint(s)")
    print("2. Look for Python traceback in server logs")
    print("3. The 500 error handler should log the full exception")
else:
    print("All tested API endpoints are working!")
    print("The 500 error might be from:")
    print("  - A static asset (image, CSS, JS file)")
    print("  - An avatar file that can't be served")
    print("  - A conditional API call based on user state")
    print("Check browser Network tab (F12) to see the exact failing URL")
print("=" * 70)
