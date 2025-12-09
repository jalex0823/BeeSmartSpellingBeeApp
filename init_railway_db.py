#!/usr/bin/env python3
"""
Initialize Railway PostgreSQL database with wordbank_storage table
Run this script to create the table and verify connection
"""
import os
import sys

# Get DATABASE_URL from environment
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("=" * 70)
    print("❌ ERROR: DATABASE_URL environment variable not set")
    print("=" * 70)
    print("\nTo set up Railway database:")
    print("1. Get your PostgreSQL URL from Railway Dashboard")
    print("2. Set environment variable:")
    print("   $env:DATABASE_URL = \"postgresql://user:pass@host:5432/dbname\"")
    print("3. Run this script again")
    sys.exit(1)

print("=" * 70)
print("🚀 RAILWAY DATABASE INITIALIZATION")
print("=" * 70)

print(f"\n📍 Database URL: {database_url[:50]}...")

# Test connection first
print("\n1. Testing connection to Railway PostgreSQL...")
try:
    import psycopg2
    # Parse connection string
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Simple test query
    cursor.execute("SELECT 1")
    cursor.fetchone()
    print("   ✅ Connection successful!")
    
    cursor.close()
    conn.close()
except ImportError:
    print("   ⚠️  psycopg2 not installed, trying with SQLAlchemy...")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)

# Now use Flask/SQLAlchemy to create tables
print("\n2. Initializing Flask app with Railway database...")

# Change to app directory
os.chdir(r'c:\Temp\BeeSmartSpellingBeeApp')
sys.path.insert(0, r'c:\Temp\BeeSmartSpellingBeeApp')

# Set the environment variable before importing
os.environ['DATABASE_URL'] = database_url

try:
    from AjaSpellBApp import app, db
    from models import WordBankStorage
    
    print(f"   ✅ Flask app loaded")
    print(f"   Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
    
    with app.app_context():
        print("\n3. Creating database tables...")
        
        # Create all tables
        db.create_all()
        print("   ✅ db.create_all() executed")
        
        # Verify WordBankStorage table
        print("\n4. Verifying wordbank_storage table...")
        
        try:
            # Test query
            count = WordBankStorage.query.count()
            print(f"   ✅ wordbank_storage table exists with {count} wordbanks")
            
            # Show schema
            from sqlalchemy import inspect
            inspector = inspect(WordBankStorage)
            print(f"\n   Table schema:")
            for col in inspector.columns:
                print(f"     - {col.name} ({col.type})")
            
            print("\n" + "=" * 70)
            print("✅ RAILWAY DATABASE INITIALIZATION COMPLETE")
            print("=" * 70)
            print("\nNext steps:")
            print("1. Restart Flask app")
            print("2. Test word upload")
            print("3. Verify words appear in Railway database")
            print("4. Deploy to Railway production")
            
        except Exception as e:
            print(f"   ⚠️  Could not verify table: {e}")
            print("   Table may have been created, try uploading words to verify")
            
except Exception as e:
    print(f"   ❌ Error loading Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
