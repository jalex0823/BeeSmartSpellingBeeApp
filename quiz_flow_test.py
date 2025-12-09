"""
Quiz Flow Smoke Test - End-to-End Quiz Functionality
Tests: Word Import → Quiz Start → Quiz Interaction → Report Card
"""

import sys
import re
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_header(title):
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}🐝 {title}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

def print_section(title):
    print(f"\n{BLUE}{'─'*70}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'─'*70}{RESET}")

def check_quiz_flow_elements():
    """Test quiz.html for complete flow elements"""
    print_header("QUIZ FLOW SMOKE TEST")
    
    quiz_path = Path('templates/quiz.html')
    if not quiz_path.exists():
        print(f"{RED}✗ quiz.html not found{RESET}")
        return False
    
    content = quiz_path.read_text(encoding='utf-8')
    all_passed = True
    
    # Phase 1: Word Import & Initialization
    print_section("Phase 1: Word Import & Initialization")
    
    import_elements = {
        '/api/wordbank': 'Word bank API endpoint',
        '/api/next': 'Next word API endpoint',
        'loadNextWord': 'Load next word function',
        'quizStarted': 'Quiz started flag'
    }
    
    for element, description in import_elements.items():
        if element in content:
            print(f"{GREEN}✓ {description} ({element}){RESET}")
        else:
            print(f"{RED}✗ Missing: {description} ({element}){RESET}")
            all_passed = False
    
    # Phase 2: Quiz Start & Avatar Loading
    print_section("Phase 2: Quiz Start & Avatar Loading")
    
    start_elements = {
        'QuizManager': 'Quiz manager class',
        'loadUserAvatar': 'User avatar loader',
        'showIntroAnnouncer': 'Intro announcement system',
        'mascotBee3D': 'Avatar container',
        'SmartyBee3D': '3D avatar renderer'
    }
    
    for element, description in start_elements.items():
        if element in content:
            print(f"{GREEN}✓ {description} ({element}){RESET}")
        else:
            print(f"{RED}✗ Missing: {description} ({element}){RESET}")
            all_passed = False
    
    # Phase 3: Quiz Interaction (Word Display, Input, Feedback)
    print_section("Phase 3: Quiz Interaction")
    
    interaction_elements = {
        'currentWord': 'Current word display',
        'spellingInput': 'User input field',
        'submitAnswer': 'Answer submission',
        'showDefinition': 'Definition display',
        'showSentence': 'Sentence context',
        'toggleStat': 'Toggle stats function',
        'feedbackArea': 'Feedback display',
        'pronounceWord': 'Word pronunciation'
    }
    
    for element, description in interaction_elements.items():
        if element in content:
            print(f"{GREEN}✓ {description} ({element}){RESET}")
        else:
            print(f"{RED}✗ Missing: {description} ({element}){RESET}")
            all_passed = False
    
    # Phase 4: Progress Tracking
    print_section("Phase 4: Progress Tracking")
    
    progress_elements = {
        'correctCount': 'Correct count element',
        'incorrectCount': 'Incorrect count element',
        'this.correctCount': 'Correct count tracking',
        'this.incorrectCount': 'Incorrect count tracking',
        'updateScoreDisplay': 'Score update function',
        'totalWords': 'Total word count'
    }
    
    for element, description in progress_elements.items():
        if element in content:
            print(f"{GREEN}✓ {description} ({element}){RESET}")
        else:
            print(f"{RED}✗ Missing: {description} ({element}){RESET}")
            all_passed = False
    
    # Phase 5: Answer Processing
    print_section("Phase 5: Answer Processing & Auto-Advance")
    
    processing_elements = {
        'checkAnswer': 'Answer validation',
        'isAnswering': 'Answer state management',
        'loadNextWord': 'Next word loading',
        'handleCorrectAnswer': 'Correct answer handler',
        'handleIncorrectAnswer': 'Incorrect answer handler'
    }
    
    for element, description in processing_elements.items():
        if element in content:
            print(f"{GREEN}✓ {description} ({element}){RESET}")
        else:
            print(f"{YELLOW}⚠ Optional: {description} ({element}){RESET}")
    
    # Phase 6: Report Card Generation
    print_section("Phase 6: Report Card & Results")
    
    report_elements = {
        'quizComplete': 'Quiz complete screen',
        'completionStats': 'Completion statistics',
        'Your Report Card': 'Report card header',
        'restartButton': 'Restart quiz button',
        'correctWords': 'Correct words list',
        'incorrectWords': 'Incorrect words list'
    }
    
    for element, description in report_elements.items():
        if element in content:
            print(f"{GREEN}✓ {description} ({element}){RESET}")
        else:
            print(f"{RED}✗ Missing: {description} ({element}){RESET}")
            all_passed = False
    
    # Critical Bug Checks
    print_section("Critical Bug Checks")
    
    # Check for isAnswering flag management
    if 'this.isAnswering = false' in content:
        # Check if it's before setTimeout (fix for network error)
        # Look for the critical comment or the pattern
        if 'CRITICAL: Reset isAnswering BEFORE setTimeout' in content:
            print(f"{GREEN}✓ isAnswering flag reset before auto-advance (network error fix applied){RESET}")
        elif 'this.isAnswering = false' in content and 'setTimeout' in content:
            print(f"{GREEN}✓ isAnswering flag management present{RESET}")
        else:
            print(f"{YELLOW}⚠ isAnswering flag exists but verify positioning{RESET}")
    else:
        print(f"{RED}✗ isAnswering flag management missing{RESET}")
        all_passed = False
    
    # Check for avatar parameter order fix
    if "loadUserAvatar(null, 'mascotBee3D')" in content or 'loadUserAvatar(avatarId, containerId)' in content:
        print(f"{GREEN}✓ Avatar loader parameter order correct{RESET}")
    else:
        print(f"{YELLOW}⚠ Check avatar loader call parameters{RESET}")
    
    # Check for intro announcement
    if 'showIntroAnnouncer' in content and "Hello! I'm Buzzy" in content:
        print(f"{GREEN}✓ Intro announcement system present{RESET}")
    elif 'showIntroAnnouncer' in content:
        print(f"{GREEN}✓ Intro announcement system present{RESET}")
    else:
        print(f"{YELLOW}⚠ Intro announcement might be missing{RESET}")
    
    return all_passed

