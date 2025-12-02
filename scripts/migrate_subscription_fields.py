#!/usr/bin/env python3
"""
Database Migration: Add Subscription Fields to User Table

Adds new columns for App Store subscription tracking:
- subscription_type, subscription_product_id
- subscription_status, subscription_expires_at
- subscription_auto_renew, original_transaction_id
- latest_receipt_data, subscription_started_at
- subscription_canceled_at, family_shared_from

Run this script ONCE after deploying new User model to Railway/production.

Usage:
    python scripts/migrate_subscription_fields.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from sqlalchemy import text, inspect
from models import db, User
from AjaSpellBApp import app


def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if column already exists in table"""
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        print(f"⚠️ Error checking column: {e}")
        return False


def migrate_subscription_fields():
    """Add subscription tracking fields to users table"""
    
    print("=" * 60)
    print("🔄 MIGRATION: Add Subscription Fields to User Table")
    print("=" * 60)
    
    with app.app_context():
        try:
            # List of columns to add with their SQL definitions
            columns_to_add = [
                ("subscription_type", "VARCHAR(50)"),
                ("subscription_product_id", "VARCHAR(100)"),
                ("subscription_status", "VARCHAR(20) DEFAULT 'none'"),
                ("subscription_expires_at", "TIMESTAMP"),
                ("subscription_auto_renew", "BOOLEAN DEFAULT TRUE"),
                ("original_transaction_id", "VARCHAR(100) UNIQUE"),
                ("latest_receipt_data", "TEXT"),
                ("subscription_started_at", "TIMESTAMP"),
                ("subscription_canceled_at", "TIMESTAMP"),
                ("family_shared_from", "VARCHAR(100)")
            ]
            
            print(f"\n📊 Checking table: users")
            print(f"📦 Columns to add: {len(columns_to_add)}\n")
            
            added_count = 0
            skipped_count = 0
            
            for column_name, column_type in columns_to_add:
                # Check if column already exists
                if check_column_exists('users', column_name):
                    print(f"⏭️  Skipped: {column_name} (already exists)")
                    skipped_count += 1
                    continue
                
                try:
                    # Add column with ALTER TABLE
                    sql = text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                    db.session.execute(sql)
                    db.session.commit()
                    
                    print(f"✅ Added: {column_name} ({column_type})")
                    added_count += 1
                    
                except Exception as e:
                    print(f"❌ Failed to add {column_name}: {e}")
                    db.session.rollback()
            
            # Add indexes for performance
            indexes_to_add = [
                ("idx_users_subscription_type", "subscription_type"),
                ("idx_users_subscription_expires", "subscription_expires_at"),
                ("idx_users_original_transaction", "original_transaction_id")
            ]
            
            print(f"\n📊 Adding indexes for query performance...\n")
            
            for index_name, column_name in indexes_to_add:
                try:
                    # Check if index already exists
                    check_sql = text(f"""
                        SELECT COUNT(*) 
                        FROM pg_indexes 
                        WHERE indexname = :index_name
                    """)
                    result = db.session.execute(check_sql, {"index_name": index_name})
                    exists = result.scalar() > 0
                    
                    if exists:
                        print(f"⏭️  Skipped index: {index_name} (already exists)")
                        continue
                    
                    # Create index
                    sql = text(f"CREATE INDEX {index_name} ON users({column_name})")
                    db.session.execute(sql)
                    db.session.commit()
                    
                    print(f"✅ Added index: {index_name} on {column_name}")
                    
                except Exception as e:
                    print(f"⚠️ Index {index_name}: {e}")
                    db.session.rollback()
            
            print("\n" + "=" * 60)
            print("📊 MIGRATION SUMMARY")
            print("=" * 60)
            print(f"✅ Columns added: {added_count}")
            print(f"⏭️  Columns skipped: {skipped_count}")
            print(f"📝 Total columns: {len(columns_to_add)}")
            print("=" * 60)
            
            if added_count > 0:
                print("\n✨ Migration completed successfully!")
                print("\n🔑 IMPORTANT: Set APPLE_SHARED_SECRET environment variable")
                print("   Get this from App Store Connect → My Apps → Your App → App Information")
                print("   Add to Railway: Settings → Variables → APPLE_SHARED_SECRET=your_secret")
            else:
                print("\n✨ No changes needed - all columns already exist!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def verify_migration():
    """Verify all subscription columns exist"""
    
    print("\n" + "=" * 60)
    print("🔍 VERIFICATION: Checking Subscription Fields")
    print("=" * 60)
    
    with app.app_context():
        try:
            required_columns = [
                'subscription_type',
                'subscription_product_id',
                'subscription_status',
                'subscription_expires_at',
                'subscription_auto_renew',
                'original_transaction_id',
                'latest_receipt_data',
                'subscription_started_at',
                'subscription_canceled_at',
                'family_shared_from'
            ]
            
            all_exist = True
            
            for column in required_columns:
                exists = check_column_exists('users', column)
                status = "✅" if exists else "❌"
                print(f"{status} {column}")
                if not exists:
                    all_exist = False
            
            print("=" * 60)
            
            if all_exist:
                print("✅ All subscription columns verified!")
                
                # Test query
                print("\n🧪 Testing subscription query...")
                user = User.query.first()
                if user:
                    status = user.get_subscription_status()
                    print(f"✅ Subscription status query successful: {status['status']}")
                else:
                    print("⚠️ No users in database to test query")
                
                return True
            else:
                print("❌ Some columns are missing!")
                return False
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print("\n🚀 Starting subscription fields migration...\n")
    
    # Check database connection
    print("🔗 Testing database connection...")
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            print("✅ Database connected successfully\n")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("\n💡 Make sure DATABASE_URL is set correctly")
            sys.exit(1)
    
    # Run migration
    success = migrate_subscription_fields()
    
    if not success:
        print("\n❌ Migration failed! Check errors above.")
        sys.exit(1)
    
    # Verify migration
    print("\n")
    verified = verify_migration()
    
    if verified:
        print("\n" + "=" * 60)
        print("🎉 MIGRATION COMPLETE!")
        print("=" * 60)
        print("\n📱 Next steps:")
        print("1. Set APPLE_SHARED_SECRET in Railway environment variables")
        print("2. Configure webhook URL in App Store Connect:")
        print("   https://your-railway-domain.up.railway.app/apple-webhook")
        print("3. Test subscription purchase in sandbox environment")
        print("4. Deploy iOS app with StoreKit integration")
        print("\n✅ Backend is ready for App Store subscriptions!")
        sys.exit(0)
    else:
        print("\n❌ Verification failed!")
        sys.exit(1)
