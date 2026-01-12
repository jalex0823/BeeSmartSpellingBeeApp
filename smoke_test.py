"""
Smoke Test - Quiz and Menu Template Validation
Checks for syntax errors, context integrity, and critical elements
"""

import sys
import re
from pathlib import Path
import io

# Ensure Windows console can handle Unicode (emojis, symbols) without crashing.
if sys.platform == "win32":
    try:
        if getattr(sys.stdout, "buffer", None) is not None and not getattr(sys.stdout, "closed", False):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if getattr(sys.stderr, "buffer", None) is not None and not getattr(sys.stderr, "closed", False):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        # Best-effort only; never fail the smoke test due to console encoding tweaks.
        pass

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def check_template_syntax(template_path):
    """Validate Jinja2 template syntax"""
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(template_path.name)
        return True, "Template syntax valid"
    except Exception as e:
        return False, str(e)

def check_critical_elements(file_path, required_elements):
    """Check for presence of critical elements"""
    content = file_path.read_text(encoding='utf-8')
    missing = []
    found = []
    
    for element in required_elements:
        if element in content:
            found.append(element)
        else:
            missing.append(element)
    
    return found, missing

def check_javascript_patterns(file_path):
    """Check for common JavaScript issues"""
    content = file_path.read_text(encoding='utf-8')
    issues = []
    
    # Check for unmatched braces (basic check)
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        issues.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
    
    # Check for console.error statements (potential error handlers)
    error_count = len(re.findall(r'console\.error\(', content))
    
    # Check for unclosed template literals
    backticks = content.count('`')
    if backticks % 2 != 0:
        issues.append(f"Unmatched backticks (template literals): {backticks}")
    
    return issues, error_count

def run_smoke_tests():
    """Run all smoke tests"""
    print_section("🐝 BeeSmart Spelling App - Smoke Test Suite")
    
    all_passed = True
    
    # Test 1: quiz.html
    print_section("📋 Testing quiz.html")
    quiz_path = Path('templates/quiz.html')
    
    if not quiz_path.exists():
        print(f"{RED}✗ quiz.html not found{RESET}")
        all_passed = False
    else:
        # Syntax check
        passed, msg = check_template_syntax(quiz_path)
        if passed:
            print(f"{GREEN}✓ Jinja2 syntax validation passed{RESET}")
        else:
            print(f"{RED}✗ Syntax error: {msg}{RESET}")
            all_passed = False
        
        # Critical elements check
        critical_quiz = [
            'QuizManager',
            'showDefinition',
            'showSentence',
            'toggleStat',
            'currentWord',
            'feedbackArea',
            'spellingInput'
        ]
        found, missing = check_critical_elements(quiz_path, critical_quiz)
        
        print(f"\n{BLUE}Critical Elements:{RESET}")
        for elem in found:
            print(f"{GREEN}  ✓ {elem}{RESET}")
        for elem in missing:
            print(f"{RED}  ✗ {elem} (missing){RESET}")
            all_passed = False
        
        # JavaScript checks
        issues, error_handlers = check_javascript_patterns(quiz_path)
        if issues:
            print(f"\n{YELLOW}JavaScript Warnings:{RESET}")
            for issue in issues:
                print(f"{YELLOW}  ⚠ {issue}{RESET}")
        print(f"{BLUE}  Info: {error_handlers} error handlers found{RESET}")
    
    # Test 2: unified_menu.html
    print_section("📋 Testing unified_menu.html")
    menu_path = Path('templates/unified_menu.html')
    
    if not menu_path.exists():
        print(f"{RED}✗ unified_menu.html not found{RESET}")
        all_passed = False
    else:
        # Syntax check
        passed, msg = check_template_syntax(menu_path)
        if passed:
            print(f"{GREEN}✓ Jinja2 syntax validation passed{RESET}")
        else:
            print(f"{RED}✗ Syntax error: {msg}{RESET}")
            all_passed = False
        
        # Critical elements check
        critical_menu = [
            'WordBankManager',
            'action-buttons',
            'startQuizBtn',
            'selectOption',
            'exportWordList',
            'importWordList'
        ]
        found, missing = check_critical_elements(menu_path, critical_menu)
        
        print(f"\n{BLUE}Critical Elements:{RESET}")
        for elem in found:
            print(f"{GREEN}  ✓ {elem}{RESET}")
        for elem in missing:
            print(f"{RED}  ✗ {elem} (missing){RESET}")
            all_passed = False
        
        # Check for recent changes (action-buttons flex layout)
        content = menu_path.read_text(encoding='utf-8')
        if 'flex-direction: row' in content and 'action-buttons' in content:
            print(f"{GREEN}  ✓ Action buttons flex layout updated{RESET}")
        else:
            print(f"{YELLOW}  ⚠ Action buttons may not be in row layout{RESET}")
        
        # JavaScript checks
        issues, error_handlers = check_javascript_patterns(menu_path)
        if issues:
            print(f"\n{YELLOW}JavaScript Warnings:{RESET}")
            for issue in issues:
                print(f"{YELLOW}  ⚠ {issue}{RESET}")
        print(f"{BLUE}  Info: {error_handlers} error handlers found{RESET}")
    
    # Test 3: Flask app
    print_section("🐍 Testing AjaSpellBApp.py")
    app_path = Path('AjaSpellBApp.py')
    
    if not app_path.exists():
        print(f"{RED}✗ AjaSpellBApp.py not found{RESET}")
        all_passed = False
    else:
        try:
            import py_compile
            py_compile.compile(str(app_path), doraise=True)
            print(f"{GREEN}✓ Python syntax validation passed{RESET}")
        except py_compile.PyCompileError as e:
            print(f"{RED}✗ Python syntax error: {e}{RESET}")
            all_passed = False
    
    # Final summary
    print_section("📊 Smoke Test Summary")
    if all_passed:
        print(f"{GREEN}✓ All smoke tests PASSED{RESET}")
        print(f"{GREEN}  No critical errors detected{RESET}")
        return 0
    else:
        print(f"{RED}✗ Some tests FAILED{RESET}")
        print(f"{YELLOW}  Review errors above{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(run_smoke_tests())
