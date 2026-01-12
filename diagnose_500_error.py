"""
Diagnose 500 Internal Server Error
Tests common endpoints to identify which one is failing
"""

import requests
import sys

# Default to localhost, but allow override
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5051"

print("=" * 70)
print("500 Error Diagnostic Tool")
print("=" * 70)
print(f"Testing: {BASE_URL}")
print("=" * 70)
print()

# Common endpoints that might return 500 errors
endpoints = [
    ("/", "Home page"),
    ("/health", "Health check"),
    ("/api/wordbank", "Wordbank API"),
    ("/api/avatars", "Avatars API"),
    ("/api/buzz-dust/info", "Buzz Dust API"),
    ("/api/next", "Next word API (POST)"),
    ("/quiz", "Quiz page"),
    ("/honeycomb-picker", "Avatar picker"),
    ("/privacy", "Privacy policy"),
]

failed = []
passed = []

for path, name in endpoints:
    try:
        if path == "/api/next":
            # POST endpoint
            r = requests.post(f"{BASE_URL}{path}", json={"word": "test"}, timeout=5)
        else:
            # GET endpoint
            r = requests.get(f"{BASE_URL}{path}", timeout=5)
        
        if r.status_code == 500:
            print(f"❌ FAIL [{r.status_code}] {name} ({path})")
            print(f"   Response: {r.text[:200]}")
            failed.append((path, name, r.status_code))
        elif r.status_code >= 200 and r.status_code < 300:
            print(f"✅ PASS [{r.status_code}] {name} ({path})")
            passed.append((path, name))
        else:
            print(f"⚠️  [{r.status_code}] {name} ({path})")
            failed.append((path, name, r.status_code))
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - {name} ({path})")
        print(f"   Server may not be running at {BASE_URL}")
        failed.append((path, name, "Connection Error"))
    except Exception as e:
        print(f"❌ ERROR - {name} ({path}): {e}")
        failed.append((path, name, str(e)))

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✅ Passed: {len(passed)}")
print(f"❌ Failed: {len(failed)}")
print()

if failed:
    print("FAILED ENDPOINTS:")
    for path, name, status in failed:
        print(f"  - {name} ({path}): {status}")
    print()
    print("💡 TIP: Check the server logs for the actual error traceback")
    print("   The 500 error handler should log the full Python exception")
else:
    print("✅ All tested endpoints are working!")
    print("   The 500 error might be from a different endpoint.")
    print("   Check the browser console (F12) to see which specific URL is failing.")

print()
print("=" * 70)
