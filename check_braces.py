#!/usr/bin/env python3
"""Check for mismatched braces/parentheses in unified_menu.html"""

def check_script_blocks(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_script = False
    script_start = 0
    brace_stack = []
    paren_stack = []
    bracket_stack = []
    
    for i, line in enumerate(lines, 1):
        if '<script' in line:
            in_script = True
            script_start = i
            brace_stack = []
            paren_stack = []
            bracket_stack = []
            print(f"\n[OK] Script block starts at line {i}")
        
        if in_script:
            for j, char in enumerate(line):
                if char == '{':
                    brace_stack.append((i, j))
                elif char == '}':
                    if brace_stack:
                        brace_stack.pop()
                    else:
                        print(f"❌ Extra closing brace }} at line {i}, col {j}")
                
                if char == '(':
                    paren_stack.append((i, j))
                elif char == ')':
                    if paren_stack:
                        paren_stack.pop()
                    else:
                        print(f"❌ Extra closing paren ) at line {i}, col {j}")
                
                if char == '[':
                    bracket_stack.append((i, j))
                elif char == ']':
                    if bracket_stack:
                        bracket_stack.pop()
                    else:
                        print(f"❌ Extra closing bracket ] at line {i}, col {j}")
        
        if '</script>' in line and in_script:
            in_script = False
            if brace_stack:
                print(f"❌ Unclosed braces in script block (started line {script_start}):")
                for line_num, col in brace_stack:
                    print(f"   {{ at line {line_num}, col {col}")
            if paren_stack:
                print(f"❌ Unclosed parens in script block (started line {script_start}):")
                for line_num, col in paren_stack:
                    print(f"   ( at line {line_num}, col {col}")
            if bracket_stack:
                print(f"❌ Unclosed brackets in script block (started line {script_start}):")
                for line_num, col in bracket_stack:
                    print(f"   [ at line {line_num}, col {col}")
            
            if not brace_stack and not paren_stack and not bracket_stack:
                print(f"[OK] Script block closed at line {i} - all balanced")

if __name__ == '__main__':
    check_script_blocks('templates/unified_menu.html')
