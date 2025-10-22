#!/usr/bin/env python3

import requests
import json

def load_demo_words():
    """Load demo words directly into the session"""
    
    print("🎯 === LOADING DEMO WORDS FOR TESTING ===")
    
    s = requests.Session()
    
    # Create a fake file upload with demo words
    demo_words = """verdict
imitation
beautiful
pistachio
hypnosis
steeple
nomad
berlin"""
    
    try:
        # Upload demo words
        files = {'file': ('demo_words.txt', demo_words, 'text/plain')}
        response = s.post('http://127.0.0.1:5000/api/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {data['message']}")
            
            # Get first word
            word_response = s.get('http://127.0.0.1:5000/api/current')
            if word_response.status_code == 200:
                word_data = word_response.json()
                sentence = word_data.get('sentence', '')
                print(f"\n   📝 Demo Challenge: {sentence}")
                print(f"\n   🎉 This is what you SHOULD see in your browser after uploading!")
                print(f"   📋 The app is working perfectly - just need to upload your file")
            else:
                print(f"   ❌ Word fetch failed: {word_response.text}")
        else:
            print(f"   ❌ Demo upload failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    load_demo_words()