#!/usr/bin/env python3
"""
Check Franken Bee thumbnail configuration
"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT slug, name, thumbnail_file, folder_path 
        FROM avatars 
        WHERE slug LIKE '%franken%'
    """))
    
    print("🔍 Franken Bee database entries:")
    for row in result:
        print(f"   Slug: {row[0]}")
        print(f"   Name: {row[1]}")
        print(f"   Thumbnail: {row[2]}")
        print(f"   Folder: {row[3]}")
        print()
