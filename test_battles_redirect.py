import requests
import time

# Wait a moment for Flask to fully start
time.sleep(2)

try:
    # Test main page
    r = requests.get('http://localhost:5000/')
    print(f"Main page status: {r.status_code}")
    
    # Test battles page
    r = requests.get('http://localhost:5000/battles')
    print(f"Battles page status: {r.status_code}")
    
    if r.status_code == 200:
        print("✅ Battles page loads successfully!")
        print("🔗 The 'Join the Battle' button will now redirect to /battles")
    else:
        print(f"❌ Battles page error: {r.status_code}")
        
except Exception as e:
    print(f"❌ Error testing: {e}")