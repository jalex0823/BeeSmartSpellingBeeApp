#!/usr/bin/env python3
"""
Simple test to verify dictionary integration works
"""
import requests
import json

def test_basic_upload():
    """Test uploading a simple word list"""
    print("🧪 Testing basic word list upload with dictionary integration...")
    
    # Test with simple words that should be in the dictionary
    word_list = {
        "words": [
            {"word": "verdict", "sentence": "", "hint": ""},
            {"word": "beautiful", "sentence": "", "hint": ""},
            {"word": "elephant", "sentence": "", "hint": ""}
        ]
    }
    
    try:
        response = requests.post("http://127.0.0.1:5000/api/upload", json=word_list)
        print(f"Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful: {data}")
            
            # Check wordbank
            wb_response = requests.get("http://127.0.0.1:5000/api/wordbank")
            print(f"Wordbank response status: {wb_response.status_code}")
            
            if wb_response.status_code == 200:
                wb_data = wb_response.json()
                print(f"✅ Wordbank retrieved: {len(wb_data.get('words', []))} words")
                
                for word in wb_data.get('words', []):
                    print(f"  - {word.get('word')}: '{word.get('sentence', 'NO SENTENCE')}'")
            else:
                print(f"❌ Wordbank failed: {wb_response.text}")
        else:
            print(f"❌ Upload failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_basic_upload()