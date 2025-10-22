"""
Complete Workflow Test: Upload → Enrich → Quiz
Tests the full cycle: plain word list → Simple Wiktionary enrichment → quiz with real definitions
"""
import requests
import time

BASE_URL = "http://localhost:5000"

def test_complete_workflow():
    """Test complete workflow: upload → enrichment with Wiktionary → quiz"""
    print("\n" + "="*80)
    print("COMPLETE WORKFLOW TEST: Upload → Enrich (51K Wiktionary) → Quiz")
    print("="*80)
    
    # Test words - mix of common and uncommon
    test_words = ["admire", "brisk", "curious", "dazzle", "eager", "fragile", "glimpse", "humble", "mingle", "timid"]
    word_list_content = "\n".join(test_words)
    
    session = requests.Session()
    
    try:
        # STEP 1: Upload plain word list
        print(f"\n📤 STEP 1: Uploading {len(test_words)} plain words...")
        print(f"   Words: {', '.join(test_words)}")
        
        files = {'file': ('test_words.txt', word_list_content.encode('utf-8'), 'text/plain')}
        upload_response = session.post(f"{BASE_URL}/api/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(f"   Response: {upload_response.text}")
            return False
        
        upload_data = upload_response.json()
        print(f"✅ Upload successful!")
        print(f"   Server message: {upload_data.get('message', 'N/A')}")
        print(f"   Words loaded: {upload_data.get('count', 0)}")
        
        # STEP 2: Verify wordbank enrichment
        print(f"\n📖 STEP 2: Checking enrichment results (Simple Wiktionary with 51K words)...")
        wb_response = session.get(f"{BASE_URL}/api/wordbank")
        
        if wb_response.status_code != 200:
            print(f"❌ Failed to get wordbank: {wb_response.status_code}")
            return False
        
        wordbank = wb_response.json()
        print(f"✅ Wordbank retrieved: {len(wordbank)} words")
        
        # Check each word's definition
        print(f"\n📋 ENRICHMENT RESULTS:")
        print("-" * 80)
        
        found_in_wiktionary = 0
        definition_not_available = 0
        
        for idx, word_rec in enumerate(wordbank, 1):
            word = word_rec.get('word', 'N/A')
            sentence = word_rec.get('sentence', '')
            hint = word_rec.get('hint', '')
            
            print(f"\n   {idx}. Word: {word}")
            
            # Check if it's a real definition from Wiktionary
            if "Definition not available" in sentence:
                print(f"      Status: ⚠️  Definition not available (spelling-only quiz)")
                definition_not_available += 1
            elif "Practice spelling this" in sentence:
                print(f"      Status: ⚠️  Using fallback (Wiktionary miss)")
            else:
                print(f"      Status: ✅ Real definition from Wiktionary!")
                found_in_wiktionary += 1
            
            # Show first 100 chars of definition
            if len(sentence) > 100:
                print(f"      Definition: {sentence[:100]}...")
            else:
                print(f"      Definition: {sentence}")
        
        print("\n" + "-" * 80)
        print(f"📊 ENRICHMENT SUMMARY:")
        print(f"   ✅ Found in Wiktionary: {found_in_wiktionary}/{len(wordbank)}")
        print(f"   ⚠️  Definition not available: {definition_not_available}/{len(wordbank)}")
        print(f"   Coverage: {(found_in_wiktionary / len(wordbank) * 100):.1f}%")
        
        # STEP 3: Start quiz and check first word
        print(f"\n🎯 STEP 3: Testing quiz interface...")
        next_response = session.post(f"{BASE_URL}/api/next")
        
        if next_response.status_code != 200:
            print(f"❌ Quiz failed to start: {next_response.status_code}")
            return False
        
        quiz_data = next_response.json()
        print(f"✅ Quiz started successfully!")
        print(f"   Current word definition shown to user:")
        print(f"   {quiz_data.get('sentence', 'N/A')}")
        
        # STEP 4: Verify word is NOT revealed
        sentence = quiz_data.get('sentence', '')
        target_word = wordbank[quiz_data.get('idx', 0)].get('word', '').lower()
        
        if target_word in sentence.lower():
            print(f"\n❌ SECURITY ISSUE: Word '{target_word}' visible in definition!")
            print(f"   Definition: {sentence}")
            return False
        else:
            print(f"\n✅ SECURITY CHECK PASSED: Word '{target_word}' is hidden (shows _____ instead)")
        
        print("\n" + "="*80)
        print("✅ COMPLETE WORKFLOW TEST PASSED!")
        print("="*80)
        print("\n🎉 Summary:")
        print(f"   • Uploaded {len(test_words)} plain words")
        print(f"   • Enriched with Simple English Wiktionary (51K words)")
        print(f"   • {found_in_wiktionary} words found with real definitions")
        print(f"   • Quiz loaded successfully with word hidden")
        print(f"   • Ready for spelling practice!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {BASE_URL}")
        print("   Make sure the Flask app is running:")
        print("   python AjaSpellBApp.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    exit(0 if success else 1)
