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

# Paths
GLB_DIR = Path("/Users/jalex0823/Dropbox/GitBackUpAppFolder/static/assets/avatars/glb_files")
THUMB_DIR = GLB_DIR / "AvatarThumbnails"
OUTPUT_DIR = Path("/Users/jalex0823/Dropbox/GitBackUpAppFolder/static/assets/avatars/app_store_cards")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Card settings
CARD_SIZE = 2048
BLACK = (0, 0, 0, 255)
HONEY_GOLD = (250, 210, 90, 255)
CARD_BG = (18, 18, 24, 255)
TEXT_DARK = (15, 15, 15, 255)
GLOW_COLOR = (255, 200, 50, 120)

def get_avatar_info(glb_filename):
    """Get avatar info from catalog with App Store metadata"""
    base = os.path.splitext(glb_filename)[0]
    
    # App Store metadata mapping
    app_store_data = {
        'AlBee': {'sku': 'al_bee', 'product_id': 'beesmart.avatar.al_bee', 'tier': 'premium', 'price': '$1.99'},
        'BrotherBee': {'sku': 'brother_bee', 'product_id': 'beesmart.avatar.brother_bee', 'tier': 'default_free', 'price': '$0.00'},
        'BudaBee': {'sku': 'buda_bee', 'product_id': 'beesmart.avatar.buda_bee', 'tier': 'premium', 'price': '$0.99'},
        'BuilderBee': {'sku': 'builder_bee', 'product_id': 'beesmart.avatar.builder_bee', 'tier': 'default_free', 'price': '$0.00'},
        'BuzzBee': {'sku': 'buzz_bee', 'product_id': 'beesmart.avatar.buzz_bee', 'tier': 'earn_or_buy', 'price': '$0.99'},
        'CoolBee': {'sku': 'cool_bee', 'product_id': 'beesmart.avatar.cool_bee', 'tier': 'default_free', 'price': '$0.00'},
        'CutieBee': {'sku': 'cutie_bee', 'product_id': 'beesmart.avatar.cutie_bee', 'tier': 'earn_or_buy', 'price': '$0.99'},
        'DetectiveBee': {'sku': 'detective_bee', 'product_id': 'beesmart.avatar.detective_bee', 'tier': 'default_free', 'price': '$0.00'},
        'DivaBee': {'sku': 'diva_bee', 'product_id': 'beesmart.avatar.diva_bee', 'tier': 'premium', 'price': '$1.99'},
        'DocBee': {'sku': 'doc_bee', 'product_id': 'beesmart.avatar.doc_bee', 'tier': 'premium', 'price': '$0.99'},
        'ExplorerBee': {'sku': 'explorer_bee', 'product_id': 'beesmart.avatar.explorer_bee', 'tier': 'default_free', 'price': '$0.00'},
        'FrankenBee': {'sku': 'franken_bee', 'product_id': 'beesmart.avatar.franken_bee', 'tier': 'premium', 'price': '$0.99'},
        'HoneyCombBee': {'sku': 'honey_comb', 'product_id': 'beesmart.avatar.honey_comb', 'tier': 'premium', 'price': '$0.99'},
        'JRockBee': {'sku': 'j_rock_bee', 'product_id': 'beesmart.avatar.j_rock_bee', 'tier': 'premium', 'price': '$0.99'},
        'BeeKnight': {'sku': 'knight_bee', 'product_id': 'beesmart.avatar.knight_bee', 'tier': 'earn_or_buy', 'price': '$0.99'},
        'MascotBee': {'sku': 'mascot_bee', 'product_id': 'beesmart.avatar.mascot_bee', 'tier': 'mascot', 'price': '$0.00'},
        'MotorBee': {'sku': 'motor_bee', 'product_id': 'beesmart.avatar.motor_bee', 'tier': 'premium', 'price': '$0.99'},
        'OBee': {'sku': 'o_bee', 'product_id': 'beesmart.avatar.o_bee', 'tier': 'premium', 'price': '$0.99'},
        'ProfessorBee': {'sku': 'professor_bee', 'product_id': 'beesmart.avatar.professor_bee', 'tier': 'earn_or_buy', 'price': '$0.99'},
        'QueenBee': {'sku': 'queen_bee', 'product_id': 'beesmart.avatar.queen_bee', 'tier': 'premium', 'price': '$1.99'},
        'RoboBee': {'sku': 'robo_bee', 'product_id': 'beesmart.avatar.robo_bee', 'tier': 'premium', 'price': '$1.99'},
        'RockerBee': {'sku': 'rocker_bee', 'product_id': 'beesmart.avatar.rocker_bee', 'tier': 'earn_or_buy', 'price': '$0.99'},
        'Seabea': {'sku': 'sea_bee', 'product_id': 'beesmart.avatar.sea_bee', 'tier': 'premium', 'price': '$0.99'},
        'SelfieBee': {'sku': 'selfie_bee', 'product_id': 'beesmart.avatar.selfie_bee', 'tier': 'earn_or_buy', 'price': '$0.99'},
        'SingerBee': {'sku': 'singer_bee', 'product_id': 'beesmart.avatar.singer_bee', 'tier': 'premium', 'price': '$0.99'},
        'SpaceBee': {'sku': 'space_bee', 'product_id': 'beesmart.avatar.space_bee', 'tier': 'premium', 'price': '$0.99'},
        'SuperBee': {'sku': 'super_bee', 'product_id': 'beesmart.avatar.super_bee', 'tier': 'premium', 'price': '$0.99'},
        'VampBee': {'sku': 'vamp_bee', 'product_id': 'beesmart.avatar.vamp_bee', 'tier': 'earn_or_buy', 'price': '$0.99'},
        'WareBee': {'sku': 'ware_bee', 'product_id': 'beesmart.avatar.ware_bee', 'tier': 'premium', 'price': '$1.99'},
        'ZomBee': {'sku': 'zom_bee', 'product_id': 'beesmart.avatar.zom_bee', 'tier': 'premium', 'price': '$1.99'}
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
        'price': '$0.99'
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

def create_app_store_card(avatar_img, info, size=CARD_SIZE):
    """Create beautiful App Store card with metadata"""
    # Create base card
    card = Image.new("RGBA", (size, size), CARD_BG)
    draw = ImageDraw.Draw(card)
    
    w, h = size, size
    margin = int(w * 0.04)
    
    # Gradient background
    for y in range(h):
        alpha = int(30 + 25 * (1.0 - y / h))
        color = (CARD_BG[0] + alpha, CARD_BG[1] + alpha, CARD_BG[2] + alpha, 255)
        draw.line([(0, y), (w, y)], fill=color)
    
    # Gold border
    border_rect = [margin, margin, w - margin, h - margin]
    draw.rounded_rectangle(border_rect, radius=int(w * 0.03), outline=HONEY_GOLD, width=int(w * 0.008))
    
    # Name plate (larger to fit more info)
    plate_h = int(h * 0.22)
    plate_top = h - margin - plate_h - int(h * 0.025)
    plate_rect = [
        margin + int(w * 0.06),
        plate_top,
        w - margin - int(w * 0.06),
        h - margin - int(h * 0.025)
    ]
    draw.rounded_rectangle(plate_rect, radius=int(w * 0.02), fill=HONEY_GOLD)
    
    # Tier badge (top right corner)
    tier_colors = {
        'default_free': (100, 200, 100, 255),
        'earn_or_buy': (100, 150, 255, 255),
        'premium': (255, 200, 50, 255),
        'mascot': (255, 100, 255, 255)
    }
    tier_color = tier_colors.get(info.get('tier'), tier_colors['premium'])
    tier_size = int(w * 0.12)
    tier_pos = (w - margin - tier_size - int(w * 0.02), margin + int(w * 0.02))
    draw.ellipse([tier_pos[0], tier_pos[1], tier_pos[0] + tier_size, tier_pos[1] + tier_size], fill=tier_color)
    
    # Price badge (top left corner)
    price_size = int(w * 0.12)
    price_pos = (margin + int(w * 0.02), margin + int(w * 0.02))
    price_color = (50, 200, 50, 255) if info.get('price') == '$0.00' else (255, 150, 50, 255)
    draw.ellipse([price_pos[0], price_pos[1], price_pos[0] + price_size, price_pos[1] + price_size], fill=price_color)
    
    # Avatar area (adjusted for larger name plate)
    avatar_top = margin + int(h * 0.08)
    avatar_bottom = plate_top - int(h * 0.04)
    avatar_w = int((w - 2 * margin) * 0.75)
    avatar_h = avatar_bottom - avatar_top
    
    # Resize and center avatar
    aspect = avatar_img.width / avatar_img.height
    if aspect > 1:
        new_w = avatar_w
        new_h = int(avatar_w / aspect)
    else:
        new_h = avatar_h
        new_w = int(avatar_h * aspect)
    
    # Make sure it fits
    if new_w > avatar_w:
        new_w = avatar_w
        new_h = int(avatar_w / aspect)
    if new_h > avatar_h:
        new_h = avatar_h
        new_w = int(avatar_h * aspect)
    
    avatar_resized = avatar_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Add subtle glow effect
    glow = Image.new("RGBA", (new_w + 40, new_h + 40), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([0, 0, new_w + 40, new_h + 40], fill=GLOW_COLOR)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=20))
    
    # Position avatar
    avatar_x = (w - new_w) // 2
    avatar_y = avatar_top + (avatar_h - new_h) // 2
    glow_x = avatar_x - 20
    glow_y = avatar_y - 20
    
    card.paste(glow, (glow_x, glow_y), glow)
    card.paste(avatar_resized, (avatar_x, avatar_y), avatar_resized)
    
    # Text on name plate
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(w * 0.055))
        info_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(w * 0.035))
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(w * 0.025))
    except:
        title_font = ImageFont.load_default()
        info_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw text info on name plate
    text_x = plate_rect[0] + int(w * 0.03)
    text_y = plate_rect[1] + int(h * 0.015)
    
    # Avatar name
    draw.text((text_x, text_y), info.get('name', 'Unknown'), fill=TEXT_DARK, font=title_font)
    text_y += int(h * 0.045)
    
    # SKU
    sku_text = f"SKU: {info.get('sku', 'unknown')}"
    draw.text((text_x, text_y), sku_text, fill=TEXT_DARK, font=info_font)
    text_y += int(h * 0.035)
    
    # Product ID
    product_text = f"ID: {info.get('product_id', 'beesmart.avatar.unknown')}"
    draw.text((text_x, text_y), product_text, fill=TEXT_DARK, font=small_font)
    text_y += int(h * 0.03)
    
    # Tier
    tier_text = f"Tier: {info.get('tier', 'premium').replace('_', ' ').title()}"
    draw.text((text_x, text_y), tier_text, fill=TEXT_DARK, font=small_font)
    text_y += int(h * 0.03)
    
    # Price (last line, left-justified)
    price_text = f"Price: {info.get('price', '$0.99')}"
    draw.text((text_x, text_y), price_text, fill=TEXT_DARK, font=info_font)
    
    # Add price to price badge
    try:
        badge_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(w * 0.02))
    except:
        badge_font = ImageFont.load_default()
    
    price_display = info.get('price', '$0.99').replace('$0.00', 'FREE')
    price_bbox = draw.textbbox((0, 0), price_display, font=badge_font)
    price_text_w = price_bbox[2] - price_bbox[0]
    price_text_h = price_bbox[3] - price_bbox[1]
    price_text_x = price_pos[0] + (price_size - price_text_w) // 2
    price_text_y = price_pos[1] + (price_size - price_text_h) // 2
    draw.text((price_text_x, price_text_y), price_display, fill=(255, 255, 255, 255), font=badge_font)
    
    return card

def main():
    print("=" * 70)
    print("🎨 APP STORE AVATAR CARD GENERATOR (Simple Version)")
    print("=" * 70)
    print(f"\n📂 Thumbnails: {THUMB_DIR}")
    print(f"📂 Output:     {OUTPUT_DIR}")
    print(f"📐 Size:       {CARD_SIZE}x{CARD_SIZE}px\n")
    
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
