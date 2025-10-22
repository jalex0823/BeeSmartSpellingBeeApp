import urllib.request
import urllib.error
import json

# Test clear API without authorization
print("Testing /api/clear without authorization...")
try:
    data = json.dumps({}).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:5000/api/clear',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))
    print(f"❌ Unexpected success: {result}")
except urllib.error.HTTPError as e:
    error_data = json.loads(e.read().decode('utf-8'))
    print(f"✅ Expected error (status {e.status}): {error_data}")

print("\nTesting /api/clear with authorization...")
try:
    data = json.dumps({"confirmed": True}).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:5000/api/clear',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {e}")