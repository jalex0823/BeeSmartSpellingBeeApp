#!/usr/bin/env python3
"""
Clean up avatar picker display issues
1. Remove remaining inactive duplicates showing as placeholders
2. Verify Franken Bee thumbnail is correct
"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("🔍 Checking for placeholder/duplicate avatars...\n")
    
    # Check for avatars that might be showing as placeholders
    result = conn.execute(text("""
        SELECT slug, name, is_active, thumbnail_file 
        FROM avatars 
        WHERE name LIKE '%Buzzbot%' OR name LIKE '%Doctor Bee%' OR slug LIKE '%franken%'
        ORDER BY slug
    """))
    
    avatars = list(result)
    
    print("Found avatars:")
    for av in avatars:
        status = "ACTIVE" if av[2] else "INACTIVE"
        print(f"  {av[0]:<20} | {av[1]:<30} | {status} | {av[3]}")
    
    print("\n🗑️  Removing placeholders/duplicates...\n")
    
    # Remove any remaining "Buzzbot Bee" or "Doctor Bee" that aren't the proper ones
    slugs_to_remove = []
    
    for av in avatars:
        slug, name, is_active, thumb = av
        # Remove if it's not the canonical version
        if ('buzzbot' in name.lower() or 'doctor bee' in name.lower()) and slug not in ['robo-bee', 'doc-bee']:
            slugs_to_remove.append(slug)
    
    if slugs_to_remove:
        for slug in slugs_to_remove:
            print(f"  ✓ Removing '{slug}'")
            conn.execute(text("DELETE FROM avatars WHERE slug = :slug"), {"slug": slug})
        conn.commit()
    else:
        print("  ℹ️  No duplicates to remove")
    
    # Verify Franken Bee thumbnail
    print("\n🔍 Checking Franken Bee thumbnail...")
    result = conn.execute(text("""
        SELECT slug, name, thumbnail_file 
        FROM avatars 
        WHERE slug LIKE '%franken%' AND is_active = true
    """))
    
    franken = result.fetchone()
    if franken:
        print(f"  Current: {franken[0]} -> {franken[2]}")
        correct_thumb = "AvatarThumbnails/FrankenBee!.png"
        if franken[2] != correct_thumb:
            print(f"  ✓ Updating to: {correct_thumb}")
            conn.execute(text("""
                UPDATE avatars 
                SET thumbnail_file = :thumb 
                WHERE slug = :slug
            """), {"thumb": correct_thumb, "slug": franken[0]})
            conn.commit()
        else:
            print(f"  ✅ Already correct!")
    
    # Final check
    print("\n📊 Final active avatar count:")
    result = conn.execute(text("SELECT COUNT(*) FROM avatars WHERE is_active = true"))
    count = result.scalar()
    print(f"  Active avatars: {count}")
    
    print("\n✅ Cleanup complete!")