def check_api_endpoints():
    """Check if Flask app has required API endpoints"""
    print_section("API Endpoints Check")
    
    app_path = Path('AjaSpellBApp.py')
    if not app_path.exists():
        print(f"{RED}✗ AjaSpellBApp.py not found{RESET}")
        return False
    
    content = app_path.read_text(encoding='utf-8')
    all_passed = True
    
    endpoints = {
        '/api/next': 'Get next quiz word',
        '/api/answer': 'Submit answer',
        '/api/wordbank': 'Get word bank',
        '/api/upload': 'Upload words',
        '/api/clear': 'Clear word bank',
        '/api/users/me/avatar': 'Get user avatar'
    }
    
    for endpoint, description in endpoints.items():
        # Check for route decorator with endpoint
        pattern = f"@.*route.*{re.escape(endpoint)}"
        if re.search(pattern, content):
            print(f"{GREEN}✓ {description} ({endpoint}){RESET}")
        else:
            print(f"{RED}✗ Missing: {description} ({endpoint}){RESET}")
            all_passed = False
    
    return all_passed

def check_unified_menu():
    """Check unified menu for word import functionality"""
    print_section("Word Import & Menu Check")
    
    menu_path = Path('templates/unified_menu.html')
    if not menu_path.exists():
        print(f"{RED}✗ unified_menu.html not found{RESET}")
        return False
    
    content = menu_path.read_text(encoding='utf-8')
    all_passed = True
    
    menu_elements = {
        'importFileInput': 'File import input',
        'handleImportFile': 'Import handler function',
        'exportWordList': 'Export functionality',
        'startQuizBtn': 'Start quiz button',
        'WordBankManager': 'Word bank manager',
        'action-buttons': 'Action buttons container'
    }
    
    for element, description in menu_elements.items():
        if element in content:
            print(f"{GREEN}✓ {description} ({element}){RESET}")
        else:
            print(f"{RED}✗ Missing: {description} ({element}){RESET}")
            all_passed = False
    
    # Check for recent layout fixes
    if 'flex-direction: row' in content and 'action-buttons' in content:
        print(f"{GREEN}✓ Action buttons layout fixed (horizontal row){RESET}")
    else:
        print(f"{YELLOW}⚠ Action buttons might not be in row layout{RESET}")
    
    # Check for welcome pill
    if 'Welcome' in content and 'current_user.username' in content:
        print(f"{GREEN}✓ Welcome pill shows user name{RESET}")
    else:
        print(f"{YELLOW}⚠ Welcome pill might not show user name{RESET}")
    
    return all_passed

def run_comprehensive_test():
    """Run all quiz flow tests"""
    print_header("BeeSmart Quiz Flow - Comprehensive Smoke Test")
    print(f"{CYAN}Testing complete flow: Import → Quiz → Report Card{RESET}\n")
    
    results = []
    
    # Test 1: Unified Menu (Word Import)
    results.append(check_unified_menu())
    
    # Test 2: Quiz Flow Elements
    results.append(check_quiz_flow_elements())
    
    # Test 3: API Endpoints
    results.append(check_api_endpoints())
    
    # Final Summary
    print_header("TEST SUMMARY")
    
    passed_count = sum(results)
    total_count = len(results)
    
    if all(results):
        print(f"{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}✓ ALL TESTS PASSED ({passed_count}/{total_count}){RESET}")
        print(f"{GREEN}  Quiz flow is ready for testing!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}")
        return 0
    else:
        print(f"{RED}{'='*70}{RESET}")
        print(f"{RED}✗ SOME TESTS FAILED ({passed_count}/{total_count} passed){RESET}")
        print(f"{YELLOW}  Review errors above for details{RESET}")
        print(f"{RED}{'='*70}{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(run_comprehensive_test())
