"""
Add thumbnail validation to avatar API - ensures only avatars with existing thumbnails are returned
"""
import os

# Read the current file
with open('AjaSpellBApp.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the spot where we build enriched_avatars from DB query
# Look for the line: thumb_cb = _cachebust_url(thumb_url) if thumb_url else None

old_code = """                    # Build thumb/preview with cache-busting
                    thumb_url = f"{base_path}/{avatar.thumbnail_file}" if avatar.thumbnail_file else None
                    thumb_cb = _cachebust_url(thumb_url) if thumb_url else None
                    
                    enriched_avatars.append({"""

new_code = """                    # Build thumb/preview with cache-busting and VALIDATE file exists
                    thumb_url = f"{base_path}/{avatar.thumbnail_file}" if avatar.thumbnail_file else None
                    thumb_cb = None
                    
                    # CRITICAL: Only include avatar if thumbnail actually exists on disk
                    if thumb_url:
                        # Check if thumbnail file exists
                        thumb_rel_path = thumb_url.lstrip('/')
                        thumb_fs_path = os.path.join(app.root_path, thumb_rel_path)
                        
                        if os.path.exists(thumb_fs_path):
                            thumb_cb = _cachebust_url(thumb_url)
                        else:
                            # Skip avatar with missing thumbnail - don't add to response
                            print(f"⚠️ [API] Skipping avatar '{avatar.name}' ({avatar.slug}): thumbnail not found at {thumb_fs_path}")
                            continue
                    else:
                        # No thumbnail path in database - skip this avatar
                        print(f"⚠️ [API] Skipping avatar '{avatar.name}' ({avatar.slug}): no thumbnail_file in database")
                        continue
                    
                    enriched_avatars.append({"""

if old_code in content:
    content = content.replace(old_code, new_code)
    
    # Write back
    with open('AjaSpellBApp.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added thumbnail validation to avatar API!")
    print("   - Avatars with missing thumbnails will be skipped")
    print("   - API will log which avatars were skipped")
else:
    print("❌ Could not find target code - file may have already been updated or structure changed")
