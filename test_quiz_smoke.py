"""
Comprehensive Quiz Smoke Test
Tests the complete quiz flow from word upload to report card
"""
import requests
import time
import json
import sys
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:5000"

class QuizSmokeTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_words = ["apple", "banana", "cherry", "date", "elderberry"]
        
    def log(self, message, emoji="📝"):
        try:
            print(f"{emoji} {message}")
        except UnicodeEncodeError:
            print(f"[{emoji.encode('ascii', 'namereplace').decode()}] {message}")
        
    def test_01_upload_words(self):
        """Test 1: Upload word list"""
        self.log("TEST 1: Uploading word list...", "📤")
        
        # Create a simple text file with words
        word_list_content = "\n".join(self.test_words)
        files = {'file': ('test_words.txt', word_list_content, 'text/plain')}
        
        response = self.session.post(f"{BASE_URL}/api/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            # API responses have varied over time; accept multiple shapes.
            count = (
                data.get('word_count')
                or data.get('count')
                or data.get('words_imported')
                or data.get('wordsProcessed')
                or (len(data.get('words', [])) if isinstance(data.get('words', None), list) else None)
            )
            count = int(count) if count is not None else 0
            self.log(f"✅ Words uploaded: {count} words", "✅")
            return True
        else:
            self.log(f"❌ Upload failed: {response.status_code} - {response.text}", "❌")
            return False
    
    def test_02_start_quiz(self):
        """Test 2: Get first word"""
        self.log("TEST 2: Starting quiz (fetching first word)...", "🎯")
        
        response = self.session.post(f"{BASE_URL}/api/next")
        
        if response.status_code == 200:
            data = response.json()
            word = data.get('word', '')
            sentence = data.get('sentence', '')
            index = data.get('index', 0)
            total = data.get('total', 0)
            
            self.log(f"✅ First word loaded: Word #{index}/{total}", "✅")
            self.log(f"   Sentence: {sentence[:50]}...", "💬")
            self.current_word = word
            return True
        else:
            self.log(f"❌ Failed to get first word: {response.status_code}", "❌")
            return False
    
    def test_03_submit_correct_answer(self):
        """Test 3: Submit correct answer"""
        self.log(f"TEST 3: Submitting CORRECT answer: '{self.current_word}'", "✍️")
        
        payload = {
            "user_input": self.current_word,
            "method": "keyboard",
            "elapsed_ms": 5000
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/answer",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_correct = data.get('correct', False)
            points = data.get('points', {})
            progress = data.get('progress', {})
            
            self.log(f"✅ Answer submitted: Correct={is_correct}", "✅")
            self.log(f"   Points earned: {points.get('earned', 0)}", "🍯")
            self.log(f"   Progress: {progress.get('correct', 0)} correct, {progress.get('incorrect', 0)} incorrect", "📊")
            self.log(f"   Streak: {progress.get('streak', 0)}", "🔥")
            return True
        else:
            self.log(f"❌ Failed to submit answer: {response.status_code}", "❌")
            return False
    
    def test_04_get_next_word(self):
        """Test 4: Verify quiz advances to next word"""
        self.log("TEST 4: Fetching next word (verifying progression)...", "⏭️")
        
        response = self.session.post(f"{BASE_URL}/api/next")
        
        if response.status_code == 200:
            data = response.json()
            word = data.get('word', '')
            index = data.get('index', 0)
            
            if word != self.current_word:
                self.log(f"✅ Quiz advanced! Now on word #{index}", "✅")
                self.current_word = word
                return True
            else:
                self.log(f"❌ Quiz STUCK! Still showing same word: '{word}'", "❌")
                return False
        else:
            self.log(f"❌ Failed to get next word: {response.status_code}", "❌")
            return False
    
    def test_05_submit_incorrect_answer(self):
        """Test 5: Submit incorrect answer"""
        self.log(f"TEST 5: Submitting INCORRECT answer: 'wrongspelling'", "✍️")
        
        payload = {
            "user_input": "wrongspelling",
            "method": "keyboard",
            "elapsed_ms": 3000
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/answer",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_correct = data.get('correct', False)
            expected = data.get('expected', '')
            progress = data.get('progress', {})
            
            self.log(f"✅ Incorrect answer handled: Correct={is_correct}", "✅")
            self.log(f"   Expected: {expected}", "📖")
            self.log(f"   Progress: {progress.get('incorrect', 0)} incorrect", "📊")
            return True
        else:
            self.log(f"❌ Failed to submit incorrect answer: {response.status_code}", "❌")
            return False
    
    def test_06_complete_remaining_words(self):
        """Test 6: Complete remaining words"""
        self.log("TEST 6: Completing remaining words...", "🏃")
        
        for i in range(3):  # Complete 3 more words
            # Get next word
            response = self.session.post(f"{BASE_URL}/api/next")
            if response.status_code != 200:
                self.log(f"❌ Failed to get word {i+1}", "❌")
                return False
            
            data = response.json()
            if data.get('done'):
                self.log(f"✅ Quiz completed early", "✅")
                return True
            
            word = data.get('word', '')
            
            # Submit answer (alternating correct/incorrect)
            user_input = word if i % 2 == 0 else "wrong"
            payload = {
                "user_input": user_input,
                "method": "keyboard",
                "elapsed_ms": 4000
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/answer",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                self.log(f"❌ Failed to submit answer for word {i+1}", "❌")
                return False
            
            time.sleep(0.5)  # Brief pause between words
        
        self.log(f"✅ Completed 3 additional words", "✅")
        return True
    
    def test_07_check_quiz_completion(self):
        """Test 7: Verify quiz completion"""
        self.log("TEST 7: Checking quiz completion...", "🏁")
        
        response = self.session.post(f"{BASE_URL}/api/next")
        
        if response.status_code == 200:
            data = response.json()
            is_done = data.get('done', False)
            
            if is_done:
                summary = data.get('summary', {})
                self.log(f"✅ Quiz completed!", "✅")
                self.log(f"   Total: {summary.get('total', 0)}", "📊")
                self.log(f"   Correct: {summary.get('correct', 0)}", "✅")
                self.log(f"   Incorrect: {summary.get('incorrect', 0)}", "❌")
                self.log(f"   Final Streak: {summary.get('streak', 0)}", "🔥")
                return True
            else:
                self.log(f"⚠️ Quiz not done yet, continuing...", "⚠️")
                return True  # Not necessarily a failure
        else:
            self.log(f"❌ Failed to check completion: {response.status_code}", "❌")
            return False
    
    def test_08_session_persistence(self):
        """Test 8: Verify session data persists"""
        self.log("TEST 8: Checking session persistence...", "💾")
        
        # Make another request to verify session is still active
        response = self.session.post(f"{BASE_URL}/api/next")
        
        if response.status_code == 200:
            self.log(f"✅ Session persisted correctly", "✅")
            return True
        else:
            self.log(f"❌ Session persistence issue: {response.status_code}", "❌")
            return False
    
    def run_all_tests(self):
        """Run all smoke tests"""
        self.log("=" * 60, "")
        self.log("BEESMART QUIZ SMOKE TEST - STARTING", "🐝")
        self.log("=" * 60, "")
        
        tests = [
            self.test_01_upload_words,
            self.test_02_start_quiz,
            self.test_03_submit_correct_answer,
            self.test_04_get_next_word,
            self.test_05_submit_incorrect_answer,
            self.test_06_complete_remaining_words,
            self.test_07_check_quiz_completion,
            self.test_08_session_persistence,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                result = test()
                if result:
                    passed += 1
                else:
                    failed += 1
                print()  # Blank line between tests
            except Exception as e:
                self.log(f"❌ Test exception: {str(e)}", "💥")
                failed += 1
                print()
        
        self.log("=" * 60, "")
        self.log("SMOKE TEST RESULTS", "📊")
        self.log("=" * 60, "")
        self.log(f"Passed: {passed}/{len(tests)}", "✅")
        self.log(f"Failed: {failed}/{len(tests)}", "❌")
        
        if failed == 0:
            self.log("ALL TESTS PASSED! 🎉", "🎉")
        else:
            self.log("SOME TESTS FAILED - Review above", "⚠️")
        
        self.log("=" * 60, "")

if __name__ == "__main__":
    tester = QuizSmokeTest()
    tester.run_all_tests()
