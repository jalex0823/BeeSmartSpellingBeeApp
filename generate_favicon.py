"""
Generate favicon from BeeSmartLogoTransparent.png
Creates multiple sizes for different platforms
"""
from PIL import Image
import os

def generate_favicon():
    """Generate favicon.ico and various sizes from logo"""
    logo_path = 'static/BeeSmartLogoTransparent.png'
    
    if not os.path.exists(logo_path):
        print(f"❌ Logo not found at {logo_path}")
        return
    
    # Open the logo
    img = Image.open(logo_path)
    
    # Convert RGBA to RGB for ICO format
    if img.mode == 'RGBA':
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        img = background
    
    # Generate favicon.ico with multiple sizes
    sizes = [(16, 16), (32, 32), (48, 48)]
    img.save('static/favicon.ico', format='ICO', sizes=sizes)
    print(f"✅ Generated static/favicon.ico")
    
    # Generate PNG favicons for different purposes
    favicon_sizes = {
        'favicon-16x16.png': (16, 16),
        'favicon-32x32.png': (32, 32),
        'favicon-96x96.png': (96, 96),
        'apple-touch-icon.png': (180, 180),
        'android-chrome-192x192.png': (192, 192),
        'android-chrome-512x512.png': (512, 512)
    }
    
    # Reopen original with alpha for PNGs
    img = Image.open(logo_path)
    
    for filename, size in favicon_sizes.items():
        resized = img.resize(size, Image.Resampling.LANCZOS)
        resized.save(f'static/{filename}')
        print(f"✅ Generated static/{filename}")
    
    print("\n🎉 All favicon files generated successfully!")
    print("\nNext steps:")
    print("1. Update base templates to include favicon links")
    print("2. Commit and push to production")

if __name__ == '__main__':
    generate_favicon()
