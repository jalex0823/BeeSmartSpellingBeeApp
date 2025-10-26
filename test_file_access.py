import requests

print("Testing file accessibility on Railway...\n")

test_files = [
    ('al-bee', 'AlBee.obj'),  # Working avatar
    ('beedoctor', 'DoctorBee.obj'),  # New avatar
    ('beeknight', 'KnightBee.obj'),  # New avatar
]

for folder, filename in test_files:
    url = f'https://beesmart.up.railway.app/static/assets/avatars/{folder}/{filename}'
    try:
        r = requests.head(url, timeout=5)
        status = "✅" if r.status_code == 200 else f"❌ {r.status_code}"
        print(f"{folder}/{filename}: {status}")
    except Exception as e:
        print(f"{folder}/{filename}: ❌ ERROR - {e}")
