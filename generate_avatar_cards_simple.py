#!/usr/bin/env python3
"""
Simple Avatar Card Generator - Uses existing thumbnails
Creates App Store-ready cards from existing avatar thumbnails
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a reasonably standard TrueType font across platforms.

    Apple promo assets are reviewed for legibility; Pillow's default bitmap font
    can render too small. We try common system fonts first and then fall back.
    """
    candidates: list[str] = []

    # Windows
    windir = os.environ.get("WINDIR")
    if windir:
        candidates.extend(
            [
                str(Path(windir) / "Fonts" / "segoeui.ttf"),
                str(Path(windir) / "Fonts" / "arial.ttf"),
            ]
        )

    # macOS
    candidates.extend(
        [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    )

    # Linux (common)
    candidates.extend(
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    )

    # Pillow often ships DejaVuSans.ttf as a known font name.
    candidates.append("DejaVuSans.ttf")

    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue

    # Final fallback: bitmap font (may be small). Keep generator functional.
    return ImageFont.load_default()

# Import avatar catalog for proper names
try:
    from avatar_catalog import AVATAR_CATALOG
    print(f"✅ Loaded avatar catalog ({len(AVATAR_CATALOG)} avatars)")
except ImportError:
    print("⚠️  Could not load avatar_catalog.py")
    AVATAR_CATALOG = []

# Paths (default to this repo's checked-in assets)
REPO_ROOT = Path(__file__).resolve().parent
AVATARS_DIR = REPO_ROOT / "static" / "assets" / "avatars"
GLB_DIR = AVATARS_DIR / "glb_files"
THUMB_DIR = GLB_DIR / "AvatarThumbnails"
OUTPUT_DIR = AVATARS_DIR / "app_store_cards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Card settings - Apple App Store IAP screenshot format
# Apple requirement: 1024 x 1024 pixels
CARD_WIDTH = 1024
CARD_HEIGHT = 1024
BLACK = (0, 0, 0, 255)
HONEY_GOLD = (250, 210, 90, 255)
TRANSPARENT_BG = True
CARD_BG = (0, 0, 0, 0) if TRANSPARENT_BG else (70, 70, 72, 255)
TEXT_DARK = (15, 15, 15, 255)
GLOW_COLOR = (255, 200, 50, 120)

def get_avatar_info(glb_filename):
    """Get avatar info from catalog with App Store metadata"""
    base = os.path.splitext(glb_filename)[0]
    
    # App Store metadata mapping
    # NOTE: Do not include price strings here; promotional imagery/metadata should not embed pricing.
    app_store_data = {
        'AlBee': {'sku': 'al_bee', 'product_id': 'beesmart.avatar.al_bee', 'tier': 'premium'},
        'BrotherBee': {'sku': 'brother_bee', 'product_id': 'beesmart.avatar.brother_bee', 'tier': 'default_free'},
        'BudaBee': {'sku': 'buda_bee', 'product_id': 'beesmart.avatar.buda_bee', 'tier': 'premium'},
        'BuilderBee': {'sku': 'builder_bee', 'product_id': 'beesmart.avatar.builder_bee', 'tier': 'default_free'},
        'BuzzBee': {'sku': 'buzz_bee', 'product_id': 'beesmart.avatar.buzz_bee', 'tier': 'earn_or_buy'},
        'CoolBee': {'sku': 'cool_bee', 'product_id': 'beesmart.avatar.cool_bee', 'tier': 'default_free'},
        'CutieBee': {'sku': 'cutie_bee', 'product_id': 'beesmart.avatar.cutie_bee', 'tier': 'earn_or_buy'},
        'DetectiveBee': {'sku': 'detective_bee', 'product_id': 'beesmart.avatar.detective_bee', 'tier': 'default_free'},
        'DivaBee': {'sku': 'diva_bee', 'product_id': 'beesmart.avatar.diva_bee', 'tier': 'premium'},
        'DocBee': {'sku': 'doc_bee', 'product_id': 'beesmart.avatar.doc_bee', 'tier': 'premium'},
        'ExplorerBee': {'sku': 'explorer_bee', 'product_id': 'beesmart.avatar.explorer_bee', 'tier': 'default_free'},
        'FrankenBee': {'sku': 'franken_bee', 'product_id': 'beesmart.avatar.franken_bee', 'tier': 'premium'},
        'GamerBee': {'sku': 'gamer_bee', 'product_id': 'beesmart.avatar.gamer_bee', 'tier': 'premium'},
        'HoneyCombBee': {'sku': 'honey_comb', 'product_id': 'beesmart.avatar.honey_comb', 'tier': 'premium'},
        'InventorBee': {'sku': 'inventor_bee', 'product_id': 'beesmart.avatar.inventor_bee', 'tier': 'premium'},
        'JRockBee': {'sku': 'j_rock_bee', 'product_id': 'beesmart.avatar.j_rock_bee', 'tier': 'premium'},
        'BeeKnight': {'sku': 'knight_bee', 'product_id': 'beesmart.avatar.knight_bee', 'tier': 'earn_or_buy'},
        'LumberjackBee': {'sku': 'lumberjack_bee', 'product_id': 'beesmart.avatar.lumberjack_bee', 'tier': 'premium'},
        'MascotBee': {'sku': 'mascot_bee', 'product_id': 'beesmart.avatar.mascot_bee', 'tier': 'mascot'},
        'MotorBee': {'sku': 'motor_bee', 'product_id': 'beesmart.avatar.motor_bee', 'tier': 'premium'},
        'NurseBee': {'sku': 'nurse_bee', 'product_id': 'beesmart.avatar.nurse_bee', 'tier': 'premium'},
        'OBee': {'sku': 'o_bee', 'product_id': 'beesmart.avatar.o_bee', 'tier': 'premium'},
        'PlumberBee': {'sku': 'plumber_bee', 'product_id': 'beesmart.avatar.plumber_bee', 'tier': 'premium'},
        'ProfessorBee': {'sku': 'professor_bee', 'product_id': 'beesmart.avatar.professor_bee', 'tier': 'earn_or_buy'},
        'QueenBee': {'sku': 'queen_bee', 'product_id': 'beesmart.avatar.queen_bee', 'tier': 'premium'},
        'RoboBee': {'sku': 'robo_bee', 'product_id': 'beesmart.avatar.robo_bee', 'tier': 'premium'},
        'RockerBee': {'sku': 'rocker_bee', 'product_id': 'beesmart.avatar.rocker_bee', 'tier': 'earn_or_buy'},
        'Seabea': {'sku': 'sea_bee', 'product_id': 'beesmart.avatar.sea_bee', 'tier': 'premium'},
        'SelfieBee': {'sku': 'selfie_bee', 'product_id': 'beesmart.avatar.selfie_bee', 'tier': 'earn_or_buy'},
        'SingerBee': {'sku': 'singer_bee', 'product_id': 'beesmart.avatar.singer_bee', 'tier': 'premium'},
        'SpaceBee': {'sku': 'space_bee', 'product_id': 'beesmart.avatar.space_bee', 'tier': 'premium'},
        'SuperBee': {'sku': 'super_bee', 'product_id': 'beesmart.avatar.super_bee', 'tier': 'premium'},
        'TechnoBee': {'sku': 'techno_bee', 'product_id': 'beesmart.avatar.techno_bee', 'tier': 'premium'},
        'UmpireBee': {'sku': 'umpire_bee', 'product_id': 'beesmart.avatar.umpire_bee', 'tier': 'premium'},
        'VampBee': {'sku': 'vamp_bee', 'product_id': 'beesmart.avatar.vamp_bee', 'tier': 'earn_or_buy'},
        'WareBee': {'sku': 'ware_bee', 'product_id': 'beesmart.avatar.ware_bee', 'tier': 'premium'},
        'XrayBee': {'sku': 'xray_bee', 'product_id': 'beesmart.avatar.xray_bee', 'tier': 'premium'},
        'YetiBee': {'sku': 'yeti_bee', 'product_id': 'beesmart.avatar.yeti_bee', 'tier': 'premium'},
        'ZomBee': {'sku': 'zom_bee', 'product_id': 'beesmart.avatar.zom_bee', 'tier': 'premium'}
    }
    
    # Get catalog info
    for avatar in AVATAR_CATALOG:
        obj_file = avatar.get('obj_file', '')
        if obj_file and base in obj_file:
            catalog_info = {
                'name': avatar.get('name', base),
                'description': avatar.get('description', '')
            }
            break
    else:
        catalog_info = {
            'name': base.replace('_', ' ').title() + ' Avatar',
            'description': ''
        }
    
    # Get App Store data
    store_data = app_store_data.get(base, {
        'sku': base.lower(),
        'product_id': f'beesmart.avatar.{base.lower()}',
        'tier': 'premium',
    })
    
    return {**catalog_info, **store_data}

def find_thumbnail(base_name):
    """Find thumbnail for avatar"""
    # Known naming variations
    name_map = {
        'BuzzbotBee': 'RoboBee',
        'DoctorBee': 'DocBee',
        'KnightBee': 'BeeKnight',
    }
    
    # Check if there's a known variation
    mapped_name = name_map.get(base_name, base_name)
    
    # Try exact match with mapped name
    exact = THUMB_DIR / f"{mapped_name}!.png"
    if exact.exists():
        return exact
    
    # Try exact match with original name
    exact = THUMB_DIR / f"{base_name}!.png"
    if exact.exists():
        return exact
    
    # Try case variations
    for file in THUMB_DIR.iterdir():
        if file.name.lower() == f"{base_name.lower()}!.png":
            return file
        if file.name.lower() == f"{mapped_name.lower()}!.png":
            return file
    
    return None

def create_app_store_card(avatar_img, info, width=CARD_WIDTH, height=CARD_HEIGHT):
    """Create Apple App Store promoted IAP promo image (1024x1024).

    Notes (based on App Store Connect guidance):
    - Avoid overlaying text on the image.
    - Avoid putting important details in the lower-left (App Store may overlay your app icon).
    - Do not include price/currency strings.
    """
    # Create base card (transparent PNG recommended for clean promoted IAP imagery)
    card = Image.new("RGBA", (width, height), CARD_BG)
    draw = ImageDraw.Draw(card)
    
    w, h = width, height
    margin = 40

    # Keep the design clean: no text overlays, no price badges.
    # Also keep key artwork away from the lower-left where App Store UI may overlay the app icon.
    
    # Safe area for artwork.
    # - Leave room around the edges for Apple's framing system.
    # - Leave extra room in the lower-left for the app icon overlay.
    avatar_top = margin + 60
    avatar_bottom = h - margin - 180
    avatar_area_h = avatar_bottom - avatar_top
    avatar_max_w = w - 2 * margin - 100  # Max width
    
    # Resize avatar proportionally to fit
    avatar_target_h = int(avatar_area_h * 0.85)  # 85% of available height
    aspect = avatar_img.width / avatar_img.height
    new_h = avatar_target_h
    new_w = int(avatar_target_h * aspect)
    
    # Make sure width doesn't exceed limits
    if new_w > avatar_max_w:
        new_w = avatar_max_w
        new_h = int(avatar_max_w / aspect)
    
    avatar_resized = avatar_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Center avatar in available space
    avatar_x = (w - new_w) // 2
    avatar_y = avatar_top + (avatar_area_h - new_h) // 2
    
    # Paste avatar
    card.paste(avatar_resized, (avatar_x, avatar_y), avatar_resized)
    
    # No text overlay on the image. Use App Store Connect metadata for display name/description.
    
    return card

def main():
    print("=" * 70)
    print("🎨 APP STORE AVATAR CARD GENERATOR (Apple IAP Format)")
    print("=" * 70)
    print(f"\n📂 Thumbnails: {THUMB_DIR}")
    print(f"📂 Output:     {OUTPUT_DIR}")
    print(f"📐 Size:       {CARD_WIDTH}x{CARD_HEIGHT}px (Apple IAP screenshot requirement)\n")
    
    glb_files = sorted([p for p in GLB_DIR.iterdir() if p.suffix.lower() == ".glb"])
    
    if not glb_files:
        print(f"❌ No .glb files found")
        return
    
    print(f"✅ Found {len(glb_files)} GLB files\n")
    
    success = 0
    skipped = 0
    
    for i, glb_path in enumerate(glb_files, 1):
        base_name = glb_path.stem
        info = get_avatar_info(glb_path.name)
        
        print(f"[{i}/{len(glb_files)}] {glb_path.name}")
        print(f"      → {info['name']} ({info['tier']})")
        
        # Find thumbnail
        thumb_path = find_thumbnail(base_name)
        
        if not thumb_path:
            print(f"      ⚠️  No thumbnail found, skipping")
            skipped += 1
            print()
            continue
        
        try:
            # Load thumbnail
            avatar_img = Image.open(thumb_path).convert("RGBA")
            
            # Create card with full info
            card = create_app_store_card(avatar_img, info)
            
            # Save
            out_path = OUTPUT_DIR / f"{base_name.lower()}.png"
            card.save(out_path, format="PNG", optimize=True)
            print(f"      ✅ Saved: {out_path.name}")
            success += 1
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 70)
    print(f"✅ Success: {success}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"📁 Output:  {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
