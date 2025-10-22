#!/usr/bin/env python3

import requests

def test_upload_simple():
    """Simple test of upload API"""
    try:
        print("🔄 Testing upload API...")
        
        # Open the file and upload it
        with open('PlainWordList50.txt', 'rb') as f:
            files = {'file': f}
            response = requests.post('http://127.0.0.1:5000/api/upload', files=files)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Upload test successful!")
        else:
            print("❌ Upload test failed!")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_upload_simple()