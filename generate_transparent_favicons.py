"""
Generate transparent favicon PNG files from BeeSmartCrestLogo1.png
This creates proper favicon files with transparency instead of white backgrounds
"""
from PIL import Image
import os

# Source logo with transparency
source_logo = 'static/BeeSmartCrestLogo1.png'

# Favicon sizes to generate
sizes = [16, 32, 96, 192, 512]

print(f"📸 Loading source logo: {source_logo}")
logo = Image.open(source_logo)

if logo.mode != 'RGBA':
    print(f"⚠️  Converting {logo.mode} to RGBA for transparency...")
    logo = logo.convert('RGBA')

print(f"✅ Source image: {logo.size} ({logo.mode})")

# Generate each size
for size in sizes:
    output_file = f'static/favicon-{size}x{size}.png'
    
    # Create a new RGBA image with transparent background
    resized = logo.resize((size, size), Image.Resampling.LANCZOS)
    
    # Save with transparency
    resized.save(output_file, 'PNG', optimize=True)
    print(f"✅ Generated: {output_file} ({size}x{size}px)")

# Also generate android-chrome icons if they don't exist
android_sizes = [(192, 'android-chrome-192x192.png'), (512, 'android-chrome-512x512.png')]
for size, filename in android_sizes:
    output_file = f'static/{filename}'
    resized = logo.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(output_file, 'PNG', optimize=True)
    print(f"✅ Generated: {output_file} ({size}x{size}px)")

print("\n🎉 All transparent favicons generated!")
print("\n📝 Note: favicon.ico will still show white background (ICO format limitation)")
print("   Browsers will use PNG versions which have proper transparency")
