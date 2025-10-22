"""
Test enrichment process with debug logging
"""
import sys
import requests
import time

# Test server URL
BASE_URL = "http://localhost:5000"

def test_plain_word_upload():
    """Test uploading plain words (no definitions) to see enrichment process"""
    print("\n" + "="*60)
    print("Testing Plain Word Upload with Enrichment Debug Logging")
    print("="*60)
    
    # Create a simple word list
    test_words = ["admire", "brisk", "curious"]
    word_list_content = "\n".join(test_words)
    
    # Upload as text file
    print(f"\n📤 Uploading {len(test_words)} plain words: {', '.join(test_words)}")
    
    files = {
        'file': ('test_words.txt', word_list_content.encode('utf-8'), 'text/plain')
    }
    
    session = requests.Session()
    
    try:
        response = session.post(f"{BASE_URL}/api/upload", files=files)
        print(f"\n📡 Upload Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   Words loaded: {data.get('count', 0)}")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            # Check wordbank to see what was stored
            print("\n🔍 Checking wordbank to see enrichment results...")
            wb_response = session.get(f"{BASE_URL}/api/wordbank")
            
            if wb_response.status_code == 200:
                wordbank = wb_response.json()
                print(f"\n📚 Wordbank contains {len(wordbank)} words:")
                
                for idx, word_rec in enumerate(wordbank, 1):
                    word = word_rec.get('word', 'N/A')
                    sentence = word_rec.get('sentence', '')
                    hint = word_rec.get('hint', '')
                    
                    print(f"\n   Word {idx}: {word}")
                    print(f"   Sentence: {sentence[:100]}{'...' if len(sentence) > 100 else ''}")
                    print(f"   Hint: {hint[:50]}{'...' if len(hint) > 50 else ''}")
                    
                    # Check if it's a fallback or real definition
                    if "Practice spelling this" in sentence:
                        print(f"   ⚠️  WARNING: Still showing fallback!")
                    else:
                        print(f"   ✅ Real definition loaded!")
            else:
                print(f"❌ Failed to get wordbank: {wb_response.status_code}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {BASE_URL}")
        print("   Make sure the Flask app is running:")
        print("   python AjaSpellBApp.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    print("\n" + "="*60)
    print("⚠️  CHECK YOUR SERVER CONSOLE for debug output!")
    print("="*60)
    print("\nLook for messages like:")
    print("   DEBUG /api/upload: Enriching 'admire' (no sentence/hint provided)...")
    print("   🔍 Looking up 'admire' via API...")
    print("   DEBUG get_word_info: API returned for 'admire': {...}")
    print("   ✅ API returned definition for 'admire'")
    print("="*60)

if __name__ == "__main__":
    test_plain_word_upload()
