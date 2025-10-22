"""
Monitor Railway Deployment Status
Checks health endpoint and provides real-time feedback
"""

import time
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("❌ 'requests' library not installed. Install with: pip install requests")
    sys.exit(1)

RAILWAY_URL = "https://beesmartspellingbee.up.railway.app"
HEALTH_ENDPOINT = f"{RAILWAY_URL}/health"
LOGIN_ENDPOINT = f"{RAILWAY_URL}/auth/login"

def check_status():
    """Check Railway deployment status"""
    timestamp = datetime.now().strftime("%I:%M:%S %p")
    
    print(f"\n{'='*70}")
    print(f"⏰ {timestamp}")
    print(f"{'='*70}")
    
    # Check 1: Health endpoint
    print(f"🔍 Checking health endpoint: {HEALTH_ENDPOINT}")
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        status_code = response.status_code
        
        if status_code == 200:
            data = response.json()
            print(f"✅ HEALTH CHECK PASSED!")
            print(f"   Status Code: {status_code}")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            
            # Check for detailed health info
            if 'checks' in data:
                checks = data['checks']
                print(f"   Session Access: {checks.get('session_access', 'N/A')}")
                print(f"   Dictionary Cache: {checks.get('dictionary_cache', 'N/A')}")
                print(f"   Database: {checks.get('database', 'N/A')}")
            
            return True
        else:
            print(f"⚠️ Health check returned status {status_code}")
            try:
                print(f"   Response: {response.text[:200]}")
            except:
                pass
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏱️ Health check TIMED OUT (server not responding)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: Cannot reach server")
        print(f"   Error: {str(e)[:100]}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)[:100]}")
        return False
    
    # Check 2: Login page (if health passed)
    print(f"\n🔍 Checking login page: {LOGIN_ENDPOINT}")
    try:
        response = requests.get(LOGIN_ENDPOINT, timeout=10)
        if response.status_code == 200:
            print(f"✅ Login page accessible!")
        else:
            print(f"⚠️ Login page returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Login page error: {str(e)[:100]}")


def monitor_deployment(interval=10, max_attempts=30):
    """Monitor deployment with periodic checks"""
    print("\n" + "="*70)
    print("🐝 BeeSmart Railway Deployment Monitor")
    print("="*70)
    print(f"📍 Monitoring: {RAILWAY_URL}")
    print(f"⏱️  Check interval: {interval} seconds")
    print(f"🔄 Max attempts: {max_attempts} (about {max_attempts * interval / 60:.0f} minutes)")
    print("\n💡 Press Ctrl+C to stop monitoring")
    print("="*70)
    
    attempt = 0
    consecutive_successes = 0
    
    try:
        while attempt < max_attempts:
            attempt += 1
            print(f"\n📊 Attempt {attempt}/{max_attempts}")
            
            success = check_status()
            
            if success:
                consecutive_successes += 1
                print(f"\n🎉 SUCCESS! ({consecutive_successes} consecutive)")
                
                if consecutive_successes >= 2:
                    print("\n" + "="*70)
                    print("✅✅✅ DEPLOYMENT CONFIRMED STABLE ✅✅✅")
                    print("="*70)
                    print(f"🌐 App URL: {RAILWAY_URL}")
                    print(f"🔐 Login URL: {LOGIN_ENDPOINT}")
                    print(f"❤️ Health URL: {HEALTH_ENDPOINT}")
                    print("="*70)
                    return True
            else:
                consecutive_successes = 0
                print(f"\n⏳ Waiting {interval} seconds before next check...")
            
            if attempt < max_attempts:
                time.sleep(interval)
        
        print("\n" + "="*70)
        print("⏰ Maximum attempts reached")
        print("="*70)
        print("❌ Deployment may still be in progress or failing")
        print(f"💡 Check Railway logs for details")
        print("="*70)
        return False
        
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 Monitoring stopped by user")
        print("="*70)
        return None


if __name__ == "__main__":
    # Check immediately
    initial_success = check_status()
    
    if initial_success:
        print("\n✅ Deployment is already live and healthy!")
        print(f"🌐 Visit: {RAILWAY_URL}")
    else:
        print("\n⏳ Deployment not ready yet. Starting monitoring...")
        time.sleep(3)
        monitor_deployment(interval=10, max_attempts=30)
