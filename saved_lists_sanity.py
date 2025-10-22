import requests

BASE = "http://127.0.0.1:5000"

s = requests.Session()

# Load home to set session
r = s.get(f"{BASE}/")
print("GET / ->", r.status_code)

# Get current saved lists
r = s.get(f"{BASE}/api/saved-lists")
print("GET /api/saved-lists ->", r.status_code, r.json())

start_lists = r.json().get("lists") if r.ok else []
start_count = len(start_lists or [])
print("start_count:", start_count)

# Save current wordbank (assumes default wordbank exists, otherwise API should handle empty)
payload = {"list_name": "AutoTest List", "description": "Created by sanity script"}
r = s.post(f"{BASE}/api/saved-lists/save", json=payload)
print("POST /api/saved-lists/save ->", r.status_code, r.json())

# Verify count increased
r = s.get(f"{BASE}/api/saved-lists")
print("GET /api/saved-lists (after save) ->", r.status_code)
print(r.json())

lists = r.json().get("lists") if r.ok else []
new_count = len(lists or [])
print("new_count:", new_count)

if new_count < start_count:
    raise SystemExit("Count decreased after save, unexpected")

# Delete the newly created list by matching name and description
created = None
for item in lists:
    if item.get("name") == payload["list_name"] and item.get("description") == payload["description"]:
        created = item
        break

if created:
    r = s.post(f"{BASE}/api/saved-lists/delete", json={"id": created["id"]})
    print("POST /api/saved-lists/delete ->", r.status_code, r.json())

    r = s.get(f"{BASE}/api/saved-lists")
    print("GET /api/saved-lists (after delete) ->", r.status_code)
    print(r.json())
else:
    print("Warning: newly created list not found; skipping delete step")
