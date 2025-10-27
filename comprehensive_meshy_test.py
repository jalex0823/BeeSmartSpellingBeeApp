#!/usr/bin/env python3
"""
Comprehensive Meshy API Test - PING, RETRIEVE, REFLECT, STOP
Tests both API keys with all endpoints and displays results for selection
"""

import requests
import json
import sys
from datetime import datetime

def ping_retrieve_reflect_stop():
    """Main function: Ping, Retrieve, Reflect, Stop"""
    
    print("🚀 MESHY API COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # API Keys to test
    api_keys = {
        "SmartBee1": "msy_0jQRvISvIBalOTBI4BBoR5DjTYTwW95pa1RS",
        "SmartBee2": "msy_VCJPHtPz6SqlulrYNcEBiVhecWChB9aQv3zV"
    }
    
    # All possible endpoints to test
    endpoints = [
        'https://api.meshy.ai/openapi/v1/image-to-3d',
        'https://api.meshy.ai/openapi/v2/text-to-3d', 
        'https://api.meshy.ai/openapi/v1/text-to-3d',
        'https://api.meshy.ai/openapi/v2/image-to-3d',
        'https://api.meshy.ai/openapi/v1/text-to-texture',
        'https://api.meshy.ai/v1/image-to-3d',
        'https://api.meshy.ai/v2/text-to-3d',
        'https://api.meshy.ai/v1/text-to-3d',
        'https://api.meshy.ai/v2/image-to-3d',
        'https://api.meshy.ai/v1/text-to-texture'
    ]
    
    all_results = {}
    
    # Test each API key
    for key_name, api_key in api_keys.items():
        print(f"🔑 TESTING API KEY: {key_name}")
        print(f"   Key: {api_key[:8]}...{api_key[-4:]}")
        print("-" * 40)
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        key_results = {}
        
        # Test each endpoint
        for endpoint in endpoints:
            try:
                print(f"📡 PING: {endpoint}")
                response = requests.get(endpoint, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Handle different response structures
                        projects = []
                        if isinstance(data, list):
                            projects = data
                        elif isinstance(data, dict):
                            # Try common container keys
                            for key in ['result', 'data', 'tasks', 'projects', 'items']:
                                if key in data and isinstance(data[key], list):
                                    projects = data[key]
                                    break
                        
                        print(f"   ✅ SUCCESS: Found {len(projects)} items")
                        
                        if len(projects) > 0:
                            key_results[endpoint] = {
                                'count': len(projects),
                                'projects': projects,
                                'sample_keys': list(projects[0].keys()) if projects else []
                            }
                            print(f"   📋 Sample keys: {list(projects[0].keys())[:5]}")
                            
                    except json.JSONDecodeError:
                        print(f"   ⚠️ Invalid JSON response")
                        
                elif response.status_code == 401:
                    print(f"   ❌ UNAUTHORIZED")
                elif response.status_code == 404:
                    print(f"   ❌ NOT FOUND")
                else:
                    print(f"   ❌ ERROR {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {str(e)}")
        
        all_results[key_name] = key_results
        print()
    
    # REFLECT - Display comprehensive results
    print("🔍 REFLECTION - COMPREHENSIVE RESULTS")
    print("=" * 60)
    
    total_projects_found = 0
    successful_connections = []
    
    for key_name, key_results in all_results.items():
        print(f"\n📊 {key_name} RESULTS:")
        if key_results:
            for endpoint, data in key_results.items():
                count = data['count']
                total_projects_found += count
                print(f"   ✅ {endpoint}: {count} projects")
                successful_connections.append({
                    'key': key_name,
                    'endpoint': endpoint,
                    'count': count,
                    'projects': data['projects']
                })
        else:
            print(f"   ❌ No projects found with any endpoint")
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Total Projects Found: {total_projects_found}")
    print(f"   Successful Connections: {len(successful_connections)}")
    
    if successful_connections:
        print(f"\n📦 AVAILABLE FOR SELECTION:")
        for i, conn in enumerate(successful_connections, 1):
            print(f"   {i}. {conn['key']} → {conn['endpoint']} ({conn['count']} projects)")
            
        # Show detailed project info for first successful connection
        if successful_connections[0]['projects']:
            print(f"\n📋 SAMPLE PROJECT DETAILS:")
            sample = successful_connections[0]['projects'][0]
            for key, value in sample.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"   {key}: {value}")
                
        # Save results to file for GUI integration
        results_file = "meshy_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_projects': total_projects_found,
                'successful_connections': successful_connections,
                'all_results': all_results
            }, f, indent=2)
        print(f"\n💾 Results saved to: {results_file}")
        
    else:
        print(f"\n❌ NO PROJECTS FOUND")
        print(f"   Both API keys returned 0 projects from all endpoints")
        print(f"   Possible causes:")
        print(f"   1. Projects are in a different Meshy account")
        print(f"   2. Projects use different API endpoints")
        print(f"   3. Account might be using different API version")
    
    # STOP
    print(f"\n🛑 STOPPING")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return successful_connections

if __name__ == "__main__":
    try:
        results = ping_retrieve_reflect_stop()
        if results:
            print(f"✅ Found {len(results)} successful connections with projects!")
        else:
            print(f"❌ No projects found in any tested endpoints")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
    
    sys.exit(0)