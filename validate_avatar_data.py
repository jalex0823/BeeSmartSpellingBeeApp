#!/usr/bin/env python3
"""
Validate avatar catalog data against provided specifications
"""

from avatar_catalog import AVATAR_CATALOG

# Expected data from user's spreadsheet
expected_data = {
    'al_bee': {'tier': 'premium', 'price': 1.99, 'description': 'A genius bee with big ideas! Al Bee loves science, puzzles, and helping learners "bee" brilliant.'},
    'brother_bee': {'tier': 'default_free', 'price': 0.00, 'description': 'Friendly, cool, and loyal — Brother Bee always cheers you on during your spelling adventure.'},
    'buda_bee': {'tier': 'premium', 'price': 0.99, 'description': 'A peaceful little bee who loves calm vibes, focus, and mindful spelling moments.'},
    'builder_bee': {'tier': 'default_free', 'price': 0.00, 'description': 'Hammer in one hand, honey in the other — Builder Bee helps you construct spelling success!'},
    'buzz_bee': {'tier': 'earn_or_buy', 'price': 0.99, 'description': 'Always pumped and ready to go — Buzz Bee brings energy to every spelling challenge!'},
    'cool_bee': {'tier': 'default_free', 'price': 0.00, 'description': 'Shades on. Chill mode activated. Cool Bee is smooth, stylish, and full of confidence.'},
    'cutie_bee': {'tier': 'earn_or_buy', 'price': 0.99, 'description': 'Adorable and sweet — Cutie Bee is guaranteed to make every game session extra fun.'},
    'detective_bee': {'tier': 'default_free', 'price': 0.00, 'description': 'Always on the case! Detective Bee finds clues and helps you spell like a pro.'},
    'diva_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Glamorous, glittery, and full of confidence. Diva Bee lights up any spelling stage.'},
    'doc_bee': {'tier': 'premium', 'price': 0.99, 'description': 'Dr. Bee is always here to help! Clipboard ready, cheering you on as you learn new words.'},
    'explorer_bee': {'tier': 'default_free', 'price': 0.00, 'description': 'Adventurous and curious, Explorer Bee loves discovering new words with you.'},
    'franken_bee': {'tier': 'premium', 'price': 0.99, 'description': 'A silly spooky bee with a big heart — Franken Bee is always stitched together with fun!'},
    'honey_comb': {'tier': 'premium', 'price': 0.99, 'description': 'Sweet, golden, and iconic — Honey Comb Bee represents pure BeeSmart pride.'},
    'j_rock_bee': {'tier': 'premium', 'price': 0.99, 'description': "Ready to rock n' roll! Guitar in hand, J Rock Bee brings rhythm to your spelling."},
    'knight_bee': {'tier': 'earn_or_buy', 'price': 0.99, 'description': 'Brave and bold — Knight Bee protects your spelling kingdom with honor!'},
    'mascot_bee': {'tier': 'mascot_free', 'price': 0.00, 'description': 'The official BeeSmart cheerleader! Mascot Bee hypes you up every step of the way.'},
    'motor_bee': {'tier': 'premium', 'price': 0.99, 'description': 'Fast and focused, Motor Bee zooms into action and powers up your learning.'},
    'o_bee': {'tier': 'premium', 'price': 0.99, 'description': 'A classic BeeSmart sidekick — O Bee keeps things simple, fun, and full of charm.'},
    'professor_bee': {'tier': 'earn_or_buy', 'price': 0.99, 'description': 'Wise, clever, and super smart — Professor Bee helps you master even the trickiest words.'},
    'queen_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Royal, radiant, and full of leadership — Queen Bee rules the spelling hive!'},
    'robo_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Bzz-bzz-beep! Robo Bee is a high-tech helper built for spelling greatness.'},
    'rocker_bee': {'tier': 'earn_or_buy', 'price': 0.99, 'description': 'Crank up the volume — Rocker Bee brings electric energy to every spelling match.'},
    'sea_bee': {'tier': 'premium', 'price': 0.99, 'description': 'A deep-sea explorer bee who loves ocean adventures and cool blue vibes.'},
    'selfie_bee': {'tier': 'earn_or_buy', 'price': 0.99, 'description': 'Smile! Selfie Bee loves photos, fun, and capturing your spelling victories.'},
    'singer_bee': {'tier': 'premium', 'price': 0.99, 'description': 'Microphone ready — Singer Bee hits every high note as you hit every correct word!'},
    'space_bee': {'tier': 'premium', 'price': 0.99, 'description': 'Out-of-this-world awesome! Space Bee is ready for spelling missions across the galaxy.'},
    'super_bee': {'tier': 'premium', 'price': 0.99, 'description': 'Strong, bold, and heroic — Super Bee saves the day when learning gets tough!'},
    'vamp_bee': {'tier': 'earn_or_buy', 'price': 0.99, 'description': 'A funny little night bee who is more cute than spooky — perfect for Halloween fun!'},
    'ware_bee': {'tier': 'premium', 'price': 1.99, 'description': 'A cyber-tech defender bee — Ware Bee protects your spelling progress with digital power.'},
    'zom_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Silly, slow, and super funny — Zom Bee brings goofy undead fun to the hive.'},
    'umpire_bee': {'tier': 'premium', 'price': 1.99, 'description': '"You\'re SAFE!" Umpire Bee calls the plays and keeps every spelling game fair and fun.'},
    'gamer_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Headset on and controller ready — Gamer Bee is locked in for spelling victory!'},
    'techno_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Glowing neon armor and futuristic style — Techno Bee is powered by pure brain energy!'},
    'inventor_bee': {'tier': 'premium', 'price': 1.99, 'description': 'A brilliant spark-powered genius — Inventor Bee creates buzzing new ideas with electricity!'},
    'nurse_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Caring, kind, and always helpful — Nurse Bee cheers you on to stay healthy and keep spelling strong!'},
    'plumber_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Fixing leaks and spelling streaks! Plumber Bee is ready to unclog tricky words.'},
    'lumberjack_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Strong, brave, and outdoorsy — Lumberjack Bee chops through tough spelling challenges!'},
    'xray_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Glowing bones and a bright smile — X-Ray Bee lights up the night with learning power!'},
    'yeti_bee': {'tier': 'premium', 'price': 1.99, 'description': 'Chilly, fluffy, and super friendly — Yeti Bee brings cool fun to your BeeSmart adventure!'},
}

