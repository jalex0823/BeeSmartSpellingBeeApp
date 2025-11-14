#!/usr/bin/env python3
"""
Test that the API returns Apple Store compliant names with " Avatar" suffix
"""

import sys
sys.path.insert(0, '.')

from AjaSpellBApp import app
import json

with app.test_client() as client:
    response = client.get('/api/avatars')
    data = response.get_json()
    
    if data['status'] == 'success':
        avatars = data['avatars']
        print(f"✅ API returned {len(avatars)} avatars")
        print()
        print("Checking Apple Store name compliance (all should end with ' Avatar'):")
        print("-" * 80)
        
        compliant = []
        non_compliant = []
        
        for av in sorted(avatars, key=lambda x: x['name']):
            name = av['name']
            avatar_id = av['id']
            
            if name.endswith(' Avatar'):
                compliant.append(name)
                status = "✅"
            else:
                non_compliant.append({'id': avatar_id, 'name': name})
                status = "❌"
            
            print(f"{status} {avatar_id:<20} → {name}")
        
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total avatars: {len(avatars)}")
        print(f"Compliant names: {len(compliant)}")
        print(f"Non-compliant: {len(non_compliant)}")
        
        if non_compliant:
            print()
            print("⚠️ NON-COMPLIANT NAMES:")
            for item in non_compliant:
                print(f"  • {item['id']}: '{item['name']}'")
        else:
            print()
            print("✅ ALL NAMES ARE APPLE STORE COMPLIANT!")
    else:
        print(f"❌ API error: {data.get('message', 'Unknown error')}")
