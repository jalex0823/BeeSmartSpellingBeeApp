"""
Diagnostic script to check Flask routes
"""
import sys
import os

# Set console encoding for Windows
if sys.platform == "win32":
    os.system('chcp 65001 >nul 2>&1')

from AjaSpellBApp import app

print("\n" + "="*70)
print("🔍 FLASK ROUTES DIAGNOSTIC")
print("="*70)

print(f"\n📊 Total routes registered: {len(app.url_map._rules)}")

print("\n🗺️ All registered routes:")
print("-" * 70)

routes = []
for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
    routes.append((str(rule), methods, rule.endpoint))

# Sort by path
routes.sort()

# Print in organized way
auth_routes = [r for r in routes if '/auth/' in r[0]]
api_routes = [r for r in routes if '/api/' in r[0]]
speed_routes = [r for r in routes if 'speed' in r[0].lower()]
other_routes = [r for r in routes if r not in auth_routes + api_routes + speed_routes]

if auth_routes:
    print("\n🔐 AUTHENTICATION ROUTES:")
    for path, methods, endpoint in auth_routes:
        print(f"   {path:50} [{methods:15}] -> {endpoint}")

if api_routes:
    print("\n🔌 API ROUTES:")
    for path, methods, endpoint in api_routes:
        print(f"   {path:50} [{methods:15}] -> {endpoint}")

if speed_routes:
    print("\n⚡ SPEED ROUND ROUTES:")
    for path, methods, endpoint in speed_routes:
        print(f"   {path:50} [{methods:15}] -> {endpoint}")

if other_routes:
    print("\n📄 OTHER ROUTES:")
    for path, methods, endpoint in other_routes[:20]:  # Limit to first 20
        print(f"   {path:50} [{methods:15}] -> {endpoint}")
    if len(other_routes) > 20:
        print(f"   ... and {len(other_routes) - 20} more routes")

print("\n" + "="*70)
print(f"✅ Diagnostic complete!")
print("="*70)
