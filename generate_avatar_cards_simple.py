#!/usr/bin/env python3
"""
Simple Avatar Card Generator - Uses existing thumbnails
Creates App Store-ready cards from existing avatar thumbnails
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
CARD_BG = (70, 70, 72, 255)  # Dark gray background from sample
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
    """Create Apple App Store IAP screenshot (768x768)"""
    # Create base card
    card = Image.new("RGBA", (width, height), CARD_BG)
    draw = ImageDraw.Draw(card)
    
    w, h = width, height
    margin = 30  # Fixed margin from sample
    border_width = 6  # Border width from sample
    corner_radius = 30  # Rounded corner radius from sample
    
    # Gold border with rounded corners
    border_rect = [margin, margin, w - margin, h - margin]
    draw.rounded_rectangle(border_rect, radius=corner_radius, outline=HONEY_GOLD, width=border_width)
    
    # Name plate at bottom (yellow background)
    plate_h = 160  # Height from sample card
    plate_top = h - margin - plate_h - 30  # Position from sample
    plate_rect = [
        margin + 45,  # Inner margin
        plate_top,
        w - margin - 45,
        h - margin - 30
    ]
    draw.rounded_rectangle(plate_rect, radius=15, fill=HONEY_GOLD)
    
    # NOTE: Apple 2.3.2 compliance — do NOT render any price text/symbols on promotional images.
    # Keep the design clean by omitting the price badge entirely.
    
    # Tier badge (top right corner - yellow circle)
    tier_size = 90  # Circle diameter from sample
    tier_pos = (w - margin - tier_size - 20, margin + 20)
    tier_colors = {
        'default_free': (100, 200, 100, 255),
        'earn_or_buy': (100, 150, 255, 255),
        'premium': (250, 210, 90, 255),  # HONEY_GOLD
        'mascot': (255, 100, 255, 255)
    }
    tier_color = tier_colors.get(info.get('tier'), tier_colors['premium'])
    draw.ellipse([tier_pos[0], tier_pos[1], tier_pos[0] + tier_size, tier_pos[1] + tier_size], 
                 fill=tier_color)
    
    # Avatar area (centered between badges and name plate)
    avatar_top = margin + 120  # Start below badges
    avatar_bottom = plate_top - 30  # End above name plate
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
    
    # Text on name plate - smaller fonts to fit everything
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)  # Title size
        info_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)   # Info size
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)  # Small size
        price_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)  # Price badge
    except:
        title_font = ImageFont.load_default()
        info_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        price_font = ImageFont.load_default()
    
    # Draw text info on name plate - tighter spacing
    text_x = plate_rect[0] + 20  # Left padding
    text_y = plate_rect[1] + 12  # Top padding
    
    # Avatar name (line 1)
    draw.text((text_x, text_y), info.get('name', 'Unknown'), fill=TEXT_DARK, font=title_font)
    text_y += 35  # Line spacing
    
    # SKU (line 2)
    sku_text = f"SKU: {info.get('sku', 'unknown')}"
    draw.text((text_x, text_y), sku_text, fill=TEXT_DARK, font=small_font)
    text_y += 23  # Line spacing
    
    # Product ID (line 3)
    product_text = f"ID: {info.get('product_id', 'beesmart.avatar.unknown')}"
    draw.text((text_x, text_y), product_text, fill=TEXT_DARK, font=small_font)
    text_y += 23  # Line spacing
    
    # Tier (line 4)
    tier_text = f"Tier: {info.get('tier', 'premium').replace('_', ' ').title()}"
    draw.text((text_x, text_y), tier_text, fill=TEXT_DARK, font=small_font)
    text_y += 23  # Line spacing
    
    # No price text on the card.
    
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
