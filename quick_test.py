#!/usr/bin/env python3
"""
Quick verification of current app functionality
"""

import urllib.request
import json
import time
import http.cookiejar

def quick_test():
    print("🔄 QUICK REFRESH TEST")
    print("=" * 50)
    
    # Create fresh session
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    urllib.request.install_opener(opener)
    
    # Upload word list in your exact format
    test_content = """verdict|The final decision made by a judge or jury. Example: The _____ was announced at the end of the trial.|
suspicious|Feeling that something or someone is not quite right. Example: He looked _____ when hiding the paper behind his back.|
Berlin|The capital city of Germany. Example: We saw pictures of _____ in our geography book.|"""
    
    # Upload
    boundary = '----WebKitFormBoundary' + str(int(time.time()))
    body_lines = ['--' + boundary,
                  'Content-Disposition: form-data; name="file"; filename="test.txt"',
                  'Content-Type: text/plain', '', test_content, '--' + boundary + '--']
    body = '\r\n'.join(body_lines).encode('utf-8')
    
    req = urllib.request.Request('http://127.0.0.1:5000/api/upload')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.data = body
    
    try:
        response = opener.open(req)
        result = json.loads(response.read().decode())
        print(f"✅ Upload: {result.get('count')} words")
        
        # Get current challenge
        response = opener.open('http://127.0.0.1:5000/api/current')
        result = json.loads(response.read().decode())
        
        challenge = result.get('sentence', '')
        print(f"\n📝 Current Challenge:")
        print(f"'{challenge}'")
        
        # Analyze what we got
        if "Fill in the blank:" in challenge:
            print("✅ SUCCESS: New format working!")
        elif "Spell the word that means:" in challenge:
            print("⚠️  OLD FORMAT: Basic definition only")
        elif "Spell this" in challenge and "letter word" in challenge:
            print("❌ PROBLEM: Still showing generic message")
        else:
            print(f"❓ UNKNOWN: {challenge}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_test()