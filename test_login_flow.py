"""
Test login functionality on live Railway deployment
"""
import requests
import json

BASE_URL = "https://beesmartspellingbee.up.railway.app"
TEST_USER = "BigDaddy2"
TEST_PASSWORD = "Aja123!!"

def test_login_flow():
    """Test complete login flow"""
    session = requests.Session()
    
    print("="*70)
    print("🔐 Testing Login Flow")
    print("="*70)
    
    # Step 1: Get login page
    print("\n1️⃣ Fetching login page...")
    try:
        r = session.get(f"{BASE_URL}/auth/login", timeout=15)
        print(f"   Status: {r.status_code}")
        print(f"   Has form: {'<form' in r.text}")
        print(f"   Has CSRF: {'csrf' in r.text.lower()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 2: Attempt login
    print("\n2️⃣ Attempting login...")
    try:
        login_data = {
            'username': TEST_USER,
            'password': TEST_PASSWORD
        }
        
        r = session.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            timeout=15,
            allow_redirects=True
        )
        
        print(f"   Status: {r.status_code}")
        print(f"   Final URL: {r.url}")
        print(f"   Redirected: {r.history}")
        
        # Check response content
        if r.status_code == 200:
            has_dashboard = 'dashboard' in r.text.lower()
            has_logout = 'logout' in r.text.lower()
            has_error = 'invalid' in r.text.lower() or 'error' in r.text.lower()
            
            print(f"   Has dashboard: {has_dashboard}")
            print(f"   Has logout: {has_logout}")
            print(f"   Has error: {has_error}")
            
            if has_error:
                # Try to extract error message
                if 'Invalid username or password' in r.text:
                    print("   ❌ Invalid credentials")
                elif 'User not found' in r.text:
                    print("   ❌ User doesn't exist")
                else:
                    print("   ❌ Unknown error")
                    # Print first 500 chars around "error"
                    idx = r.text.lower().find('error')
                    if idx > 0:
                        snippet = r.text[max(0, idx-100):idx+400]
                        print(f"\n   Context: ...{snippet}...")
            
            if has_dashboard or has_logout:
                print("   ✅ Login successful!")
                return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 3: Try to access protected route
    print("\n3️⃣ Testing dashboard access...")
    try:
        r = session.get(f"{BASE_URL}/dashboard", timeout=15)
        print(f"   Status: {r.status_code}")
        
        if r.status_code == 200:
            print("   ✅ Dashboard accessible")
            return True
        elif r.status_code == 302:
            print(f"   ⚠️  Redirected to: {r.headers.get('Location')}")
        else:
            print(f"   ❌ Access denied")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_login_flow()
    
    if not success:
        print("\n" + "="*70)
        print("🔍 TROUBLESHOOTING SUGGESTIONS")
        print("="*70)
        print("1. Verify BigDaddy2 account exists in database")
        print("2. Check password hash is correct")
        print("3. Verify Flask-Login session management")
        print("4. Check for CSRF token requirements")
        print("5. Review Railway logs for authentication errors")
        print("="*70)
