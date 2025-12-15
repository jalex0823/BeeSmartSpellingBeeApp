import re

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        # Simple check: look for 's without preceding backslash
        # But we need to ignore double-quoted strings
        # This is a heuristic
        
        # Remove double quoted strings "..."
        temp_line = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '', line)
        
        # Now look for '... 's ...' pattern
        # If we have 'It's', it looks like 'It' followed by s
        # Regex: ' followed by s
        # But we need to make sure the ' is a closing quote
        # A closing quote is preceded by non-backslash
        
        # Find all single quoted strings
        # matches = re.finditer(r"'([^'\\]*(?:\\.[^'\\]*)*)'", temp_line)
        # for m in matches:
        #     end = m.end()
        #     if end < len(temp_line) and temp_line[end] == 's':
        #         print(f"Line {i+1}: {line.strip()}")
        
        # Simpler: Look for 's where ' is not escaped
        # matches = re.finditer(r"(?<!\\)'s", temp_line)
        # for m in matches:
        #     print(f"Line {i+1}: {line.strip()}")
            
        # Even simpler: Look for 's inside a line, but try to filter out valid cases
        if "'s" in temp_line:
            # Check if it's escaped
            if "\\'s" not in temp_line:
                 # It might be valid if it's inside a double quoted string (already removed)
                 # Or if it's '... 's ...' (two strings)
                 # But 'It's' is the most likely error
                 print(f"Line {i+1}: {line.strip()}")

check_file('c:\\Temp\\BeeSmartSpellingBeeApp\\templates\\quiz.html')
