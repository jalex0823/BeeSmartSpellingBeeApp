#!/usr/bin/env python3
""" 
BeeSmart Spelling App - Complete Feature Validation Test
Tests all P0 features including new OCR functionality and UI components
"""

import unittest
import json
import sys
import os
import time
import requests

# Add the app directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, normalize, get_word_info, generate_smart_fallback, OCR_AVAILABLE


class TestCompleteApp(unittest.TestCase):
    """Test complete v1.6 application functionality"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page_modern_ui(self):
        """Test that home page loads with modern UI elements"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.data.decode('utf-8')
        
        # Check for modern UI elements
        modern_elements = [
            'Upload Word List',
            'Extract from Image', 
            'Start Quiz',
            'fairy-container',  # Animation element
            'menu-card',  # Modern card design
            'BeeSmart Spelling',  # Title
            'v1.6'  # Version badge
        ]
        
        for element in modern_elements:
            with self.subTest(element=element):
                self.assertIn(element, html_content, 
                    f"Modern UI element '{element}' not found in home page")

    def test_quiz_page_loads(self):
        """Test that quiz page loads successfully"""
        # Ensure a valid wordbank exists by using the public upload API (establishes session context)
        test_words = [{"word": "test", "sentence": "", "hint": ""}]
        upload = self.app.post(
            '/api/upload',
            data=json.dumps({'words': test_words}),
            content_type='application/json'
        )
        self.assertEqual(upload.status_code, 200)

        response = self.app.get('/quiz', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        html_content = response.data.decode('utf-8')
        
        # Check for stable quiz elements.
        # NOTE: UI copy and button labels evolve; keep this test resilient.
        stable_markers = [
            'quiz-container',
            'quiz-shell'
        ]
        for element in stable_markers:
            with self.subTest(element=element):
                self.assertIn(element, html_content,
                    f"Quiz element '{element}' not found in quiz page")

    def test_test_page_functionality(self):
        """Test that test page loads and works"""
        response = self.app.get('/test')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.data.decode('utf-8')
        self.assertIn('BeeSmart Test Page', html_content)
        self.assertIn('Test Wordbook API', html_content)

    def test_upload_image_endpoint_availability(self):
        """Test that image upload endpoint is available"""
        # Test with no file
        response = self.app.get('/api/upload/image')
        
        # Should return error about no file, but endpoint should exist
        self.assertIn(response.status_code, [200, 405])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('status', data)
            print(f"✅ Image upload endpoint available: {data['message']}")
        else:
            print("ℹ️ Image upload endpoint may not be fully configured (got 405)")

    def test_ocr_availability_status(self):
        """Test OCR availability status"""
        if OCR_AVAILABLE:
            print("✅ OCR libraries are available")
            
            # Test image upload endpoint when OCR is available
            response = self.app.get('/api/upload/image')
            self.assertEqual(response.status_code, 200)  # GET should now be OK
            
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'ready')
        else:
            print("⚠️ OCR libraries not available - image upload will show appropriate error")
            
            # Test that endpoint returns proper error
            response = self.app.get('/api/upload/image')
            self.assertEqual(response.status_code, 501)
            
            data = json.loads(response.data)
            self.assertIn('OCR (image upload) is not available', data['message'])

    def test_complete_upload_to_quiz_workflow(self):
        """Test complete workflow: upload words → quiz → answer"""
        # Step 1: Upload words via JSON
        test_words = [
            {"word": "rainbow", "sentence": "", "hint": ""},
            {"word": "butterfly", "sentence": "", "hint": ""},
            {"word": "adventure", "sentence": "", "hint": ""}
        ]
        
        response = self.app.post('/api/upload', 
                                   data=json.dumps({'words': test_words}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertTrue(result['ok'])
        self.assertEqual(result['count'], 3)
        print(f"✅ Uploaded {result['count']} words successfully")
        
        # Step 2: Start quiz
        response = self.app.post('/api/next')
        self.assertEqual(response.status_code, 200)
        
        quiz_data = json.loads(response.data)
        self.assertFalse(quiz_data['done'])
        self.assertEqual(quiz_data['index'], 1)
        self.assertEqual(quiz_data['total'], 3)
        print(f"✅ Quiz started: Question {quiz_data['index']} of {quiz_data['total']}")

        # Step 3: Load quiz page (should render)
        quiz_page = self.app.get('/quiz', follow_redirects=True)
        self.assertEqual(quiz_page.status_code, 200)

        # Step 4: Get definition fallback string for the word.
        # This app's definition orchestration is exposed via the internal helper `get_word_info()`.
        # (There is no stable public /api/definition endpoint in this codebase.)
        
        current_word = quiz_data.get('word', '')
        self.assertTrue(isinstance(current_word, str) and current_word.strip(), "Quiz response did not include a word")
        definition_text = get_word_info(current_word)
        self.assertIsInstance(definition_text, str)
        self.assertGreater(len(definition_text.strip()), 5)
        # Security: the returned definition/sentence should not reveal the answer.
        self.assertNotIn(current_word.lower(), definition_text.lower())
        print(f"✅ Definition retrieved (no word exposed): {definition_text[:50]}...")
        
        # Step 5: Submit correct answer for the word actually served by /api/next
        # (The quiz randomizes/shuffles; don't assume ordering.)
        correct_word = current_word
        response = self.app.post('/api/answer',
                               json={
                                   'user_input': correct_word,
                                   'method': 'keyboard',
                                   'elapsed_ms': 1000
                               },
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        answer_data = json.loads(response.data)
        self.assertTrue(answer_data['correct'])
        self.assertEqual(answer_data['progress']['correct'], 1)
        print(f"✅ Correct answer submitted: {answer_data['feedback_message']}")

    def test_dictionary_cache_integration(self):
        """Test dictionary cache system"""
        # Test word info retrieval
        test_word = "example"
        definition = get_word_info(test_word)
        
        self.assertIsInstance(definition, str)
        self.assertTrue(len(definition) > 10)  # Should have meaningful content
        print(f"✅ Dictionary lookup working: '{test_word}' → {definition[:50]}...")

    def test_error_handling_and_validation(self):
        """Test error handling for various edge cases"""
        # Test quiz start without words
        # Clear any existing words (the endpoint expects JSON)
        self.app.post('/api/clear', json={})
        
        response = self.app.post('/api/next')
        self.assertEqual(response.status_code, 400)
        
        error_data = json.loads(response.data)
        # Current API returns {error, message, action_required}; older versions used 'status'
        self.assertIn('error', error_data)
        self.assertIn('message', error_data)
        self.assertIn('action_required', error_data)
        print(f"✅ Proper error handling: {error_data['message']}")

    def test_session_management(self):
        """Test session state management"""
        # Test session debug endpoint
        response = self.app.get('/api/session_debug')
        self.assertEqual(response.status_code, 200)
        
        debug_data = json.loads(response.data)
        self.assertIn('wordbank_count', debug_data)
        self.assertIn('session_keys', debug_data)
        print(f"✅ Session management working: {debug_data['wordbank_count']} words in session")

    def test_health_check_comprehensive(self):
        """Test comprehensive health check"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        health_data = json.loads(response.data)
        self.assertEqual(health_data['status'], 'ok')
        # App version bumped
        self.assertEqual(health_data['version'], '1.7')
        # The health endpoint intentionally stays lightweight in production.
        # Deeper diagnostics live under /api/debug/* endpoints.
        print(f"✅ Health check ok: {health_data['status']} v{health_data['version']}")


class TestFeatureCompleteness(unittest.TestCase):
    """Test feature completeness against P0 requirements"""
    
    def test_p0_core_features_implemented(self):
        """Verify all P0 core features are implemented"""
        client = app.test_client()
        
        # Test all required endpoints exist
        required_endpoints = [
            ('/', 'GET'),           # Main menu
            ('/quiz', 'GET'),       # Quiz page
            ('/test', 'GET'),       # Test page
            ('/health', 'GET'),     # Health check
            ('/api/upload', 'POST'),        # File upload
            ('/api/upload/image', 'GET'),  # Check availability via GET
            ('/api/wordbank', 'GET'),       # Word bank
            ('/api/next', 'POST'),          # Quiz next
            ('/api/answer', 'POST'),        # Submit answer
            ('/api/pronounce', 'POST'),     # Get definition
            ('/api/reset', 'POST'),         # Reset quiz
            ('/api/build_dictionary', 'POST'), # Dictionary builder
        ]
        
        results = []
        for endpoint, method in required_endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            # Any response (even 400) means endpoint exists
            exists = response.status_code != 404
            results.append((endpoint, method, exists, response.status_code))
        
        # Print results
        print("\n🔍 P0 Endpoint Availability Check:")
        for endpoint, method, exists, status in results:
            status_icon = "✅" if exists else "❌"
            print(f"  {status_icon} {method:4} {endpoint:25} → {status}")
        
        # Assert all endpoints exist
        missing_endpoints = [(e, m) for e, m, exists, _ in results if not exists]
        self.assertEqual(len(missing_endpoints), 0, 
                        f"Missing endpoints: {missing_endpoints}")

    def test_p0_file_format_support(self):
        """Test P0 file format support"""
        formats_tested = []
        
        # Test text upload
        try:
            from AjaSpellBApp import parse_txt
            test_content = b"word1\nword2\nword3"
            result = parse_txt(test_content)
            formats_tested.append(("TXT", True, len(result)))
        except Exception as e:
            formats_tested.append(("TXT", False, str(e)))
        
        # Test CSV upload
        try:
            from AjaSpellBApp import parse_csv
            test_content = b"word,sentence,hint\ntest,example,clue"
            result = parse_csv(test_content, "test.csv")
            formats_tested.append(("CSV", True, len(result)))
        except Exception as e:
            formats_tested.append(("CSV", False, str(e)))
        
        # Test DOCX availability
        try:
            import docx
            formats_tested.append(("DOCX", True, "Available"))
        except ImportError:
            formats_tested.append(("DOCX", False, "Not installed"))
        
        # Test OCR availability
        try:
            import pytesseract
            from PIL import Image
            formats_tested.append(("OCR", True, "Available"))
        except ImportError:
            formats_tested.append(("OCR", False, "Not installed"))
        
        print("\n📁 File Format Support:")
        for format_name, supported, details in formats_tested:
            icon = "✅" if supported else "⚠️"
            print(f"  {icon} {format_name:4} → {details}")
        
        # At minimum, TXT and CSV should work
        txt_works = any(f[0] == "TXT" and f[1] for f in formats_tested)
        csv_works = any(f[0] == "CSV" and f[1] for f in formats_tested)
        
        self.assertTrue(txt_works, "TXT format support required")
        self.assertTrue(csv_works, "CSV format support required")


def run_comprehensive_test():
    """Run all tests and provide detailed report"""
    print("🐝 BeeSmart Spelling App v1.6")
    print("=" * 60)
    print("🧪 COMPREHENSIVE FEATURE VALIDATION")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCompleteApp))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureCompleteness))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 VALIDATION SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Tests Run: {total_tests}")
    print(f"Successes: {total_tests - failures - errors}")
    print(f"Failures: {failures}")  
    print(f"Errors: {errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failures == 0 and errors == 0:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        print("✅ BeeSmart v1.6 is ready for deployment!")
    else:
        print(f"\n⚠️ {failures + errors} issues found:")
        for test, error in result.failures + result.errors:
            print(f"  ❌ {test}: {error.split('AssertionError:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)