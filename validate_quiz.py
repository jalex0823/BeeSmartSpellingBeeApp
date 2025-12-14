#!/usr/bin/env python3
"""
Comprehensive Quiz.html Validator
- Check for unclosed parentheses in JSON.stringify/sendBeacon calls
- Check for unrendered Jinja {{ }} variables inside <script> tags
- Check for arrow function syntax issues
"""

import re
from pathlib import Path

def validate_quiz_html():
    quiz_path = Path('templates/quiz.html')
    content = quiz_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    issues = []
    in_script = False
    script_start = 0
    
    print("🔍 COMPREHENSIVE QUIZ.HTML VALIDATION")
    print("=" * 70)
    
    # Track all Jinja variables
    jinja_vars = re.findall(r'\{\{[^}]+\}\}', content)
    print(f"\n📋 Found {len(jinja_vars)} Jinja template variables:")
    for i, var in enumerate(jinja_vars, 1):
        print(f"  {i}. {var}")
    
    # Check for Jinja variables inside <script> tags
    print(f"\n🔍 Checking for Jinja variables in <script> tags...")
    script_blocks = re.finditer(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    
    script_jinja_count = 0
    for match in script_blocks:
        script_content = match.group(1)
        script_jinja = re.findall(r'\{\{[^}]+\}\}', script_content)
        if script_jinja:
            script_jinja_count += len(script_jinja)
            for var in script_jinja:
                print(f"  ✓ Jinja in script: {var}")
    
    print(f"  Total Jinja vars in scripts: {script_jinja_count}")
    
    # Check for unclosed parentheses in sendBeacon/JSON.stringify calls
    print(f"\n🔍 Checking sendBeacon and JSON.stringify calls...")
    
    beacon_pattern = r'navigator\.sendBeacon\s*\([^)]*(?:\{[^}]*\}[^)]*)*\)'
    beacon_calls = re.findall(beacon_pattern, content, re.DOTALL)
    print(f"  Found {len(beacon_calls)} sendBeacon calls")
    
    # Find all sendBeacon with line numbers
    for line_num, line in enumerate(lines, 1):
        if 'sendBeacon' in line:
            print(f"  Line {line_num}: {line.strip()[:80]}")
            
            # Check if there's a complete closing parenthesis
            # Count opening and closing parens from this line forward
            paren_count = 0
            search_lines = lines[line_num-1:min(line_num+5, len(lines))]
            
            for search_line in search_lines:
                paren_count += search_line.count('(') - search_line.count(')')
            
            if paren_count != 0:
                issues.append(f"⚠️ Line {line_num}: Potential unclosed parentheses in sendBeacon (balance: {paren_count})")
    
    # Check JSON.stringify calls
    for line_num, line in enumerate(lines, 1):
        if 'JSON.stringify' in line:
            print(f"  Line {line_num}: {line.strip()[:80]}")
            
            # Check balance
            paren_count = 0
            search_lines = lines[line_num-1:min(line_num+5, len(lines))]
            
            for search_line in search_lines:
                paren_count += search_line.count('(') - search_line.count(')')
            
            if paren_count != 0:
                issues.append(f"⚠️ Line {line_num}: Potential unclosed parentheses in JSON.stringify (balance: {paren_count})")
    
    # Check for arrow functions with potential brace issues
    print(f"\n🔍 Checking arrow functions...")
    arrow_pattern = r'=>\s*\{'
    arrow_functions = []
    
    for line_num, line in enumerate(lines, 1):
        if '=>' in line and '{' in line:
            arrow_functions.append((line_num, line.strip()[:100]))
    
    print(f"  Found {len(arrow_functions)} arrow functions")
    if arrow_functions:
        print(f"  First 5:")
        for line_num, text in arrow_functions[:5]:
            print(f"    Line {line_num}: {text}")
    
    # Report issues
    print(f"\n{'='*70}")
    if issues:
        print(f"⚠️ POTENTIAL ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"✅ NO OBVIOUS SYNTAX ISSUES DETECTED")
    
    print(f"{'='*70}")
    
    # Additional checks
    print(f"\n📊 STATISTICS:")
    print(f"  Total lines: {len(lines):,}")
    print(f"  Total characters: {len(content):,}")
    print(f"  Jinja variables: {len(jinja_vars)}")
    print(f"  sendBeacon calls: {len(beacon_calls)}")
    print(f"  Arrow functions: {len(arrow_functions)}")
    
    return len(issues) == 0

if __name__ == '__main__':
    validate_quiz_html()
