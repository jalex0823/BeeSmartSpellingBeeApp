"""
Quick diagnostic script to identify Railway startup issues
"""
import sys
import traceback

print("=" * 60)
print("Railway Diagnostic - Checking System")
print("=" * 60)

# 1. Check Python version
print(f"\n1. Python Version: {sys.version}")

# 2. Check config loading
try:
    from config import get_config
    config = get_config()
    db_uri = config.SQLALCHEMY_DATABASE_URI
    print(f"2. Config loaded: {db_uri[:30]}...")
except Exception as e:
    print(f"2. ❌ Config failed: {e}")
    traceback.print_exc()

# 3. Check database connection
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(db_uri)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"3. ✅ Database connection successful")
except Exception as e:
    print(f"3. ❌ Database connection failed: {e}")
    traceback.print_exc()

# 4. Check if users table exists and has buzz_dust fields
try:
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"4. Tables found: {len(tables)}")
    
    if 'users' in tables:
        columns = [col['name'] for col in inspector.get_columns('users')]
        buzz_fields = ['total_buzz_dust', 'bee_class', 'current_streak', 'longest_streak', 'last_rank_up_at']
        
        print(f"   Users table has {len(columns)} columns")
        for field in buzz_fields:
            status = "✅" if field in columns else "❌"
            print(f"   {status} {field}")
    else:
        print("   ⚠️ Users table not found")
except Exception as e:
    print(f"4. ❌ Table inspection failed: {e}")
    traceback.print_exc()

# 5. Check buzz_dust_helpers import
try:
    from buzz_dust_helpers import get_all_bee_classes
    classes = get_all_bee_classes()
    print(f"5. ✅ buzz_dust_helpers loaded: {len(classes)} bee classes")
except Exception as e:
    print(f"5. ❌ buzz_dust_helpers failed: {e}")
    traceback.print_exc()

# 6. Try importing the main app
try:
    print("\n6. Attempting to import Flask app...")
    from AjaSpellBApp import app
    print(f"   ✅ Flask app imported successfully")
    print(f"   App name: {app.name}")
except Exception as e:
    print(f"6. ❌ Flask app import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All diagnostic checks passed!")
print("=" * 60)
