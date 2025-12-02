#!/usr/bin/env python3
"""
Check for duplicate avatars in the Railway database
"""
import os
from sqlalchemy import create_engine, text
from collections import Counter

# Railway PostgreSQL connection string (from AVATAR_CATALOG_SYNC_COMPLETE_NOV13.md)
DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all avatar slugs
        result = conn.execute(text("""
            SELECT slug, name, is_active 
            FROM avatars 
            ORDER BY slug
        """))
        
        avatars = list(result)
        
        print(f"\n📊 Total avatars in database: {len(avatars)}")
        print(f"   Active avatars: {sum(1 for a in avatars if a[2])}")
        print(f"   Inactive avatars: {sum(1 for a in avatars if not a[2])}")
        
        # Check for duplicates
        slugs = [a[0] for a in avatars if a[2]]  # Only active
        slug_counts = Counter(slugs)
        duplicates = {slug: count for slug, count in slug_counts.items() if count > 1}
        
        if duplicates:
            print(f"\n⚠️  DUPLICATES FOUND:")
            for slug, count in duplicates.items():
                print(f"   {slug}: {count} entries")
                matching = [a for a in avatars if a[0] == slug and a[2]]
                for av in matching:
                    print(f"      - {av[1]}")
        else:
            print(f"\n✅ No duplicates found in active avatars")
        
        # List all active avatars
        print(f"\n📝 Active avatars ({sum(1 for a in avatars if a[2])}):")
        for slug, name, is_active in sorted(avatars):
            if is_active:
                status = "✓"
            else:
                status = "✗"
            print(f"   {status} {slug:<20} | {name}")
        
        # Check for specific problem avatars
        problem_slugs = ['buzzbot-bee', 'robot-bee', 'robo-bee', 'doctor-bee', 'doc-bee']
        print(f"\n🔍 Checking for known problem slugs:")
        for slug in problem_slugs:
            matching = [a for a in avatars if a[0] == slug]
            if matching:
                for av in matching:
                    status = "ACTIVE" if av[2] else "INACTIVE"
                    print(f"   {slug}: {av[1]} ({status})")
            else:
                print(f"   {slug}: NOT FOUND")
                
except Exception as e:
    print(f"❌ Error: {e}")
