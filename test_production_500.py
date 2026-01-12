"""
Test production endpoints to identify 500 error
"""

import requests
import sys

BASE_URL = "https://beesmartspelling.app"

print("=" * 70)
print("Testing Production Endpoints for 500 Errors")
print("=" * 70)
print(f"Base URL: {BASE_URL}")
print("=" * 70)
print()

# Common endpoints that might return 500
endpoints = [
    ("/", "Home page", "GET"),
    ("/health", "Health check", "GET"),
    ("/api/wordbank", "Wordbank API", "GET"),
    ("/api/avatars", "Avatars API", "GET"),
    ("/api/buzz-dust/info", "Buzz Dust API", "GET"),
    ("/quiz", "Quiz page", "GET"),
    ("/honeycomb-picker", "Avatar picker", "GET"),
    ("/privacy", "Privacy policy", "GET"),
]

failed = []
passed = []
errors = []

for path, name, method in endpoints:
    try:
        if method == "POST":
            r = requests.post(f"{BASE_URL}{path}", json={}, timeout=10)
        else:
            r = requests.get(f"{BASE_URL}{path}", timeout=10)
        
        if r.status_code == 500:
            print(f"[FAIL] [{r.status_code}] {name} ({path})")
            print(f"   Response preview: {r.text[:300]}")
            failed.append((path, name, r.status_code, r.text[:200]))
        elif r.status_code >= 200 and r.status_code < 300:
            print(f"[PASS] [{r.status_code}] {name} ({path})")
            passed.append((path, name))
        elif r.status_code == 404:
            print(f"[404]  {name} ({path}) - Not found")
        else:
            print(f"[{r.status_code}] {name} ({path})")
            failed.append((path, name, r.status_code, ""))
    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] {name} ({path})")
        errors.append((path, name, "Timeout"))
    except Exception as e:
        print(f"[ERROR] {name} ({path}): {str(e)[:100]}")
        errors.append((path, name, str(e)))

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Passed: {len(passed)}")
print(f"Failed (500): {len([f for f in failed if f[2] == 500])}")
print(f"Other errors: {len(errors)}")
print()

if failed:
    print("FAILED ENDPOINTS:")
    for path, name, status, preview in failed:
        print(f"  - {name} ({path}): Status {status}")
        if preview:
            print(f"    Preview: {preview}...")
    print()

if errors:
    print("ERRORS:")
    for path, name, error in errors:
        print(f"  - {name} ({path}): {error}")
    print()

print("=" * 70)
print("Next Steps:")
print("1. Check Railway logs for the failing endpoint(s)")
print("2. Look for Python traceback in server logs")
print("3. Verify database connection and environment variables")
print("=" * 70)
