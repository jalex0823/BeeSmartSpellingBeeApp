"""
Create admin user and fix avatars via Railway API
"""
import requests
import sys

# Railway production URL
BASE_URL = "https://beesmart.up.railway.app"

def create_admin_user():
    """Create the BigDaddy admin user if it doesn't exist"""
    
    print("\n👤 Creating/verifying admin user...")
    
    # Register the admin user
    register_url = f"{BASE_URL}/auth/register"
    register_data = {
        "username": "BigDaddy",
        "email": "bigdaddy@beesmart.app",
        "password": "Aja121514!",
        "confirm_password": "Aja121514!",
        "role": "student"  # Will need to be manually upgraded to admin
    }
    
    session = requests.Session()
    
    try:
        response = session.post(register_url, json=register_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Admin user created (needs role upgrade)")
                print("⚠️  User created as 'student' - needs manual upgrade to 'admin' role")
                print("   Please run: UPDATE users SET role='admin' WHERE username='BigDaddy';")
                return None
            else:
                print(f"⚠️  Registration response: {result.get('message', 'Unknown')}")
                # User might already exist, try to login
                return try_login(session)
        else:
            print(f"⚠️  Registration status: {response.status_code}")
            # User might already exist, try to login
            return try_login(session)
            
    except Exception as e:
        print(f"⚠️  Registration error: {e}")
        # Try to login anyway
        return try_login(session)

def try_login(session=None):
    """Try to login with admin credentials"""
    
    if session is None:
        session = requests.Session()
    
    print("\n🔐 Attempting admin login...")
    
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "username": "BigDaddy",
        "password": "Aja121514!"
    }
    
    try:
        response = session.post(login_url, json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Login successful")
                return session
            else:
                print(f"❌ Login failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ Login failed with status {response.status_code}")
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def fix_avatars(session):
    """Call the avatar fix endpoint"""
    
    print("\n🔧 Calling avatar fix endpoint...")
    
    fix_url = f"{BASE_URL}/api/admin/fix-avatar-glb-paths"
    
    try:
        response = session.post(fix_url)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Avatar paths fixed successfully!")
            print("=" * 60)
            print(f"📊 Statistics:")
            print(f"   Total avatars: {result.get('total_avatars', 'N/A')}")
            print(f"   Fixed: {result.get('fixed_count', 'N/A')}")
            print(f"   Already correct: {result.get('already_correct', 'N/A')}")
            print("=" * 60)
            
            if result.get('fixed_avatars'):
                print("\n📝 Fixed avatars:")
                for avatar in result['fixed_avatars']:
                    print(f"   • {avatar['name']}: {avatar['old_path']} → {avatar['new_path']}")
            
            return True
        elif response.status_code == 403:
            print("❌ Access denied - user is not an admin")
            print("   Please upgrade user role in database:")
            print("   UPDATE users SET role='admin' WHERE username='BigDaddy';")
            return False
        else:
            print(f"❌ Fix failed with status {response.status_code}")
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Fix error: {e}")
        return False

def main():
    """Main execution"""
    
    print("=" * 60)
    print("🐝 Avatar GLB Fix via Railway API")
    print("=" * 60)
    
    # Try to login first
    session = try_login()
    
    # If login fails, try to create user
    if not session:
        print("\n⚠️  Login failed - attempting to create admin user...")
        session = create_admin_user()
    
    if not session:
        print("\n❌ Could not establish authenticated session")
        print("\n💡 Manual steps:")
        print("   1. Register user 'BigDaddy' at: https://beesmart.up.railway.app/auth/register")
        print("   2. Upgrade to admin in Railway database:")
        print("      UPDATE users SET role='admin' WHERE username='BigDaddy';")
        print("   3. Run this script again")
        return False
    
    # Call the fix endpoint
    return fix_avatars(session)

if __name__ == "__main__":
    print("\n⚠️  This will update ALL avatar paths in the Railway production database")
    confirm = input("\nType 'YES' to proceed: ")
    
    if confirm.strip() == "YES":
        success = main()
        sys.exit(0 if success else 1)
    else:
        print("\n❌ Cancelled by user")
        sys.exit(1)
