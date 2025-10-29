"""
BeeSmart Mobile App - Asset Generator
Generates app icons and splash screens for iOS and Android from base images
"""

import os
from PIL import Image, ImageDraw, ImageFont
import json

# Asset specifications
IOS_ICON_SIZES = {
    'icon-20.png': (20, 20),
    'icon-20@2x.png': (40, 40),
    'icon-20@3x.png': (60, 60),
    'icon-29.png': (29, 29),
    'icon-29@2x.png': (58, 58),
    'icon-29@3x.png': (87, 87),
    'icon-40.png': (40, 40),
    'icon-40@2x.png': (80, 80),
    'icon-40@3x.png': (120, 120),
    'icon-60@2x.png': (120, 120),
    'icon-60@3x.png': (180, 180),
    'icon-76.png': (76, 76),
    'icon-76@2x.png': (152, 152),
    'icon-83.5@2x.png': (167, 167),
    'icon-1024.png': (1024, 1024),
}

ANDROID_ICON_SIZES = {
    'mipmap-mdpi/ic_launcher.png': (48, 48),
    'mipmap-hdpi/ic_launcher.png': (72, 72),
    'mipmap-xhdpi/ic_launcher.png': (96, 96),
    'mipmap-xxhdpi/ic_launcher.png': (144, 144),
    'mipmap-xxxhdpi/ic_launcher.png': (192, 192),
}

IOS_SPLASH_SIZES = {
    'splash-1170x2532.png': (1170, 2532),  # iPhone 13/14/15 Pro Max
    'splash-1284x2778.png': (1284, 2778),  # iPhone 14 Pro Max
    'splash-1125x2436.png': (1125, 2436),  # iPhone X/11 Pro/12 Mini
    'splash-828x1792.png': (828, 1792),    # iPhone XR/11
    'splash-2048x2732.png': (2048, 2732),  # iPad Pro 12.9"
    'splash-1668x2388.png': (1668, 2388),  # iPad Pro 11"
}

ANDROID_SPLASH_SIZES = {
    'drawable-land-mdpi/splash.png': (480, 320),
    'drawable-land-hdpi/splash.png': (800, 480),
    'drawable-land-xhdpi/splash.png': (1280, 720),
    'drawable-land-xxhdpi/splash.png': (1600, 960),
    'drawable-land-xxxhdpi/splash.png': (1920, 1280),
    'drawable-port-mdpi/splash.png': (320, 480),
    'drawable-port-hdpi/splash.png': (480, 800),
    'drawable-port-xhdpi/splash.png': (720, 1280),
    'drawable-port-xxhdpi/splash.png': (960, 1600),
    'drawable-port-xxxhdpi/splash.png': (1280, 1920),
}


def create_app_icon(base_image_path, output_dir, platform='ios'):
    """Generate app icons from base image"""
    print(f"🎨 Generating {platform.upper()} app icons...")
    
    try:
        base_img = Image.open(base_image_path).convert('RGBA')
    except FileNotFoundError:
        print(f"❌ Base image not found: {base_image_path}")
        print("Creating placeholder icon...")
        base_img = create_placeholder_icon()
    
    sizes = IOS_ICON_SIZES if platform == 'ios' else ANDROID_ICON_SIZES
    
    for filename, size in sizes.items():
        # Create output directory
        filepath = os.path.join(output_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Resize and save
        resized = base_img.resize(size, Image.Resampling.LANCZOS)
        
        # iOS requires no alpha channel for 1024x1024
        if platform == 'ios' and size == (1024, 1024):
            rgb_img = Image.new('RGB', size, (255, 215, 0))  # Gold background
            rgb_img.paste(resized, (0, 0), resized)
            rgb_img.save(filepath, 'PNG')
        else:
            resized.save(filepath, 'PNG')
        
        print(f"  ✅ {filename} ({size[0]}x{size[1]})")
    
    print(f"✅ Generated {len(sizes)} {platform.upper()} icons")


def create_splash_screen(base_image_path, output_dir, platform='ios'):
    """Generate splash screens from base image"""
    print(f"🎨 Generating {platform.upper()} splash screens...")
    
    try:
        base_img = Image.open(base_image_path).convert('RGBA')
    except FileNotFoundError:
        print(f"⚠️  Base splash image not found: {base_image_path}")
        print("Creating placeholder splash screens...")
        base_img = create_placeholder_splash()
    
    sizes = IOS_SPLASH_SIZES if platform == 'ios' else ANDROID_SPLASH_SIZES
    
    for filename, size in sizes.items():
        # Create output directory
        filepath = os.path.join(output_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create background
        splash = Image.new('RGB', size, (255, 215, 0))  # Gold background
        
        # Calculate scaling to fit base image
        scale = min(size[0] / base_img.width, size[1] / base_img.height) * 0.6  # 60% of screen
        new_width = int(base_img.width * scale)
        new_height = int(base_img.height * scale)
        
        # Resize and center
        resized = base_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        x = (size[0] - new_width) // 2
        y = (size[1] - new_height) // 2
        
        splash.paste(resized, (x, y), resized)
        splash.save(filepath, 'PNG')
        
        print(f"  ✅ {filename} ({size[0]}x{size[1]})")
    
    print(f"✅ Generated {len(sizes)} {platform.upper()} splash screens")


def create_placeholder_icon():
    """Create a placeholder bee icon if none exists"""
    print("🐝 Creating placeholder bee icon...")
    
    # Create golden hexagon with bee emoji
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw hexagon
    hex_points = []
    center_x, center_y = size // 2, size // 2
    radius = size // 2 - 50
    
    for i in range(6):
        angle = 60 * i - 30  # Start from top
        import math
        x = center_x + radius * math.cos(math.radians(angle))
        y = center_y + radius * math.sin(math.radians(angle))
        hex_points.append((x, y))
    
    # Draw golden hexagon
    draw.polygon(hex_points, fill=(255, 215, 0, 255))
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 300)
    except:
        font = ImageFont.load_default()
    
    text = "🐝"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2
    
    draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0, 255))
    
    return img


