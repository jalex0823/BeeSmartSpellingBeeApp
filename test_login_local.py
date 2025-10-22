"""
Test Login and Check User Credentials
Tests both local database and Railway server (when available)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import get_config
from models import db, User

def test_local_database():
    """Test local database for user credentials"""
    print("\n" + "="*70)
    print("🔍 TESTING LOCAL DATABASE")
    print("="*70)
    
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    
    with app.app_context():
        try:
            # Get all users
            users = User.query.all()
            
            if not users:
                print("❌ No users found in database")
                return False
            
            print(f"\n✅ Found {len(users)} users in database:\n")
            
            for user in users:
                print(f"👤 User: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   Role: {user.role}")
                print(f"   Display Name: {user.display_name}")
                print(f"   Created: {user.created_at}")
                print(f"   Has Password: {'✅ Yes' if user.password_hash else '❌ No'}")
                print(f"   Is Active: {'✅ Yes' if user.is_active else '❌ No'}")
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error accessing database: {e}")
            return False


def test_login_credentials(username, password):
    """Test if specific login credentials work"""
    print("\n" + "="*70)
    print(f"🔐 TESTING LOGIN: {username}")
    print("="*70)
    
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    
    with app.app_context():
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"❌ User '{username}' not found in database")
                return False
            
            print(f"\n✅ User found: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
            
            # Test password
            if user.check_password(password):
                print(f"\n✅ PASSWORD CORRECT! Login would succeed.")
                return True
            else:
                print(f"\n❌ PASSWORD INCORRECT! Login would fail.")
                return False
                
        except Exception as e:
            print(f"❌ Error testing login: {e}")
            return False


def test_railway_server():
    """Test Railway server availability and login endpoint"""
    print("\n" + "="*70)
    print("🚂 TESTING RAILWAY SERVER")
    print("="*70)
    
    try:
        import requests
        
        railway_url = "https://beesmartspellingbee.up.railway.app"
        
        # Test health endpoint
        print(f"\n🔍 Testing health endpoint: {railway_url}/health")
        try:
            response = requests.get(f"{railway_url}/health", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Server is healthy!")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Database: {data.get('checks', {}).get('database', 'unknown')}")
            else:
                print(f"   ⚠️ Server responded but not healthy")
        except requests.exceptions.Timeout:
            print(f"   ❌ Server timed out (deployment may be failing)")
            return False
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Could not connect to server (deployment may be down)")
            return False
        
        # Test login page
        print(f"\n🔍 Testing login page: {railway_url}/login")
        try:
            response = requests.get(f"{railway_url}/login", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Login page is accessible")
            else:
                print(f"   ⚠️ Login page returned status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error accessing login page: {e}")
        
        return True
        
    except ImportError:
        print("   ⚠️ 'requests' library not installed. Install with: pip install requests")
        return False
    except Exception as e:
        print(f"   ❌ Error testing Railway server: {e}")
        return False


if __name__ == "__main__":
    print("\n🐝 BeeSmart Login Credential Test")
    print("="*70)
    
    # Test 1: Check local database
    test_local_database()
    
    # Test 2: Test Railway server
    test_railway_server()
    
    # Test 3: Test specific credentials (if provided)
    print("\n" + "="*70)
    print("💡 To test specific login credentials, run:")
    print("   python test_login_local.py <username> <password>")
    print("="*70)
    
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
        test_login_credentials(username, password)
    
    print("\n✨ Test complete!\n")
