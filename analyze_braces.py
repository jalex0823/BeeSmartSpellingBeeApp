#!/usr/bin/env python3
"""Analyze brace balance in quiz.html, especially around event listeners."""

def analyze_braces(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    stack = []
    issues = []
    in_beforeunload = False
    in_pagehide = False
    
    for line_num, line in enumerate(lines, start=1):
        # Track event listeners
        if 'beforeunload' in line and 'addEventListener' in line:
            in_beforeunload = True
            print(f"\n🔍 Found beforeunload at line {line_num}")
        if 'pagehide' in line and 'addEventListener' in line:
            in_pagehide = True
            print(f"\n🔍 Found pagehide at line {line_num}")
        
        # Count braces
        for char_pos, char in enumerate(line):
            if char == '{':
                stack.append((line_num, char_pos, in_beforeunload, in_pagehide))
            elif char == '}':
                if stack:
                    open_info = stack.pop()
                    if in_beforeunload or in_pagehide:
                        if len(stack) == 0:
                            print(f"✅ Closed at line {line_num} (opened at line {open_info[0]})")
                            in_beforeunload = False
                            in_pagehide = False
                else:
                    issues.append(f"❌ UNMATCHED CLOSING BRACE at line {line_num}, position {char_pos}")
                    print(f"❌ Line {line_num}: {line.strip()}")
    
    if stack:
        print(f"\n❌ UNMATCHED OPENING BRACES:")
        for line_num, pos, before, page in stack[-10:]:  # Show last 10
            print(f"  Line {line_num} (beforeunload={before}, pagehide={page})")
    else:
        print("\n✅ All braces balanced!")
    
    return issues

if __name__ == '__main__':
    issues = analyze_braces('templates/quiz.html')
    if issues:
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