def create_placeholder_splash():
    """Create a placeholder splash screen"""
    print("🐝 Creating placeholder splash screen...")
    
    # Create golden background with bee and app name
    img = Image.new('RGBA', (1170, 2532), (255, 215, 0, 255))
    draw = ImageDraw.Draw(img)
    
    # Add bee emoji
    try:
        font_emoji = ImageFont.truetype("seguiemj.ttf", 400)
        font_title = ImageFont.truetype("arialbd.ttf", 120)
        font_subtitle = ImageFont.truetype("arial.ttf", 60)
    except:
        font_emoji = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
    
    # Bee emoji
    bee_text = "🐝"
    bbox = draw.textbbox((0, 0), bee_text, font=font_emoji)
    bee_width = bbox[2] - bbox[0]
    draw.text(((1170 - bee_width) // 2, 800), bee_text, font=font_emoji, fill=(0, 0, 0, 255))
    
    # App title
    title = "BeeSmart"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = bbox[2] - bbox[0]
    draw.text(((1170 - title_width) // 2, 1300), title, font=font_title, fill=(0, 0, 0, 255))
    
    # Subtitle
    subtitle = "Spelling Bee"
    bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = bbox[2] - bbox[0]
    draw.text(((1170 - subtitle_width) // 2, 1450), subtitle, font=font_subtitle, fill=(50, 50, 50, 255))
    
    return img


def generate_all_assets(base_icon_path=None, base_splash_path=None):
    """Generate all mobile app assets"""
    print("🚀 BeeSmart Mobile Asset Generator")
    print("=" * 50)
    
    # Directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mobile_dir = os.path.join(base_dir, 'mobile-wrapper')
    
    ios_icon_dir = os.path.join(mobile_dir, 'ios', 'App', 'App', 'Assets.xcassets', 'AppIcon.appiconset')
    ios_splash_dir = os.path.join(mobile_dir, 'ios', 'App', 'App', 'Assets.xcassets', 'Splash.imageset')
    android_icon_dir = os.path.join(mobile_dir, 'android', 'app', 'src', 'main', 'res')
    android_splash_dir = os.path.join(mobile_dir, 'android', 'app', 'src', 'main', 'res')
    
    # Use existing bee logo or create placeholder
    if not base_icon_path:
        base_icon_path = os.path.join(base_dir, 'static', 'css', 'images', 'bee-logo.png')
    
    if not base_splash_path:
        base_splash_path = base_icon_path  # Use same image for splash
    
    # Generate iOS assets
    print("\n📱 iOS Assets")
    print("-" * 50)
    create_app_icon(base_icon_path, ios_icon_dir, platform='ios')
    create_splash_screen(base_splash_path, ios_splash_dir, platform='ios')
    
    # Generate Android assets
    print("\n🤖 Android Assets")
    print("-" * 50)
    create_app_icon(base_icon_path, android_icon_dir, platform='android')
    create_splash_screen(base_splash_path, android_splash_dir, platform='android')
    
    print("\n" + "=" * 50)
    print("✅ All assets generated successfully!")
    print("\n📝 Next steps:")
    print("1. Review generated icons and splash screens")
    print("2. Replace with custom designs if needed")
    print("3. Run: npx cap sync")
    print("4. Open in Xcode/Android Studio and build")


if __name__ == '__main__':
    import sys
    
    icon_path = sys.argv[1] if len(sys.argv) > 1 else None
    splash_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    generate_all_assets(icon_path, splash_path)
