#!/usr/bin/env python3

import requests
import json

def full_app_test():
    """Complete test of the app functionality with the original word list"""
    
    print("🎯 === COMPLETE APP TEST WITH PLAINWORDLIST50.TXT ===")
    
    s = requests.Session()
    
    print("1. 📁 Uploading PlainWordList50.txt...")
    try:
        with open('PlainWordList50.txt', 'r', encoding='utf-8') as f:
            files = {'file': ('PlainWordList50.txt', f, 'text/plain')}
            response = s.post('http://127.0.0.1:5000/api/upload', files=files)
            
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: Uploaded {data['count']} words!")
        else:
            print(f"   ❌ FAILED: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return
    
    print("\n2. 🎮 Testing spelling quiz with multiple words...")
    
    words_tested = 0
    words_with_definitions = 0
    words_with_patterns = 0
    
    for i in range(10):  # Test first 10 words
        try:
            response = s.get('http://127.0.0.1:5000/api/current')
            
            if response.status_code == 200:
                data = response.json()
                sentence = data.get('sentence', '')
                progress = data.get('progress', {})
                
                words_tested += 1
                word_num = progress.get('index', i+1)
                
                print(f"\n   📝 Word {word_num}:")
                print(f"      Challenge: {sentence[:80]}...")
                
                # Analyze what type of challenge this is
                if 'Fill in the blank:' in sentence and not sentence.startswith('Spell the'):
                    words_with_definitions += 1
                    print("      ✅ Full definition + example!")
                elif 'ending in' in sentence or 'starting with' in sentence:
                    words_with_patterns += 1
                    print("      ✅ Pattern recognition!")
                else:
                    print("      ⚠️  Generic format")
                
                # Submit a test answer to move to next word
                if i < 9:  # Don't submit on last word
                    submit_response = s.post('http://127.0.0.1:5000/api/submit', 
                                           json={'answer': 'testanswer'})
                    if submit_response.status_code == 200:
                        submit_data = submit_response.json()
                        actual_word = submit_data.get('expected', 'unknown')
                        print(f"      📚 Correct answer was: {actual_word}")
                    
            else:
                print(f"   ❌ Failed to get word {i+1}: {response.text}")
                break
                
        except Exception as e:
            print(f"   ❌ Error on word {i+1}: {e}")
            break
    
    print(f"\n3. 📊 RESULTS SUMMARY:")
    print(f"   • Words tested: {words_tested}")
    print(f"   • Words with full definitions: {words_with_definitions}")
    print(f"   • Words with pattern recognition: {words_with_patterns}")
    print(f"   • Success rate: {((words_with_definitions + words_with_patterns) / words_tested * 100):.1f}%")
    
    if (words_with_definitions + words_with_patterns) >= words_tested * 0.8:
        print("\n🎉 EXCELLENT! The built-in dictionary is working perfectly!")
        print("   Ready for browser testing! Go to http://127.0.0.1:5000")
    else:
        print("\n⚠️  Some issues detected. Check the dictionary coverage.")
    
    print(f"\n4. 🌐 BROWSER INSTRUCTIONS:")
    print(f"   1. Open http://127.0.0.1:5000 in your browser")
    print(f"   2. Upload 'PlainWordList50.txt' file")
    print(f"   3. Start the spelling quiz")
    print(f"   4. You should see beautiful challenges like:")
    print(f"      'A decision on an issue of fact in a civil or criminal case.'")
    print(f"      'Fill in the blank: The jury reached a _____ after three hours'")

if __name__ == "__main__":
    full_app_test()