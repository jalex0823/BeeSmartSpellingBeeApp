"""
Make Favicon Backgrounds Transparent
=====================================
Converts all favicon PNG files to have transparent backgrounds.
Removes white or light-colored backgrounds and keeps the bee logo.
"""

from PIL import Image
import os

def make_background_transparent(image_path, output_path=None, threshold=240):
    """
    Make white/light backgrounds transparent in an image.
    
    Args:
        image_path: Path to input image
        output_path: Path for output (None = overwrite original)
        threshold: RGB value threshold for transparency (default 240 = light colors)
    """
    if output_path is None:
        output_path = image_path
    
    # Open image and convert to RGBA
    img = Image.open(image_path)
    img = img.convert("RGBA")
    
    # Get pixel data
    pixels = img.load()
    width, height = img.size
    
    # Make light pixels transparent
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            
            # If pixel is light (close to white), make it transparent
            if r >= threshold and g >= threshold and b >= threshold:
                pixels[x, y] = (r, g, b, 0)  # Set alpha to 0 (transparent)
    
    # Save with transparency
    img.save(output_path, "PNG")
    print(f"✅ Processed: {os.path.basename(output_path)}")

def main():
    """Process all favicon files"""
    print("\n🐝 BeeSmart Favicon Transparency Tool")
    print("=" * 60)
    
    favicon_files = [
        "static/favicon-16x16.png",
        "static/favicon-32x32.png",
        "static/favicon-96x96.png",
        "static/favicon-192x192.png",
        "static/favicon-512x512.png",
        "static/apple-touch-icon.png"
    ]
    
    processed = 0
    
    for filepath in favicon_files:
        if os.path.exists(filepath):
            try:
                # Create backup
                backup_path = filepath.replace(".png", "_backup.png")
                if not os.path.exists(backup_path):
                    img = Image.open(filepath)
                    img.save(backup_path)
                    print(f"📦 Backup created: {os.path.basename(backup_path)}")
                
                # Make transparent
                make_background_transparent(filepath, threshold=240)
                processed += 1
                
            except Exception as e:
                print(f"❌ Error processing {filepath}: {e}")
        else:
            print(f"⚠️ File not found: {filepath}")
    
    print("\n" + "=" * 60)
    print(f"✅ Processed {processed} favicon files")
    print("💡 Original files backed up with '_backup.png' suffix")
    print("=" * 60)

if __name__ == "__main__":
    main()
