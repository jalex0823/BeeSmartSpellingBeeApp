#!/usr/bin/env python3
"""
Railway Avatar System Deployment Test
Test script to verify avatar system will work on Railway
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_local_avatar_apis():
    """Test avatar APIs locally before Railway deployment"""
    
    print("🧪 RAILWAY AVATAR DEPLOYMENT TEST")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    tests = [
        {
            'name': 'Avatar Catalog API',
            'endpoint': '/api/avatars',
            'method': 'GET'
        },
        {
            'name': 'Individual Avatar API', 
            'endpoint': '/api/avatar/cool-bee',
            'method': 'GET'
        },
        {
            'name': 'Avatar Categories API',
            'endpoint': '/api/avatars/categories', 
            'method': 'GET'
        }
    ]
    
    results = []
    
    print("🔍 Testing current avatar APIs...")
    
    for test in tests:
        print(f"\n📡 Testing: {test['name']}")
        print(f"   Endpoint: {test['endpoint']}")
        
        try:
            response = requests.get(f"{base_url}{test['endpoint']}", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS")
                
                # Show key data points
                if 'avatars' in data:
                    print(f"   📊 Avatars count: {len(data['avatars'])}")
                elif 'avatar' in data:
                    print(f"   🐝 Avatar: {data['avatar'].get('name', 'Unknown')}")
                elif 'categories' in data:
                    print(f"   📂 Categories: {len(data['categories'])}")
                
                results.append({
                    'test': test['name'],
                    'status': 'PASS',
                    'response_time': response.elapsed.total_seconds(),
                    'data_size': len(str(data))
                })
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
                results.append({
                    'test': test['name'],
                    'status': 'FAIL',
                    'error': f"HTTP {response.status_code}",
                    'response': response.text[:200]
                })
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION ERROR: Flask app not running")
            print(f"   💡 Start with: python AjaSpellBApp.py")
            
            results.append({
                'test': test['name'],
                'status': 'ERROR',
                'error': 'Connection refused - Flask not running'
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            
            results.append({
                'test': test['name'],
                'status': 'ERROR', 
                'error': str(e)
            })
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 AVATAR API TEST SUMMARY")
    print("=" * 60)
    
    passed = len([r for r in results if r['status'] == 'PASS'])
    failed = len([r for r in results if r['status'] == 'FAIL']) 
    errors = len([r for r in results if r['status'] == 'ERROR'])
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🚫 Errors: {errors}")
    
    if passed == len(tests):
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Avatar system ready for Railway deployment")
        return True
    else:
        print(f"\n⚠️  ISSUES DETECTED")
        print(f"   Fix issues before Railway deployment")
        
        for result in results:
            if result['status'] != 'PASS':
                print(f"   • {result['test']}: {result.get('error', 'Failed')}")
        
        return False

def generate_railway_test_plan():
    """Generate post-deployment test plan for Railway"""
    
    test_plan = f'''
🚂 RAILWAY AVATAR SYSTEM POST-DEPLOYMENT TEST PLAN
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================================

1. IMMEDIATE HEALTH CHECK
   URL: https://your-app.railway.app/api/avatar/health
   Expected: JSON with avatar system status
   
2. AVATAR CATALOG TEST  
   URL: https://your-app.railway.app/api/avatars
   Expected: JSON with avatar list (18+ avatars)
   
3. INDIVIDUAL AVATAR TEST
   URL: https://your-app.railway.app/api/avatar/cool-bee
   Expected: JSON with Cool Bee avatar info
   
4. THEME SYSTEM TEST
   URL: https://your-app.railway.app/api/avatar/theme/al-bee
   Expected: JSON with Al Bee theme data
   
5. AIS (Avatar Installation System) TEST
   • Log into Railway console
   • Check for avatar-related errors in logs
   • Verify 3D Avatar Files directory deployed
   
6. USER INTERFACE TEST
   • Load main app in browser
   • Navigate to avatar selection
   • Verify avatars load and display
   • Test avatar switching functionality
   
7. PERFORMANCE CHECK
   • Test avatar loading speed
   • Check 3D model rendering
   • Verify thumbnail display
   
TROUBLESHOOTING COMMANDS:
========================
# Check Railway logs
railway logs --tail

# Check file system on Railway 
railway shell
ls -la static/Avatars/
ls -la static/Avatars/3D\ Avatar\ Files/

# Test avatar endpoints
curl https://your-app.railway.app/api/avatar/health
curl https://your-app.railway.app/api/avatars

FALLBACK STRATEGIES:
===================
If avatar system fails on Railway:
1. Check Railway logs for specific errors
2. Verify static files deployed correctly
3. Use avatar health endpoint for diagnostics
4. Enable Railway-safe mode with fallback avatars
5. Check AIS (Avatar Installation System) compatibility

EXPECTED RAILWAY ISSUES:
========================
• File path differences (Linux vs Windows)
• Static file serving configuration
• Import path issues
• Memory constraints for 3D files
• Network timeouts for large assets

SUCCESS INDICATORS:
==================
✅ /api/avatar/health returns 200 OK
✅ /api/avatars returns 18+ avatars
✅ Avatar selection UI works in browser
✅ 3D models load without errors
✅ AIS ready for 6 new avatar installation
'''
    
    return test_plan

if __name__ == "__main__":
    # Test local APIs first
    local_success = test_local_avatar_apis()
    
    # Generate Railway test plan
    test_plan = generate_railway_test_plan()
    
    # Save test plan
    with open("railway_deployment_test_plan.md", "w") as f:
        f.write(test_plan)
    
    print(f"\n📋 Railway deployment test plan saved to:")
    print(f"   railway_deployment_test_plan.md")
    
    if local_success:
        print(f"\n🚀 READY FOR RAILWAY DEPLOYMENT!")
        print(f"   All local tests passed - avatar system should work on Railway")
        print(f"   Apply Railway-safe fixes and deploy")
    else:
        print(f"\n⚠️  FIX LOCAL ISSUES FIRST")
        print(f"   Resolve failing tests before Railway deployment")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Start Flask app: python AjaSpellBApp.py")
    print(f"2. Run this test again to verify all APIs work")
    print(f"3. Apply Railway avatar fixes to AjaSpellBApp.py") 
    print(f"4. Deploy to Railway")
    print(f"5. Use railway_deployment_test_plan.md to verify deployment")
    print(f"6. Install 6 new avatars using AIS once system is stable")