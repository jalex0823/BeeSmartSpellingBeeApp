#!/usr/bin/env python3
"""
Update avatar_catalog.py with new marketing descriptions and fix mascot tier
"""

# New approved marketing descriptions
NEW_DESCRIPTIONS = {
    'al_bee': 'A genius bee with big ideas! Al Bee loves science, puzzles, and helping learners "bee" brilliant.',
    'brother_bee': 'Friendly, cool, and loyal — Brother Bee always cheers you on during your spelling adventure.',
    'buda_bee': 'A peaceful little bee who loves calm vibes, focus, and mindful spelling moments.',
    'builder_bee': 'Hammer in one hand, honey in the other — Builder Bee helps you construct spelling success!',
    'buzz_bee': 'Always pumped and ready to go — Buzz Bee brings energy to every spelling challenge!',
    'cool_bee': 'Shades on. Chill mode activated. Cool Bee is smooth, stylish, and full of confidence.',
    'cutie_bee': 'Adorable and sweet — Cutie Bee is guaranteed to make every game session extra fun.',
    'detective_bee': 'Always on the case! Detective Bee finds clues and helps you spell like a pro.',
    'diva_bee': 'Glamorous, glittery, and full of confidence. Diva Bee lights up any spelling stage.',
    'doc_bee': 'Dr. Bee is always here to help! Clipboard ready, cheering you on as you learn new words.',
    'explorer_bee': 'Adventurous and curious, Explorer Bee loves discovering new words with you.',
    'franken_bee': 'A silly spooky bee with a big heart — Franken Bee is always stitched together with fun!',
    'honey_comb': 'Sweet, golden, and iconic — Honey Comb Bee represents pure BeeSmart pride.',
    'j_rock_bee': "Ready to rock n' roll! Guitar in hand, J Rock Bee brings rhythm to your spelling.",
    'knight_bee': 'Brave and bold — Knight Bee protects your spelling kingdom with honor!',
    'mascot_bee': 'The official BeeSmart cheerleader! Mascot Bee hypes you up every step of the way.',
    'motor_bee': 'Fast and focused, Motor Bee zooms into action and powers up your learning.',
    'o_bee': 'A classic BeeSmart sidekick — O Bee keeps things simple, fun, and full of charm.',
    'professor_bee': 'Wise, clever, and super smart — Professor Bee helps you master even the trickiest words.',
    'queen_bee': 'Royal, radiant, and full of leadership — Queen Bee rules the spelling hive!',
    'robo_bee': 'Bzz-bzz-beep! Robo Bee is a high-tech helper built for spelling greatness.',
    'rocker_bee': 'Crank up the volume — Rocker Bee brings electric energy to every spelling match.',
    'sea_bee': 'A deep-sea explorer bee who loves ocean adventures and cool blue vibes.',
    'selfie_bee': 'Smile! Selfie Bee loves photos, fun, and capturing your spelling victories.',
    'singer_bee': 'Microphone ready — Singer Bee hits every high note as you hit every correct word!',
    'space_bee': 'Out-of-this-world awesome! Space Bee is ready for spelling missions across the galaxy.',
    'super_bee': 'Strong, bold, and heroic — Super Bee saves the day when learning gets tough!',
    'vamp_bee': 'A funny little night bee who is more cute than spooky — perfect for Halloween fun!',
    'ware_bee': 'A cyber-tech defender bee — Ware Bee protects your spelling progress with digital power.',
    'zom_bee': 'Silly, slow, and super funny — Zom Bee brings goofy undead fun to the hive.',
    'umpire_bee': '"You\'re SAFE!" Umpire Bee calls the plays and keeps every spelling game fair and fun.',
    'gamer_bee': 'Headset on and controller ready — Gamer Bee is locked in for spelling victory!',
    'techno_bee': 'Glowing neon armor and futuristic style — Techno Bee is powered by pure brain energy!',
    'inventor_bee': 'A brilliant spark-powered genius — Inventor Bee creates buzzing new ideas with electricity!',
    'nurse_bee': 'Caring, kind, and always helpful — Nurse Bee cheers you on to stay healthy and keep spelling strong!',
    'plumber_bee': 'Fixing leaks and spelling streaks! Plumber Bee is ready to unclog tricky words.',
    'lumberjack_bee': 'Strong, brave, and outdoorsy — Lumberjack Bee chops through tough spelling challenges!',
    'xray_bee': 'Glowing bones and a bright smile — X-Ray Bee lights up the night with learning power!',
    'yeti_bee': 'Chilly, fluffy, and super friendly — Yeti Bee brings cool fun to your BeeSmart adventure!',
}

def main():
    print("=" * 80)
    print("📝 UPDATING AVATAR CATALOG")
    print("=" * 80)
    print()
    
    # Read current catalog
    with open('avatar_catalog.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    updates_made = 0
    
    # Fix mascot tier first
    print("🔧 Fixing mascot_bee tier...")
    old_mascot_tier = '"tier": "mascot",'
    new_mascot_tier = '"tier": "mascot_free",'
    if old_mascot_tier in content:
        content = content.replace(old_mascot_tier, new_mascot_tier, 1)
        print("   ✅ Changed mascot tier from 'mascot' to 'mascot_free'")
        updates_made += 1
    
    print()
    print("📝 Updating descriptions...")
    print()
    
    # Update each description
    for sku, new_desc in NEW_DESCRIPTIONS.items():
        # Find the avatar entry - look for the "id": "sku" pattern
        id_pattern = f'"id": "{sku.replace("_", "-")}"'
        
        if id_pattern in content:
            # Find the start of this avatar dict
            id_pos = content.find(id_pattern)
            
            # Find the description line after the id
            desc_start = content.find('"description":', id_pos)
            if desc_start == -1:
                print(f"   ⚠️  Could not find description for {sku}")
                continue
            
            # Find the end of the description (next line with comma)
            desc_line_end = content.find(',\n', desc_start)
            if desc_line_end == -1:
                print(f"   ⚠️  Could not find end of description for {sku}")
                continue
            
            # Extract old description line
            old_desc_line = content[desc_start:desc_line_end + 1]
            
            # Create new description line
            new_desc_line = f'"description": "{new_desc}",'
            
            # Replace
            content = content.replace(old_desc_line, new_desc_line, 1)
            print(f"   ✅ Updated {sku}")
            updates_made += 1
        else:
            print(f"   ⚠️  Could not find avatar {sku}")
    
    # Write updated catalog
    with open('avatar_catalog.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 80)
    print(f"✅ CATALOG UPDATED: {updates_made} changes made")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Run validate_avatar_data.py to confirm all updates")
    print("2. Update generate_avatar_cards_simple.py app_store_data descriptions")
    print("3. Regenerate App Store cards")

if __name__ == "__main__":
    main()
