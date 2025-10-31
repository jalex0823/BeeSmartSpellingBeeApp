#!/usr/bin/env python
"""
Railway Admin Setup - Interactive Script
Connects to Railway PostgreSQL and runs admin setup
"""
import os
import sys

print("🐝 BeeSmart Railway Admin Setup\n")
print("=" * 60)
print("This script will connect to your Railway PostgreSQL database")
print("and set up admin access for your account.")
print("=" * 60)

# Check if DATABASE_URL is already set
db_url = os.environ.get('DATABASE_URL')

if not db_url:
    print("\n📝 Please enter your Railway PostgreSQL DATABASE_URL:")
    print("   (Get it from: Railway Dashboard → PostgreSQL → Variables → DATABASE_URL)")
    print("   Format: postgresql://user:pass@host:port/dbname\n")
    
    db_url = input("DATABASE_URL: ").strip()
    
    if not db_url:
        print("\n❌ No DATABASE_URL provided. Exiting.")
        sys.exit(1)
    
    # Set it for this session
    os.environ['DATABASE_URL'] = db_url

# Verify it's PostgreSQL
if 'postgresql://' not in db_url and 'postgres://' not in db_url:
    print("\n❌ Invalid DATABASE_URL. Must be a PostgreSQL connection string.")
    print(f"   Got: {db_url[:50]}...")
    sys.exit(1)

print("\n✅ Connected to Railway PostgreSQL")
print(f"   Host: {db_url.split('@')[1].split(':')[0] if '@' in db_url else 'unknown'}")

# Get username
username = input("\n👤 Enter your admin username (default: BigDaddy2): ").strip() or "BigDaddy2"

print(f"\n🔧 Running admin setup for: {username}")
print("   This will:")
print("   - Migrate database (add new columns)")
print("   - Set admin_all_access = True")
print("   - Set premium_member = True")
print("   - Generate teacher key\n")

confirm = input("Continue? (y/N): ").strip().lower()

if confirm != 'y':
    print("\n❌ Cancelled by user.")
    sys.exit(0)

print("\n" + "=" * 60)
print("Starting migration and admin setup...")
print("=" * 60 + "\n")

# Import and run the setup script
from setup_admin import migrate_database, setup_admin
from AjaSpellBApp import app

with app.app_context():
    # Run migration first
    if migrate_database():
        print("\n" + "=" * 60)
        print("Database migration complete! Now setting up admin...")
        print("=" * 60 + "\n")
        
        # Then setup admin
        if setup_admin(username):
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Admin setup complete!")
            print("=" * 60)
            print("\nYou can now access /admin/dashboard on Railway")
        else:
            print("\n❌ Admin setup failed. Check the errors above.")
            sys.exit(1)
    else:
        print("\n❌ Migration failed. Check the errors above.")
        sys.exit(1)
