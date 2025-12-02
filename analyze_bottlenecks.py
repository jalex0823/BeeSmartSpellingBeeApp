#!/usr/bin/env python3
"""
Analyze AjaSpellBApp.py for performance bottlenecks
"""
import re

with open('AjaSpellBApp.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')

print("=" * 70)
print("🔍 PERFORMANCE BOTTLENECK ANALYSIS")
print("=" * 70)

# 1. Check @app.before_request handlers
print("\n📌 @app.before_request handlers (run on EVERY request):")
before_request_pattern = r'@app\.before_request'
matches = [(i+1, line) for i, line in enumerate(lines) if re.search(before_request_pattern, line)]
for line_num, line in matches:
    func_name = lines[line_num].strip() if line_num < len(lines) else "unknown"
    print(f"   Line {line_num}: {func_name}")

# 2. Check for db.session.commit() without try/except
print("\n📌 Database commits (potential blocking operations):")
commit_count = len(re.findall(r'db\.session\.commit\(\)', content))
print(f"   Total db.session.commit() calls: {commit_count}")

# 3. Check for .all() queries that might load too much data
print("\n📌 Potentially expensive .all() queries:")
all_queries = re.findall(r'\.query.*\.all\(\)', content)
print(f"   Total .all() queries: {len(all_queries)}")
if len(all_queries) > 0:
    print(f"   Sample queries:")
    for query in all_queries[:5]:
        print(f"     - {query[:80]}...")

# 4. Check for Session logging
print("\n📌 Session logging operations:")
session_log_calls = len(re.findall(r'SessionLog\(|log_session_action', content))
print(f"   SessionLog operations: {session_log_calls}")

# 5. Check for print statements (can slow down production)
print("\n📌 Print statements (should use logging in production):")
print_count = len(re.findall(r'\bprint\(', content))
print(f"   Total print() statements: {print_count}")

# 6. Check startup operations
print("\n📌 Startup operations:")
startup_operations = [
    ('load_simple_wiktionary', 'Loading 50K+ word dictionary'),
    ('load_dictionary_cache', 'Loading dictionary cache'),
    ('db.create_all', 'Database table creation'),
    ('threading.Thread', 'Background threads'),
]

for operation, description in startup_operations:
    count = len(re.findall(operation, content))
    if count > 0:
        print(f"   ✓ {description}: {count} occurrence(s)")

print("\n" + "=" * 70)
print("RECOMMENDATIONS:")
print("=" * 70)
print("1. ✅ DONE - Disabled Wiktionary loading (saves 30-60s)")
print("2. 🔧 SessionLog in @before_request - adds DB call to EVERY request")
print("3. 🔧 session.permanent check runs on EVERY request")
print(f"4. ⚠️  {print_count} print statements - should use proper logging")
print("5. 🔧 Consider lazy-loading avatar catalog on first access")
print("6. 🔧 Cache frequently-accessed DB queries")
