#!/usr/bin/env python3
"""
Rebuild avatar_catalog.py with exactly 31 avatars from the user's image.
Removes: biker-bee, doctor-bee, franken-bee, seabea, superbee
Adds: buzzbot-bee, buzzhero-bee, doc-bee, honey-comb, j-rock-bee, sea-bee
"""

# Read the current catalog
with open('avatar_catalog.py', 'r') as f:
    content = f.read()

# Define the 31 avatars from the image with their tiers
avatars_from_image = {
    # Row 1
    "al-bee": {"name": "Al Bee Avatar", "tier": "premium", "unlock": 20000, "price": 0.99},
    "brother-bee": {"name": "Brother Bee Avatar", "tier": "default_free", "unlock": 0, "price": 0.00},
    "buda-bee": {"name": "Buda Bee Avatar", "tier": "premium", "unlock": 15000, "price": 0.99},
    "builder-bee": {"name": "Builder Bee Avatar", "tier": "default_free", "unlock": 0, "price": 0.00},
    "buzz-bee": {"name": "Buzz Bee Avatar", "tier": "earn_or_buy", "unlock": 3000, "price": 0.99},
    "buzzbot-bee": {"name": "Buzzbot Bee Avatar", "tier": "premium", "unlock": 18000, "price": 0.99},
    
    # Row 2
    "buzzhero-bee": {"name": "Buzzhero Bee Avatar", "tier": "premium", "unlock": 18000, "price": 0.99},
    "cool-bee": {"name": "Cool Bee Avatar", "tier": "default_free", "unlock": 0, "price": 0.00},
    "cutie-bee": {"name": "Cutie Bee Avatar", "tier": "premium", "unlock": 15000, "price": 0.99},
    "detective-bee": {"name": "Detective Bee Avatar", "tier": "earn_or_buy", "unlock": 5000, "price": 0.99},
    "diva-bee": {"name": "Diva Bee Avatar", "tier": "premium", "unlock": 18000, "price": 0.99},
    "doc-bee": {"name": "Doc Bee Avatar", "tier": "premium", "unlock": 18000, "price": 0.99},
    
    # Row 3
    "explorer-bee": {"name": "Explorer Bee Avatar", "tier": "earn_or_buy", "unlock": 5000, "price": 0.99},
    "honey-comb": {"name": "Honey Comb Avatar", "tier": "premium", "unlock": 18000, "price": 0.99},
    "j-rock-bee": {"name": "J Rock Bee Avatar", "tier": "premium", "unlock": 18000, "price": 0.99},
    "knight-bee": {"name": "Knight Bee Avatar", "tier": "premium", "unlock": 15000, "price": 0.99},
    "mascot-bee": {"name": "Mascot Bee Avatar", "tier": "mascot", "unlock": 0, "price": 0.00},
    "motor-bee": {"name": "Motor Bee Avatar", "tier": "earn_or_buy", "unlock": 5000, "price": 0.99},
    
    # Row 4
    "o-bee": {"name": "O Bee Avatar", "tier": "premium", "unlock": 20000, "price": 0.99},
    "professor-bee": {"name": "Professor Bee Avatar", "tier": "premium", "unlock": 15000, "price": 0.99},
    "queen-bee": {"name": "Queen Bee Avatar", "tier": "premium", "unlock": 20000, "price": 0.99},
    "rocker-bee": {"name": "Rocker Bee Avatar", "tier": "premium", "unlock": 15000, "price": 0.99},
    "robo-bee": {"name": "Robo Bee Avatar", "tier": "earn_or_buy", "unlock": 5000, "price": 0.99},
    "sea-bee": {"name": "Sea Bee Avatar", "tier": "premium", "unlock": 18000, "price": 0.99},
    
    # Row 5
    "selfie-bee": {"name": "Selfie Bee Avatar", "tier": "earn_or_buy", "unlock": 3000, "price": 0.99},
    "singer-bee": {"name": "Singer Bee Avatar", "tier": "earn_or_buy", "unlock": 5000, "price": 0.99},
    "space-bee": {"name": "Space Bee Avatar", "tier": "earn_or_buy", "unlock": 5000, "price": 0.99},
    "super-bee": {"name": "Super Bee Avatar", "tier": "earn_or_buy", "unlock": 5000, "price": 0.99},
    "vamp-bee": {"name": "Vamp Bee Avatar", "tier": "premium", "unlock": 15000, "price": 0.99},
    "ware-bee": {"name": "Ware Bee Avatar", "tier": "premium", "unlock": 15000, "price": 0.99},
    "zom-bee": {"name": "Zom Bee Avatar", "tier": "premium", "unlock": 15000, "price": 0.99},
}

# GLB mapping
glb_files = {
    "al-bee": "AlBee.glb",
    "brother-bee": "BrotherBee.glb",
    "buda-bee": "BudaBee.glb",
    "builder-bee": "BuilderBee.glb",
    "cool-bee": "CoolBee.glb",
    "cutie-bee": "CutieBee.glb",
    "detective-bee": "DetectiveBee.glb",
    "knight-bee": "KnightBee.glb",
    "mascot-bee": "MascotBee.glb",
    "motor-bee": "MotorBee.glb",
    "o-bee": "OBee.glb",
    "professor-bee": "ProfessorBee.glb",
    "queen-bee": "QueenBee.glb",
    "robo-bee": "RoboBee.glb",
    "rocker-bee": "RockerBee.glb",
    "singer-bee": "SingerBee.glb",
    "space-bee": "SpaceBee.glb",
    "super-bee": "SuperBee.glb",
    "vamp-bee": "VampBee.glb",
    "ware-bee": "WareBee.glb",
    "zom-bee": "ZomBee.glb",
    # New ones
    "buzzbot-bee": "BuzzbotBee.glb",
    "buzzhero-bee": "SuperBee.glb",  # Uses SuperBee.glb per user
    "doc-bee": "DoctorBee.glb",
    "honey-comb": "HoneyComb.glb",
    "j-rock-bee": "JRockBee.glb",
    "sea-bee": "SeaBee.glb",
}

print("✅ 31 avatars from image:")
for idx, avatar_id in enumerate(sorted(avatars_from_image.keys()), 1):
    info = avatars_from_image[avatar_id]
    glb = glb_files.get(avatar_id, "N/A")
    print(f"{idx:2}. {avatar_id:20} -> {info['name']:30} [{info['tier']:15}] GLB: {glb}")

print(f"\n📊 Total: {len(avatars_from_image)} avatars")

# Count by tier
tier_counts = {}
for info in avatars_from_image.values():
    tier = info['tier']
    tier_counts[tier] = tier_counts.get(tier, 0) + 1

print("\n📈 Distribution:")
for tier, count in sorted(tier_counts.items()):
    print(f"  {tier}: {count}")
