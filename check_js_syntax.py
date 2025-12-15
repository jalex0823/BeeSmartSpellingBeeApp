import re

def check_js_balance(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract script blocks
    script_blocks = []
    # Simple regex for <script>...</script> (doesn't handle nested scripts or attributes well, but good enough for most)
    # We use a loop to find them to keep track of line numbers
    pos = 0
    while True:
        start = content.find('<script', pos)
        if start == -1:
            break
        
        # Find end of opening tag
        tag_end = content.find('>', start)
        if tag_end == -1:
            break
            
        # Find closing tag
        end = content.find('</script>', tag_end)
        if end == -1:
            print(f"Error: Unclosed <script> tag starting at line {content[:start].count('\n') + 1}")
            return
            
        script_content = content[tag_end+1:end]
        start_line = content[:tag_end+1].count('\n') + 1
        script_blocks.append((script_content, start_line))
        pos = end + 9

    print(f"Found {len(script_blocks)} script blocks.")

    for i, (script, start_line) in enumerate(script_blocks):
        # Remove comments
        # Remove // comments
        script = re.sub(r'//.*', '', script)
        # Remove /* */ comments (non-greedy)
        script = re.sub(r'/\*.*?\*/', '', script, flags=re.DOTALL)
        
        # Remove strings
        # This is tricky because of escaped quotes.
        # We'll just remove anything between quotes that isn't escaped.
        # Simple approximation: remove "..." and '...' and `...`
        script = re.sub(r'"(?:[^"\\]|\\.)*"', '""', script)
        script = re.sub(r"'(?:[^'\\]|\\.)*'", "''", script)
        script = re.sub(r'`(?:[^`\\]|\\.)*`', '``', script)

        stack = []
        for char_idx, char in enumerate(script):
            if char in '{[(':
                stack.append((char, start_line + script[:char_idx].count('\n')))
            elif char in '}])':
                if not stack:
                    print(f"Error: Unexpected '{char}' at line {start_line + script[:char_idx].count('\n')} in script block {i+1}")
                    # return # Don't return, keep checking
                else:
                    last, last_line = stack.pop()
                    expected = {'{': '}', '[': ']', '(': ')'}[last]
                    if char != expected:
                        print(f"Error: Mismatched '{char}' at line {start_line + script[:char_idx].count('\n')}. Expected '{expected}' (opened at line {last_line})")
                        # return

        if stack:
            print(f"Error: Unclosed '{stack[-1][0]}' in script block {i+1} starting at line {start_line}")
            print(f"  Opened at line {stack[-1][1]}")
            # return

    print("JS check complete.")

check_js_balance(r'c:\Temp\BeeSmartSpellingBeeApp\templates\unified_menu.html')
