import re
import sys

def check_js_balance(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove comments
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove strings
    content = re.sub(r'"(?:[^"\\]|\\.)*"', '""', content)
    content = re.sub(r"'(?:[^'\\]|\\.)*'", "''", content)
    content = re.sub(r'`(?:[^`\\]|\\.)*`', '``', content)

    stack = []
    for i, char in enumerate(content):
        line_num = content[:i].count('\n') + 1
        if char in '{[(':
            stack.append((char, line_num))
        elif char in '}])':
            if not stack:
                print(f"Error: Unexpected '{char}' at line {line_num}")
            else:
                last, last_line = stack.pop()
                expected = {'{': '}', '[': ']', '(': ')'}[last]
                if char != expected:
                    print(f"Error: Mismatched '{char}' at line {line_num}. Expected '{expected}' (opened at line {last_line})")

    if stack:
        print(f"Error: Unclosed '{stack[-1][0]}' at end of file. Opened at line {stack[-1][1]}")
    else:
        print("Balanced.")

if __name__ == "__main__":
    check_js_balance(sys.argv[1])
