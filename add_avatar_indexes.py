#!/usr/bin/env python3
"""
Add database indexes to Avatar table for improved query performance.
Run this script on Railway and locally to optimize avatar queries.
"""

import os
import sys
from sqlalchemy import text, inspect

# Import app and database
from AjaSpellBApp import app, db

def add_avatar_indexes():
    """Add indexes to Avatar table to speed up queries"""
    
    with app.app_context():
        print("🔧 Adding indexes to Avatar table...")
        
        # Get database engine and inspector
        engine = db.get_engine()
        inspector = inspect(engine)
        
        # Check existing indexes
        existing_indexes = {idx['name'] for idx in inspector.get_indexes('avatars')}
        print(f"📋 Existing indexes: {existing_indexes}")
        
        indexes_to_add = []
        
        # Single column indexes
        if 'ix_avatars_name' not in existing_indexes:
            indexes_to_add.append("CREATE INDEX ix_avatars_name ON avatars(name)")
        
        if 'ix_avatars_description' not in existing_indexes:
            indexes_to_add.append("CREATE INDEX ix_avatars_description ON avatars(description)")
        
        if 'ix_avatars_sort_order' not in existing_indexes:
            indexes_to_add.append("CREATE INDEX ix_avatars_sort_order ON avatars(sort_order)")
        
        if 'ix_avatars_is_active' not in existing_indexes:
            indexes_to_add.append("CREATE INDEX ix_avatars_is_active ON avatars(is_active)")
        
        # Composite indexes for common query patterns
        if 'idx_active_sorted' not in existing_indexes:
            indexes_to_add.append("CREATE INDEX idx_active_sorted ON avatars(is_active, sort_order, name)")
        
        if 'idx_category_active' not in existing_indexes:
            indexes_to_add.append("CREATE INDEX idx_category_active ON avatars(category, is_active)")
        
        # Add indexes
        if not indexes_to_add:
            print("✅ All indexes already exist!")
            return
        
        print(f"➕ Adding {len(indexes_to_add)} new indexes...")
        
        with engine.connect() as conn:
            for sql in indexes_to_add:
                try:
                    print(f"   Executing: {sql}")
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"   ✅ Success")
                except Exception as e:
                    print(f"   ⚠️  Error: {e}")
        
        print("\n🎉 Index creation complete!")
        
        # Show final indexes
        inspector = inspect(engine)
        final_indexes = inspector.get_indexes('avatars')
        print(f"\n📊 Final indexes on avatars table:")
        for idx in final_indexes:
            print(f"   - {idx['name']}: {idx['column_names']}")

if __name__ == '__main__':
    add_avatar_indexes()
