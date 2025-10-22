"""
Create proper thumbnail images for avatar selection
Uses preview.png files where available, otherwise uses texture.png
"""

from PIL import Image
import os

AVATAR_DIR = "static/assets/avatars"
AVATARS = [
    "cool-bee", "explorer-bee", "rockstar-bee", "doctor-bee",
    "scientist-bee", "professor-bee", "superhero-bee", "knight-bee",
    "robot-bee", "bee-diva", "queen-bee", "majesty-bee",
    "sea-bee", "biker-bee", "killer-bee", "anxious-bee"
]

def create_thumbnails():
    """Create 200x200 thumbnails from preview or texture files"""
    
    for avatar_id in AVATARS:
        avatar_path = os.path.join(AVATAR_DIR, avatar_id)
        
        if not os.path.exists(avatar_path):
            print(f"⚠️  Skipping {avatar_id} - folder not found")
            continue
        
        # Try to use preview.png first, fall back to texture.png
        preview_path = os.path.join(avatar_path, "preview.png")
        texture_path = os.path.join(avatar_path, "texture.png")
        thumbnail_path = os.path.join(avatar_path, "thumbnail.png")
        
        source_file = None
        if os.path.exists(preview_path):
            source_file = preview_path
            source_type = "preview"
        elif os.path.exists(texture_path):
            source_file = texture_path
            source_type = "texture"
        
        if not source_file:
            print(f"❌ {avatar_id}: No source file found")
            continue
        
        try:
            # Open source image
            img = Image.open(source_file)
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to 200x200 with high quality
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Save as thumbnail
            img.save(thumbnail_path, 'PNG', quality=95, optimize=True)
            
            size_kb = os.path.getsize(thumbnail_path) / 1024
            print(f"✅ {avatar_id}: Created from {source_type} ({size_kb:.1f} KB)")
            
        except Exception as e:
            print(f"❌ {avatar_id}: Error - {e}")

if __name__ == '__main__':
    print("🐝 Creating Avatar Thumbnails")
    print("=" * 50)
    create_thumbnails()
    print("=" * 50)
    print("✨ Thumbnail creation complete!")
