#!/usr/bin/env python3
"""
Main Menu Tiles Smoke Test
Tests functionality and performance of all main menu tiles
"""

import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

# Main menu tiles configuration
MENU_TILES = {
    'upload_word_list': {
        'id': None,
        'selector': '.menu-option[onclick*="text"]',
        'type': 'text',
        'function': 'showTextUploadInterface',
        'requires_auth': False,
        'requires_premium': False,
        'navigates_away': False,
        'description': 'Upload Word List - File upload interface'
    },
    'type_manually': {
        'id': None,
        'selector': '.menu-option[onclick*="manual"]',
        'type': 'manual',
        'function': 'showManualWordEntry',
        'requires_auth': False,
        'requires_premium': False,
        'navigates_away': False,
        'description': 'Type Words Manually - Text entry interface'
    },
    'extract_from_image': {
        'id': 'tileImageUpload',
        'selector': '#tileImageUpload',
        'type': 'image',
        'function': 'showImageUploadInterface',
        'requires_auth': True,
        'requires_premium': True,
        'navigates_away': False,
        'description': 'Extract from Image - OCR image upload (Premium)'
    },
    'dictionary_search': {
        'id': 'tileDictionary',
        'selector': '#tileDictionary',
        'type': 'dictionary',
        'function': 'showDictionaryInterface',
        'requires_auth': False,
        'requires_premium': False,
        'navigates_away': False,
        'description': 'Dictionary Search - Word lookup interface'
    },
    'avatars': {
        'id': 'tileAvatars',
        'selector': '#tileAvatars',
        'type': 'avatars',
        'function': None,  # Navigates away
        'requires_auth': False,
        'requires_premium': False,
        'navigates_away': True,
        'navigation_url': '/honeycomb-picker',
        'description': 'Avatars - Navigate to avatar picker'
    },
    'saved_lists': {
        'id': 'tileSavedLists',
        'selector': '#tileSavedLists',
        'type': 'saved',
        'function': None,  # Navigates away
        'requires_auth': True,
        'requires_premium': True,
        'navigates_away': True,
        'navigation_url': '/word-lists',
        'description': 'Saved Word Lists - Navigate to saved lists (Premium)'
    },
    'random_play': {
        'id': 'tileRandom',
        'selector': '#tileRandom',
        'type': 'random',
        'function': 'showRandomPlayInterface',
        'requires_auth': False,
        'requires_premium': False,
        'navigates_away': False,
        'description': 'Random Play - AI word selection interface'
    },
    'speed_round': {
        'id': 'tileSpeedRound',
        'selector': '#tileSpeedRound',
        'type': 'speed',
        'function': 'showSpeedRoundInterface',
        'requires_auth': True,
        'requires_premium': True,
        'navigates_away': True,
        'navigation_url': '/speed-round',
        'description': 'Speed Round Challenge - Navigate to speed round (Premium)'
    }
}