def main():
    print("=" * 80)
    print("🔍 AVATAR CATALOG VALIDATION")
    print("=" * 80)
    print()
    
    issues = []
    matches = []
    
    # Build SKU lookup from catalog
    catalog_by_sku = {}
    for avatar in AVATAR_CATALOG:
        product_id = avatar.get('product_id', '')
        sku = product_id.replace('beesmart.avatar.', '')
        catalog_by_sku[sku] = avatar
    
    print(f"📊 Catalog avatars: {len(AVATAR_CATALOG)}")
    print(f"📊 Expected avatars: {len(expected_data)}")
    print()
    
    # Check each expected avatar
    for sku, expected in expected_data.items():
        if sku not in catalog_by_sku:
            issues.append(f"❌ {sku}: NOT FOUND in catalog")
            continue
        
        catalog_avatar = catalog_by_sku[sku]
        catalog_tier = catalog_avatar.get('tier')
        catalog_price = catalog_avatar.get('price')
        catalog_desc = catalog_avatar.get('description')
        
        mismatches = []
        
        # Check tier
        if catalog_tier != expected['tier']:
            mismatches.append(f"  TIER: catalog='{catalog_tier}' vs expected='{expected['tier']}'")
        
        # Check price
        if catalog_price != expected['price']:
            mismatches.append(f"  PRICE: catalog={catalog_price} vs expected={expected['price']}")
        
        # Check description
        if catalog_desc != expected['description']:
            mismatches.append(f"  DESCRIPTION: Different")
            mismatches.append(f"    Catalog:  {catalog_desc}")
            mismatches.append(f"    Expected: {expected['description']}")
        
        if mismatches:
            issues.append(f"⚠️  {sku}:")
            issues.extend(mismatches)
        else:
            matches.append(f"✅ {sku}")
    
    print("MATCHES:")
    print("=" * 80)
    for match in matches:
        print(match)
    
    if issues:
        print()
        print("ISSUES FOUND:")
        print("=" * 80)
        for issue in issues:
            print(issue)
        print()
        print(f"❌ Total issues: {len([i for i in issues if i.startswith('❌') or i.startswith('⚠️')])}")
    else:
        print()
        print("=" * 80)
        print("🎉 ALL DATA VALIDATED SUCCESSFULLY!")
        print("=" * 80)
    
    print()
    print(f"✅ Matches: {len(matches)}")
    print(f"⚠️  Issues:  {len([i for i in issues if i.startswith('❌') or i.startswith('⚠️')])}")

if __name__ == "__main__":
    main()
