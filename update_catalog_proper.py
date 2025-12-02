#!/usr/bin/env python3
"""
Update avatar_catalog.py with new marketing descriptions and fix mascot tier
This version properly handles special characters in descriptions
"""

import re

# New approved marketing descriptions with proper Python string escaping
NEW_DESCRIPTIONS = {
    'al-bee': r'A genius bee with big ideas! Al Bee loves science, puzzles, and helping learners "bee" brilliant.',
    'brother-bee': r'Friendly, cool, and loyal — Brother Bee always cheers you on during your spelling adventure.',
    'buda-bee': r'A peaceful little bee who loves calm vibes, focus, and mindful spelling moments.',
    'builder-bee': r'Hammer in one hand, honey in the other — Builder Bee helps you construct spelling success!',
    'buzz-bee': r'Always pumped and ready to go — Buzz Bee brings energy to every spelling challenge!',
    'cool-bee': r'Shades on. Chill mode activated. Cool Bee is smooth, stylish, and full of confidence.',
    'cutie-bee': r'Adorable and sweet — Cutie Bee is guaranteed to make every game session extra fun.',
    'detective-bee': r'Always on the case! Detective Bee finds clues and helps you spell like a pro.',
    'diva-bee': r'Glamorous, glittery, and full of confidence. Diva Bee lights up any spelling stage.',
    'doc-bee': r'Dr. Bee is always here to help! Clipboard ready, cheering you on as you learn new words.',
    'explorer-bee': r'Adventurous and curious, Explorer Bee loves discovering new words with you.',
    'franken-bee': r'A silly spooky bee with a big heart — Franken Bee is always stitched together with fun!',
    'honey-comb': r'Sweet, golden, and iconic — Honey Comb Bee represents pure BeeSmart pride.',
    'j-rock-bee': r"Ready to rock n' roll! Guitar in hand, J Rock Bee brings rhythm to your spelling.",
    'knight-bee': r'Brave and bold — Knight Bee protects your spelling kingdom with honor!',
    'mascot-bee': r'The official BeeSmart cheerleader! Mascot Bee hypes you up every step of the way.',
    'motor-bee': r'Fast and focused, Motor Bee zooms into action and powers up your learning.',
    'o-bee': r'A classic BeeSmart sidekick — O Bee keeps things simple, fun, and full of charm.',
    'professor-bee': r'Wise, clever, and super smart — Professor Bee helps you master even the trickiest words.',
    'queen-bee': r'Royal, radiant, and full of leadership — Queen Bee rules the spelling hive!',
    'robo-bee': r'Bzz-bzz-beep! Robo Bee is a high-tech helper built for spelling greatness.',
    'rocker-bee': r'Crank up the volume — Rocker Bee brings electric energy to every spelling match.',
    'sea-bee': r'A deep-sea explorer bee who loves ocean adventures and cool blue vibes.',
    'selfie-bee': r'Smile! Selfie Bee loves photos, fun, and capturing your spelling victories.',
    'singer-bee': r'Microphone ready — Singer Bee hits every high note as you hit every correct word!',
    'space-bee': r'Out-of-this-world awesome! Space Bee is ready for spelling missions across the galaxy.',
    'super-bee': r'Strong, bold, and heroic — Super Bee saves the day when learning gets tough!',
    'vamp-bee': r'A funny little night bee who is more cute than spooky — perfect for Halloween fun!',
    'ware-bee': r'A cyber-tech defender bee — Ware Bee protects your spelling progress with digital power.',
    'zom-bee': r'Silly, slow, and super funny — Zom Bee brings goofy undead fun to the hive.',
    'umpire-bee': r'"You\'re SAFE!" Umpire Bee calls the plays and keeps every spelling game fair and fun.',
    'gamer-bee': r'Headset on and controller ready — Gamer Bee is locked in for spelling victory!',
    'techno-bee': r'Glowing neon armor and futuristic style — Techno Bee is powered by pure brain energy!',
    'inventor-bee': r'A brilliant spark-powered genius — Inventor Bee creates buzzing new ideas with electricity!',
    'nurse-bee': r'Caring, kind, and always helpful — Nurse Bee cheers you on to stay healthy and keep spelling strong!',
    'plumber-bee': r'Fixing leaks and spelling streaks! Plumber Bee is ready to unclog tricky words.',
    'lumberjack-bee': r'Strong, brave, and outdoorsy — Lumberjack Bee chops through tough spelling challenges!',
    'xray-bee': r'Glowing bones and a bright smile — X-Ray Bee lights up the night with learning power!',
    'yeti-bee': r'Chilly, fluffy, and super friendly — Yeti Bee brings cool fun to your BeeSmart adventure!',
}

def main():
    print("=" * 80)
    print("📝 UPDATING AVATAR CATALOG DESCRIPTIONS (PROPER ESCAPING)")
    print("=" * 80)
    print()
    
    # Read current catalog
    with open('avatar_catalog.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    updates_made = 0
    
    # Fix mascot tier first
    print("🔧 Fixing mascot_bee tier...")
    content = re.sub(
        r'("id": "mascot-bee".*?"tier": )"mascot"',
        r'\1"mascot_free"',
        content,
        flags=re.DOTALL
    )
    print("   ✅ Set mascot tier to 'mascot_free'")
    updates_made += 1
    
    print()
    print("📝 Updating descriptions...")
    print()
    
    # Update each description
    for avatar_id, new_desc in NEW_DESCRIPTIONS.items():
        # Pattern to find description line for this avatar
        # Matches: "description": "any text",
        pattern = rf'("id": "{avatar_id}".*?"description": )"[^"]*?",'
        
        # Escape the new description for JSON (only need to escape quotes and backslashes)
        escaped_desc = new_desc.replace('\\', '\\\\').replace('"', '\\"')
        
        replacement = rf'\1"{escaped_desc}",'
        
        new_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
        
        if new_content != content:
            content = new_content
            print(f"   ✅ Updated {avatar_id}")
            updates_made += 1
        else:
            print(f"   ⚠️  Could not update {avatar_id}")
    
    # Write updated catalog
    with open('avatar_catalog.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 80)
    print(f"✅ CATALOG UPDATED: {updates_made} changes made")
    print("=" * 80)

if __name__ == "__main__":
    main()