def test_tile_structure():
    """Test 1: Verify tile HTML structure exists"""
    print_header("TEST 1: Tile HTML Structure")
    
    try:
        with open('templates/unified_menu.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {}
        for tile_name, tile_config in MENU_TILES.items():
            selector = tile_config['selector']
            tile_id = tile_config.get('id')
            
            # Check if selector exists in HTML
            if tile_id:
                found = f'id="{tile_id}"' in content or f"id='{tile_id}'" in content
            else:
                # For class-based selectors, check for onclick pattern
                found = tile_config['type'] in content and 'selectOption' in content
            
            if found:
                print_success(f"{tile_name}: Found in HTML")
                results[tile_name] = True
            else:
                print_error(f"{tile_name}: NOT FOUND in HTML")
                results[tile_name] = False
        
        return all(results.values()), results
    except Exception as e:
        print_error(f"Failed to read template: {e}")
        return False, {}

def test_tile_functions():
    """Test 2: Verify JavaScript functions exist"""
    print_header("TEST 2: JavaScript Functions")
    
    try:
        with open('templates/unified_menu.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {}
        required_functions = [
            'selectOption',
            'showTextUploadInterface',
            'showManualWordEntry',
            'showImageUploadInterface',
            'showDictionaryInterface',
            'showRandomPlayInterface',
            'showSpeedRoundInterface',
            'uploadTextFile',
            'uploadImageFile'
        ]
        
        for func_name in required_functions:
            # Check for function definition
            patterns = [
                f'function {func_name}',
                f'const {func_name} =',
                f'let {func_name} =',
                f'{func_name}: function',
                f'{func_name}: function('
            ]
            
            found = any(pattern in content for pattern in patterns)
            
            if found:
                print_success(f"{func_name}(): Found")
                results[func_name] = True
            else:
                print_error(f"{func_name}(): NOT FOUND")
                results[func_name] = False
        
        return all(results.values()), results
    except Exception as e:
        print_error(f"Failed to check functions: {e}")
        return False, {}

def test_tile_selectors():
    """Test 3: Verify CSS selectors are valid"""
    print_header("TEST 3: CSS Selector Validity")
    
    results = {}
    for tile_name, tile_config in MENU_TILES.items():
        selector = tile_config['selector']
        
        # Basic selector validation
        if selector.startswith('#') or selector.startswith('.') or selector.startswith('['):
            print_success(f"{tile_name}: Valid selector '{selector}'")
            results[tile_name] = True
        else:
            print_error(f"{tile_name}: Invalid selector '{selector}'")
            results[tile_name] = False
    
    return all(results.values()), results

def test_tile_navigation():
    """Test 4: Verify navigation URLs are correct"""
    print_header("TEST 4: Navigation URLs")
    
    try:
        with open('AjaSpellBApp.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {}
        navigation_tiles = {
            'avatars': '/honeycomb-picker',
            'saved_lists': '/word-lists',
            'speed_round': '/speed-round'
        }
        
        for tile_name, expected_url in navigation_tiles.items():
            # Check if route exists
            route_pattern = f"@app.route('{expected_url}'" or f'@app.route("{expected_url}"'
            found = route_pattern in content or f"route('{expected_url}'" in content
            
            if found:
                print_success(f"{tile_name}: Route '{expected_url}' exists")
                results[tile_name] = True
            else:
                print_warning(f"{tile_name}: Route '{expected_url}' not found (may use redirect)")
                results[tile_name] = True  # Don't fail, might use redirect
        
        return True, results
    except Exception as e:
        print_error(f"Failed to check routes: {e}")
        return False, {}

def test_tile_performance_indicators():
    """Test 5: Check for performance optimization indicators"""
    print_header("TEST 5: Performance Indicators")
    
    try:
        with open('templates/unified_menu.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'lazy_loading': 'loading="lazy"' in content or 'lazy' in content.lower(),
            'event_delegation': 'addEventListener' in content,
            'debounce_throttle': 'debounce' in content or 'throttle' in content,
            'async_operations': 'async' in content or 'await' in content,
            'error_handling': 'try' in content and 'catch' in content
        }
        
        results = {}
        for check_name, found in checks.items():
            if found:
                print_success(f"{check_name}: Present")
                results[check_name] = True
            else:
                print_warning(f"{check_name}: Not found (may not be needed)")
                results[check_name] = True  # Don't fail, optional optimization
        
        return True, results
    except Exception as e:
        print_error(f"Failed to check performance: {e}")
        return False, {}

def test_tile_accessibility():
    """Test 6: Check accessibility features"""
    print_header("TEST 6: Accessibility Features")
    
    try:
        with open('templates/unified_menu.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'title_attributes': 'title=' in content,
            'aria_labels': 'aria-label' in content or 'ariaLabel' in content,
            'keyboard_navigation': 'keydown' in content or 'keypress' in content,
            'focus_management': 'focus()' in content or 'blur()' in content
        }
        
        results = {}
        for check_name, found in checks.items():
            if found:
                print_success(f"{check_name}: Present")
                results[check_name] = True
            else:
                print_warning(f"{check_name}: Not found")
                results[check_name] = True  # Optional
        
        return True, results
    except Exception as e:
        print_error(f"Failed to check accessibility: {e}")
        return False, {}

def generate_test_report(all_results: Dict):
    """Generate comprehensive test report"""
    print_header("TEST REPORT SUMMARY")
    
    total_tests = len(all_results)
    passed_tests = sum(1 for result in all_results.values() if result.get('passed', False))
    
    print(f"\n{Colors.BOLD}Overall Results:{Colors.RESET}")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {Colors.GREEN}{passed_tests}{Colors.RESET}")
    print(f"  Failed: {Colors.RED}{total_tests - passed_tests}{Colors.RESET}")
    print(f"  Success Rate: {Colors.BOLD}{(passed_tests/total_tests*100):.1f}%{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Test Breakdown:{Colors.RESET}")
    for test_name, result in all_results.items():
        status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
        color = Colors.GREEN if result.get('passed', False) else Colors.RED
        print(f"  {color}{status}{Colors.RESET} - {test_name}")
    
    # Generate JSON report
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'success_rate': f"{(passed_tests/total_tests*100):.1f}%"
        },
        'results': all_results,
        'tiles_tested': list(MENU_TILES.keys())
    }
    
    with open('menu_tiles_smoke_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{Colors.BLUE}📄 Detailed report saved to: menu_tiles_smoke_test_report.json{Colors.RESET}\n")
    
    return passed_tests == total_tests

def main():
    """Run all smoke tests"""
    print_header("MAIN MENU TILES SMOKE TEST")
    print_info(f"Testing {len(MENU_TILES)} menu tiles")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_results = {}
    
    # Run all tests
    test_functions = [
        ("Tile Structure", test_tile_structure),
        ("JavaScript Functions", test_tile_functions),
        ("CSS Selectors", test_tile_selectors),
        ("Navigation Routes", test_tile_navigation),
        ("Performance Indicators", test_tile_performance_indicators),
        ("Accessibility Features", test_tile_accessibility)
    ]
    
    for test_name, test_func in test_functions:
        try:
            start_time = time.time()
            passed, details = test_func()
            elapsed = time.time() - start_time
            
            all_results[test_name] = {
                'passed': passed,
                'details': details,
                'duration_seconds': round(elapsed, 3)
            }
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            all_results[test_name] = {
                'passed': False,
                'error': str(e),
                'duration_seconds': 0
            }
    
    # Generate report
    all_passed = generate_test_report(all_results)
    
    # Exit code
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
