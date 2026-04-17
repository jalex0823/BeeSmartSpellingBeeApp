import re

with open("AjaSpellBApp.py", encoding="utf-8") as f:
    content = f.read()

# Find all route definitions with their function names
pattern = re.compile(r"@app\.route\('([^']+)'[^)]*\)\s*(?:@[^\n]+\n)*def (\w+)")
matches = pattern.findall(content)
for path, func in matches:
    print(f"{path:<55} -> {func}")
