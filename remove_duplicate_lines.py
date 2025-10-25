#!/usr/bin/env python3
"""Remove duplicate mascot animation functions from unified_menu.html"""

file_path = r'c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\templates\unified_menu.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 9268-9492 (Python uses 0-based indexing, so 9267-9491)
# Keep line 9267 (the comment) and everything before/after
new_lines = lines[:9267] + [
    '        // Old helper functions removed - using new fly-by animation\n',
    '        console.log(\'✨ Interactive mascot system loaded\');\n',
    '\n'
] + lines[9492:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ Removed duplicate functions (lines 9268-9492)")
print(f"Original line count: {len(lines)}")
print(f"New line count: {len(new_lines)}")
print(f"Lines removed: {len(lines) - len(new_lines)}")
