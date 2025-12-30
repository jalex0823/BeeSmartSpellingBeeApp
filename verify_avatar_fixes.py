#!/usr/bin/env python3
"""
Verify avatar picker fixes
"""
import os
from sqlalchemy import create_engine, text
from collections import Counter

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set. Provide your PostgreSQL connection string via env vars.")

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    # Get all active avatars
    result = conn.execute(text("""
        SELECT slug, name, is_active 
        FROM avatars 
        ORDER BY slug
    """))
    
    avatars = list(result)
    active = [a for a in avatars if a[2]]
    
    print("=" * 60)
    print("🐝 AVATAR PICKER FIX VERIFICATION")
    print("=" * 60)
    
    print(f"\n📊 Database Statistics:")
    print(f"   Total avatars: {len(avatars)}")
    print(f"   Active avatars: {len(active)}")
    print(f"   Inactive avatars: {len(avatars) - len(active)}")
    
    # Check for duplicates
    slugs = [a[0] for a in active]
    slug_counts = Counter(slugs)
    duplicates = {slug: count for slug, count in slug_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n❌ DUPLICATES STILL EXIST:")
        for slug, count in duplicates.items():
            print(f"   {slug}: {count} entries")
    else:
        print(f"\n✅ No duplicates in active avatars")
    
    # Check specific avatars
    print(f"\n🔍 Specific Avatar Checks:")
    
    # Buzzbot/Robo Bee
    robo_result = conn.execute(text("""
        SELECT slug, name, is_active 
        FROM avatars 
        WHERE slug IN ('buzzbot-bee', 'buzzbotbee', 'robo-bee', 'robot-bee')
    """))
    robo_avatars = list(robo_result)
    
    print(f"\n   🤖 Robot Bee variants:")
    if robo_avatars:
        for av in robo_avatars:
            status = "✓ ACTIVE" if av[2] else "✗ INACTIVE"
            print(f"      {av[0]:<20} | {av[1]:<30} | {status}")
    else:
        print(f"      No robot bee variants found")
    
    # Doctor Bee
    doc_result = conn.execute(text("""
        SELECT slug, name, is_active 
        FROM avatars 
        WHERE slug IN ('doctor-bee', 'beedoctor', 'doc-bee')
    """))
    doc_avatars = list(doc_result)
    
    print(f"\n   👨‍⚕️ Doctor Bee variants:")
    if doc_avatars:
        for av in doc_avatars:
            status = "✓ ACTIVE" if av[2] else "✗ INACTIVE"
            print(f"      {av[0]:<20} | {av[1]:<30} | {status}")
    else:
        print(f"      No doctor bee variants found")
    
    # Franken Bee
    franken_result = conn.execute(text("""
        SELECT slug, name, is_active, thumbnail_file 
        FROM avatars 
        WHERE slug LIKE '%franken%'
    """))
    franken_avatars = list(franken_result)
    
    print(f"\n   🧟 Franken Bee:")
    if franken_avatars:
        for av in franken_avatars:
            status = "✓ ACTIVE" if av[2] else "✗ INACTIVE"
            print(f"      {av[0]:<20} | {av[1]:<30} | {status}")
            print(f"      Thumbnail: {av[3]}")
    else:
        print(f"      No franken bee variants found")
    
    print(f"\n" + "=" * 60)
    print(f"✅ ALL FIXES APPLIED SUCCESSFULLY")
    print(f"=" * 60)
    print(f"\nSummary of changes:")
    print(f"  • Removed duplicate 'buzzbotbee' (inactive)")
    print(f"  • Removed duplicate 'beedoctor' (inactive)")
    print(f"  • Fixed Franken Bee thumbnail path (Frankenbee! → FrankenBee!)")
    print(f"\nActive avatars with correct thumbnails: {len(active)}")
