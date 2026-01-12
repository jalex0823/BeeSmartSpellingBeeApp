"""
Generate Android splash screen images with BeeSmart branding
Replaces any Flutter logos with BeeSmart logo for consistency
"""

import os
import sys
from PIL import Image

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def create_android_splash_screens():
    """Generate Android splash screens with BeeSmart logo"""
    print("Generating Android splash screens with BeeSmart branding...")
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, 'static', 'BeeSmartCrestLogo1.png')
    android_res_dir = os.path.join(base_dir, 'mobile', 'android', 'app', 'src', 'main', 'res')
    
    # Check if logo exists
    if not os.path.exists(logo_path):
        print(f"[ERROR] Logo not found: {logo_path}")
        print("Trying alternative logo paths...")
        alt_paths = [
            os.path.join(base_dir, 'BeeSmartCrestLogo1.png'),
            os.path.join(base_dir, 'BeeSmartAppIcon.png'),
            os.path.join(base_dir, 'static', 'BeeSmartLogo.png'),
        ]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                logo_path = alt_path
                print(f"[OK] Using logo: {logo_path}")
                break
        else:
            print("[ERROR] No logo found. Please ensure BeeSmartCrestLogo1.png exists.")
            return False
    
    # Load logo
    try:
        logo = Image.open(logo_path).convert('RGBA')
        print(f"[OK] Loaded logo: {logo_path} ({logo.width}x{logo.height})")
    except Exception as e:
        print(f"[ERROR] Error loading logo: {e}")
        return False
    
    # Android splash screen sizes (portrait and landscape)
    splash_sizes = {
        # Portrait
        'drawable-port-mdpi/splash.png': (320, 480),
        'drawable-port-hdpi/splash.png': (480, 800),
        'drawable-port-xhdpi/splash.png': (720, 1280),
        'drawable-port-xxhdpi/splash.png': (960, 1600),
        'drawable-port-xxxhdpi/splash.png': (1280, 1920),
        # Landscape
        'drawable-land-mdpi/splash.png': (480, 320),
        'drawable-land-hdpi/splash.png': (800, 480),
        'drawable-land-xhdpi/splash.png': (1280, 720),
        'drawable-land-xxhdpi/splash.png': (1600, 960),
        'drawable-land-xxxhdpi/splash.png': (1920, 1280),
        # Default
        'drawable/splash.png': (720, 1280),
    }
    
    gold_color = (255, 215, 0)  # #FFD700 - BeeSmart gold
    
    for relative_path, size in splash_sizes.items():
        # Create splash screen with gold background
        splash = Image.new('RGB', size, gold_color)
        
        # Calculate logo scaling (60% of smaller dimension, maintaining aspect ratio)
        max_logo_size = int(min(size) * 0.6)
        logo_aspect = logo.width / logo.height
        
        if logo.width > logo.height:
            new_width = max_logo_size
            new_height = int(max_logo_size / logo_aspect)
        else:
            new_height = max_logo_size
            new_width = int(max_logo_size * logo_aspect)
        
        # Resize logo
        resized_logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center logo on splash screen
        x = (size[0] - new_width) // 2
        y = (size[1] - new_height) // 2
        
        # Paste logo onto splash (handle transparency)
        if resized_logo.mode == 'RGBA':
            # Create a temporary RGB image for pasting
            logo_rgb = Image.new('RGB', resized_logo.size, gold_color)
            logo_rgb.paste(resized_logo, (0, 0), resized_logo)
            splash.paste(logo_rgb, (x, y))
        else:
            splash.paste(resized_logo, (x, y))
        
        # Save splash screen
        filepath = os.path.join(android_res_dir, relative_path)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        splash.save(filepath, 'PNG', optimize=True)
        print(f"  [OK] Generated: {relative_path} ({size[0]}x{size[1]})")
    
    print(f"\n[SUCCESS] Successfully generated {len(splash_sizes)} Android splash screen images!")
    print(f"Location: {android_res_dir}")
    print("\nNext steps:")
    print("1. Verify the splash screens look correct")
    print("2. Run: npx cap sync (if using Capacitor)")
    print("3. Rebuild the Android app")
    print("4. Test the splash screen appears correctly")
    
    return True

if __name__ == '__main__':
    create_android_splash_screens()
