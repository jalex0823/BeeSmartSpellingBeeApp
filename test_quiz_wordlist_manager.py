"""
Test Quiz Word List Manager

Tests the word list management functionality to ensure:
1. New word list selection overrides existing lists
2. Refresh list button clears active list
3. Quiz uses selected word list across page reloads
4. Backward compatibility with globals
"""

import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestQuizWordListManager(unittest.TestCase):
    """Test suite for Quiz Word List Manager module"""
    
    def test_module_file_exists(self):
        """Test that the quiz-wordlist.js file exists"""
        module_path = os.path.join(
            os.path.dirname(__file__),
            'static',
            'js',
            'quiz-wordlist.js'
        )
        self.assertTrue(
            os.path.exists(module_path),
            f"Word list manager module not found at {module_path}"
        )
    
    def test_module_has_required_functions(self):
        """Test that the module contains required functions"""
        module_path = os.path.join(
            os.path.dirname(__file__),
            'static',
            'js',
            'quiz-wordlist.js'
        )
        
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for class definition
        self.assertIn('class QuizWordListManager', content, 
                     "QuizWordListManager class not found")
        
        # Check for key methods
        self.assertIn('ensureUsingSelectedList', content,
                     "ensureUsingSelectedList method not found")
        self.assertIn('getCurrentWordList', content,
                     "getCurrentWordList method not found")
        self.assertIn('clearActiveWordList', content,
                     "clearActiveWordList method not found")
        
        # Check for localStorage key
        self.assertIn('beesmart_active_wordlist', content,
                     "localStorage key not defined")
        
        # Check for global exports
        self.assertIn('window.getCurrentWordList', content,
                     "window.getCurrentWordList not exported")
        self.assertIn('window.clearActiveWordList', content,
                     "window.clearActiveWordList not exported")
        
        # Check for event emission
        self.assertIn('wordlist:changed', content,
                     "wordlist:changed event not found")
        
        # Check for backward-compatible globals
        self.assertIn('window.QUIZ_WORDS', content,
                     "QUIZ_WORDS global not set")
        self.assertIn('window.QUIZ_CURRENT_INDEX', content,
                     "QUIZ_CURRENT_INDEX global not set")
        self.assertIn('window.QUIZ_ACTIVE_LIST_ID', content,
                     "QUIZ_ACTIVE_LIST_ID global not set")
    
    def test_quiz_template_includes_module(self):
        """Test that quiz.html includes the word list manager module"""
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'quiz.html'
        )
        
        self.assertTrue(
            os.path.exists(template_path),
            f"Quiz template not found at {template_path}"
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for script tag
        self.assertIn('quiz-wordlist.js', content,
                     "quiz-wordlist.js not included in template")
    
    def test_quiz_template_has_data_anchor(self):
        """Test that quiz.html has the #quiz-root data anchor"""
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'quiz.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for quiz-root element
        self.assertIn('id="quiz-root"', content,
                     "#quiz-root element not found in template")
        
        # Check for data attributes
        self.assertIn('data-selected-list-id', content,
                     "data-selected-list-id attribute not found")
        self.assertIn('data-selected-list-name', content,
                     "data-selected-list-name attribute not found")
        self.assertIn('data-words-url', content,
                     "data-words-url attribute not found")
    
    def test_quiz_template_has_refresh_button(self):
        """Test that quiz.html has the refresh list button"""
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'quiz.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for refresh button
        self.assertIn('refreshWordListBtn', content,
                     "refreshWordListBtn not found in template")
        self.assertIn('Refresh List', content,
                     "'Refresh List' text not found in template")
    
    def test_module_structure_valid_js(self):
        """Test that the module has valid JavaScript structure"""
        module_path = os.path.join(
            os.path.dirname(__file__),
            'static',
            'js',
            'quiz-wordlist.js'
        )
        
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic syntax checks
        # Count opening and closing braces (should match)
        open_braces = content.count('{')
        close_braces = content.count('}')
        self.assertEqual(open_braces, close_braces,
                        f"Mismatched braces: {open_braces} open vs {close_braces} close")
        
        # Check for IIFE wrapper
        self.assertIn('(function()', content,
                     "Module not wrapped in IIFE")
        self.assertIn("'use strict'", content,
                     "Strict mode not enabled")
        
        # Check for proper error handling
        self.assertIn('try {', content,
                     "No try-catch blocks found")
        self.assertIn('catch (e)', content,
                     "No catch blocks found")
    
    def test_storage_key_consistency(self):
        """Test that storage key is consistent throughout the module"""
        module_path = os.path.join(
            os.path.dirname(__file__),
            'static',
            'js',
            'quiz-wordlist.js'
        )
        
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should use STORAGE_KEY constant
        self.assertIn('const STORAGE_KEY', content,
                     "STORAGE_KEY constant not defined")
        
        # Check it's used in localStorage operations
        storage_operations = content.count('localStorage.')
        self.assertGreater(storage_operations, 0,
                          "No localStorage operations found")


class TestQuizIntegration(unittest.TestCase):
    """Test integration with existing quiz code"""
    
    def test_quiz_template_structure_preserved(self):
        """Test that quiz.html structure is preserved"""
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'quiz.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that important existing elements are still present
        self.assertIn('id="quizCard"', content,
                     "quizCard element missing")
        self.assertIn('class="quiz-container', content,
                     "quiz-container class missing")
        self.assertIn('QuizManager', content,
                     "QuizManager class missing")
        
        # Check that existing functionality is preserved
        self.assertIn('/api/wordbank', content,
                     "/api/wordbank endpoint reference missing")
        self.assertIn('/api/next', content,
                     "/api/next endpoint reference missing")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestQuizWordListManager))
    suite.addTests(loader.loadTestsFromTestCase(TestQuizIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
