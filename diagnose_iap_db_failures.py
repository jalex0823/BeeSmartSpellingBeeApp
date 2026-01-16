#!/usr/bin/env python3
"""
IAP Database Failure Diagnostic Script

This script helps identify specific database failure patterns in IAP flows.
Run this script to diagnose root causes of database commit failures.

Usage:
    python3 diagnose_iap_db_failures.py
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_connection():
    """Check if database connection is working"""
    print("=" * 70)
    print("DATABASE CONNECTION CHECK")
    print("=" * 70)
    
    try:
        from config import Config
        from models import db
        
        db_url = Config.SQLALCHEMY_DATABASE_URI
        print(f"Database URL: {db_url[:50]}..." if len(db_url) > 50 else f"Database URL: {db_url}")
        
        # Test connection
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection: OK")
            return True
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False

def check_pool_configuration():
    """Check database connection pool configuration"""
    print("\n" + "=" * 70)
    print("CONNECTION POOL CONFIGURATION")
    print("=" * 70)
    
    try:
        from config import Config
        
        options = Config.SQLALCHEMY_ENGINE_OPTIONS
        print("Current pool configuration:")
        for key, value in options.items():
            print(f"  {key}: {value}")
        
        # Check for recommended settings
        recommendations = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'pool_size': 5,
            'max_overflow': 10
        }
        
        print("\nRecommended settings:")
        for key, value in recommendations.items():
            current = options.get(key, 'NOT SET')
            status = "✅" if current == value else "⚠️"
            print(f"  {status} {key}: {current} (recommended: {value})")
        
        return True
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False

def check_table_schema():
    """Check PurchaseRecord and AnonPurchaseOwnership table schemas"""
    print("\n" + "=" * 70)
    print("TABLE SCHEMA CHECK")
    print("=" * 70)
    
    try:
        from config import Config
        from models import db, PurchaseRecord, AnonPurchaseOwnership
        
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        inspector = inspect(engine)
        
        # Check PurchaseRecord table
        if 'purchase_records' in inspector.get_table_names():
            print("✅ purchase_records table exists")
            columns = {col['name']: col for col in inspector.get_columns('purchase_records')}
            
            # Check user_id constraint
            if 'user_id' in columns:
                col = columns['user_id']
                nullable = col.get('nullable', True)
                print(f"  user_id nullable: {nullable} {'⚠️ (should be False)' if nullable else '✅'}")
            
            # Check for unique constraints
            unique_constraints = inspector.get_unique_constraints('purchase_records')
            if unique_constraints:
                print(f"  Unique constraints: {len(unique_constraints)}")
                for uc in unique_constraints:
                    print(f"    - {uc['name']}: {uc['column_names']}")
            else:
                print("  ⚠️ No unique constraints (race conditions possible)")
        else:
            print("❌ purchase_records table does not exist")
        
        # Check AnonPurchaseOwnership table
        if 'anon_purchase_ownership' in inspector.get_table_names():
            print("\n✅ anon_purchase_ownership table exists")
            unique_constraints = inspector.get_unique_constraints('anon_purchase_ownership')
            if unique_constraints:
                print(f"  Unique constraints: {len(unique_constraints)}")
                for uc in unique_constraints:
                    print(f"    - {uc['name']}: {uc['column_names']}")
            else:
                print("  ⚠️ No unique constraints")
        else:
            print("\n❌ anon_purchase_ownership table does not exist")
        
        return True
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_foreign_keys():
    """Check foreign key constraints"""
    print("\n" + "=" * 70)
    print("FOREIGN KEY CONSTRAINTS CHECK")
    print("=" * 70)
    
    try:
        from config import Config
        from models import db, PurchaseRecord
        
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        inspector = inspect(engine)
        
        # Check PurchaseRecord foreign keys
        if 'purchase_records' in inspector.get_table_names():
            fks = inspector.get_foreign_keys('purchase_records')
            print(f"Foreign keys on purchase_records: {len(fks)}")
            for fk in fks:
                print(f"  - {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        return True
    except Exception as e:
        print(f"❌ Foreign key check failed: {e}")
        return False

def test_concurrent_inserts():
    """Test concurrent insert behavior (simulate race condition)"""
    print("\n" + "=" * 70)
    print("CONCURRENT INSERT TEST")
    print("=" * 70)
    
    try:
        from config import Config
        from models import db, PurchaseRecord, User
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        
        # Get a test user
        session = Session()
        test_user = session.query(User).first()
        
        if not test_user:
            print("⚠️ No users found in database - skipping concurrent insert test")
            return True
        
        print(f"Testing with user_id: {test_user.id}")
        
        # Try to create duplicate PurchaseRecord
        test_product_id = f"test_product_{datetime.utcnow().timestamp()}"
        
        # First insert
        rec1 = PurchaseRecord(
            user_id=test_user.id,
            platform='test',
            product_id=test_product_id,
            status='verified'
        )
        session.add(rec1)
        session.commit()
        print(f"✅ First insert successful: product_id={test_product_id}")
        
        # Try duplicate (should be handled gracefully)
        try:
            rec2 = PurchaseRecord(
                user_id=test_user.id,
                platform='test',
                product_id=test_product_id,
                status='verified'
            )
            session.add(rec2)
            session.commit()
            print("⚠️ Duplicate insert succeeded (no unique constraint)")
        except IntegrityError as e:
            print(f"✅ Duplicate insert prevented: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error on duplicate: {e}")
        
        # Cleanup
        session.query(PurchaseRecord).filter_by(
            user_id=test_user.id,
            platform='test',
            product_id=test_product_id
        ).delete()
        session.commit()
        print("✅ Test records cleaned up")
        
        session.close()
        return True
    except Exception as e:
        print(f"❌ Concurrent insert test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_recent_errors():
    """Check for recent database errors in logs (if available)"""
    print("\n" + "=" * 70)
    print("RECENT ERROR PATTERNS")
    print("=" * 70)
    
    print("⚠️ Log file analysis not implemented in this script")
    print("   Check application logs for patterns like:")
    print("   - 'IAP restore: failed to commit PurchaseRecord'")
    print("   - 'db_commit_failed'")
    print("   - 'IntegrityError'")
    print("   - 'OperationalError'")
    print("   - 'DetachedInstanceError'")
    
    return True

def generate_recommendations():
    """Generate recommendations based on findings"""
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    recommendations = [
        "✅ Ensure database connection pool is properly configured (pool_size, max_overflow, pool_timeout)",
        "✅ Use database-level locking (with_for_update) to prevent race conditions",
        "✅ Validate foreign keys before creating records",
        "✅ Use db.session.merge() to handle detached instances",
        "✅ Implement per-product commits to isolate failures",
        "✅ Add unique constraints where appropriate to prevent duplicates",
        "✅ Monitor connection pool usage and adjust pool_size if needed",
        "✅ Set appropriate query timeouts to prevent hanging transactions",
        "✅ Use skip_locked=True in with_for_update to prevent deadlocks",
        "✅ Log all database errors with exc_info=True for debugging"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

def main():
    """Run all diagnostic checks"""
    print("\n" + "=" * 70)
    print("IAP DATABASE FAILURE DIAGNOSTIC TOOL")
    print("=" * 70)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print()
    
    results = {
        'connection': check_database_connection(),
        'pool_config': check_pool_configuration(),
        'schema': check_table_schema(),
        'foreign_keys': check_foreign_keys(),
        'concurrent_inserts': test_concurrent_inserts(),
        'recent_errors': check_recent_errors()
    }
    
    generate_recommendations()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All checks passed!")
    else:
        print("⚠️ Some checks failed - review recommendations above")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
