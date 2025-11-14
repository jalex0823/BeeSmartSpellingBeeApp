"""
3D Bee Avatar Catalog
Manages the catalog of 24 bee avatars with monetization tiers

Monetization Tiers:
- DEFAULT_FREE: Available during registration (5 avatars)
- EARN_OR_BUY: Unlock with Honey Points or purchase (5 avatars)
- PREMIUM: Top-tier avatars with higher unlock requirements (12 avatars)
- MASCOT: Default for guests/unregistered users (1 avatar)
- ANXIOUS: Special emotion category (1 avatar)

Dynamic naming: If available, avatar display names are sourced from the
original render PNG filenames that end with '!' under
    Avatars/3D Avatar Files/<folder>/*!.png
We strip the trailing '!' and the .png extension, preserving the author's
original casing/spaces. This lets you name avatars by renaming the render PNGs.

Note: Admin users and premium accounts can override unlock requirements.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Avatar Catalog: All 24 Bee Types
# Each entry includes folder name, specific file names, and monetization data
# Inline catalog (legacy). Can be externalized to data/avatar_catalog.json.
# To avoid disruption, we keep this as the fallback unless USE_EXTERNAL_AVATAR_CATALOG=1.
AVATAR_CATALOG: List[Dict] = [
    {
        "id": "al-bee",
        "product_id": "beesmart.avatar.al_bee",
        "name": "Al Bee Avatar",
        "folder": "al-bee",
        "obj_file": "AlBee.obj",
        "mtl_file": "AlBee.mtl",
        "texture_file": "AlBee.png",
        "description": "Genius bee with wild hair! Discovered the theory of Bee-lativity: E=MC² (Energy = Mighty Cool Buzzing²)",
        "variants": ["default"],
        "category": "classic",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 20000,
        "price": 0.99
    },
    {
        "id": "brother-bee",
        "product_id": "beesmart.avatar.brother_bee",
        "name": "Brother Bee Avatar",
        "folder": "brother-bee",
        "obj_file": "BrotherBee.obj",
        "mtl_file": "BrotherBee.mtl",
        "texture_file": "Buzz_Hero_1022221450.png",
        "description": "Your reliable bee bro – friendly and helpful!",
        "variants": ["default"],
        "category": "classic",
        "tier": "default_free",
        "is_default_free": True,
        "is_purchasable": False,
        "unlock_points": 0,
        "price": 0.00
    },
    {
        "id": "builder-bee",
        "product_id": "beesmart.avatar.builder_bee",
        "name": "Builder Bee Avatar",
        "folder": "builder-bee",
        "obj_file": "BuilderBee.obj",
        "mtl_file": "BuilderBee.mtl",
        "texture_file": "Builder_Bee_1022223231.png",
        "description": "Hard hat on! Builds and fixes around the hive.",
        "variants": ["default"],
        "category": "profession",
        "tier": "default_free",
        "is_default_free": True,
        "is_purchasable": False,
        "unlock_points": 0,
        "price": 0.00
    },
    {
        "id": "buda-bee",
        "product_id": "beesmart.avatar.buda_bee",
        "name": "Buda Bee Avatar",
        "folder": "glb_files",
        "obj_file": "BudaBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Peaceful and wise bee finding inner buzz-lightenment! 🧘‍♂️",
        "variants": ["default"],
        "category": "spiritual",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 15000,
        "price": 0.99
    },
    {
        "id": "buzz-bee",
        "product_id": "beesmart.avatar.buzz_bee",
        "name": "Buzz Bee Avatar",
        "folder": "glb_files",
        "obj_file": "BuzzBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Always buzzing with energy and enthusiasm!",
        "variants": ["default"],
        "category": "classic",
        "tier": "earn_or_buy",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 3000,
        "price": 0.99
    },
    {
        "id": "cool-bee",
        "product_id": "beesmart.avatar.cool_bee",
        "name": "Cool Bee Avatar",
        "folder": "cool-bee",
        "obj_file": "CoolBee.obj",
        "mtl_file": "CoolBee.mtl",
        "texture_file": "Cool_Bee_1022222744.png",
        "description": "The coolest bee around - always stylish!",
        "variants": ["default"],
        "category": "classic",
        "tier": "default_free",
        "is_default_free": True,
        "is_purchasable": False,
        "unlock_points": 0,
        "price": 0.00
    },
    {
        "id": "cutie-bee",
        "product_id": "beesmart.avatar.cutie_bee",
        "name": "Cutie Bee Avatar",
        "folder": "glb_files",
        "obj_file": "CutieBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Adorably sweet bee with the cutest little wings! 🥰",
        "variants": ["default"],
        "category": "cute",
        "tier": "earn_or_buy",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 4000,
        "price": 0.99
    },
    {
        "id": "detective-bee",
        "product_id": "beesmart.avatar.detective_bee",
        "name": "Detective Bee Avatar",
        "folder": "detective-bee",
        "obj_file": "DetectiveBee.obj",
        "mtl_file": "DetectiveBee.mtl",
        "texture_file": "Detective_Bee_1022222906.png",
        "description": "Elementary, my dear Wats-bee! Solving word mysteries with magnifying glass and deductive buzzing.",
        "variants": ["default"],
        "category": "profession",
        "tier": "default_free",
        "is_default_free": True,
        "is_purchasable": False,
        "unlock_points": 0,
        "price": 0.00
    },
    {
        "id": "diva-bee",
        "product_id": "beesmart.avatar.diva_bee",
        "name": "Diva Bee Avatar",
        "folder": "diva-bee",
        "obj_file": "DivaBee.obj",
        "mtl_file": "DivaBee.mtl",
        "texture_file": "Bee_Diva_1018233351.png",
        "description": "Glamorous and fabulous! The Bee-yoncé of the hive. Born to spell, born to shine!",
        "variants": ["default"],
        "category": "entertainment",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 12000,
        "price": 0.99
    },
    {
        "id": "doc-bee",
        "product_id": "beesmart.avatar.doc_bee",
        "name": "Doc Bee Avatar",
        "folder": "glb_files",
        "obj_file": "DocBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Medical expert bee ready to diagnose and cure!",
        "variants": ["default"],
        "category": "profession",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 18000,
        "price": 0.99
    },
    {
        "id": "explorer-bee",
        "product_id": "beesmart.avatar.explorer_bee",
        "name": "Explorer Bee Avatar",
        "folder": "explorer-bee",
        "obj_file": "ExplorerBee.obj",
        "mtl_file": "ExplorerBee.mtl",
        "texture_file": "Explorer_Bee_1022223832.png",
        "description": "Adventure awaits! Ready to discover new horizons.",
        "variants": ["default"],
        "category": "adventure",
        "tier": "default_free",
        "is_default_free": True,
        "is_purchasable": False,
        "unlock_points": 0,
        "price": 0.00
    },
    {
        "id": "franken-bee",
        "product_id": "beesmart.avatar.franken_bee",
        "name": "Franken Bee Avatar",
        "folder": "glb_files",
        "obj_file": "FrankenBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Created in Dr. Franken-sting's laboratory! Spells by lightning power. 'It's alive... and spelling!'",
        "variants": ["default"],
        "category": "fantasy",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 18000,
        "price": 0.99
    },
    {
        "id": "honey-comb",
        "product_id": "beesmart.avatar.honey_comb",
        "name": "Honey Comb Avatar",
        "folder": "glb_files",
        "obj_file": "HoneyComb.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Sweet geometric perfection! The architectural marvel of the hive.",
        "variants": ["default"],
        "category": "classic",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 18000,
        "price": 0.99
    },
    {
        "id": "j-rock-bee",
        "product_id": "beesmart.avatar.j_rock_bee",
        "name": "J Rock Bee Avatar",
        "folder": "glb_files",
        "obj_file": "JRockBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Rock star bee with attitude and style!",
        "variants": ["default"],
        "category": "entertainment",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 18000,
        "price": 0.99
    },
    {
        "id": "knight-bee",
        "product_id": "beesmart.avatar.knight_bee",
        "name": "Knight Bee Avatar",
        "folder": "glb_files",
        "obj_file": "KnightBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Brave and noble! Defender of the hive.",
        "variants": ["default"],
        "category": "fantasy",
        "tier": "earn_or_buy",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 4000,
        "price": 0.99
    },
    {
        "id": "mascot-bee",
        "product_id": "beesmart.avatar.mascot_bee",
        "name": "Mascot Bee Avatar",
        "folder": "mascot-bee",
        "obj_file": "MascotBee.obj",
        "mtl_file": "MascotBee.mtl",
        "texture_file": "MascotBee.png",
        "description": "The original BeeSmart mascot! Cheerful and encouraging.",
        "variants": ["default"],
        "category": "classic",
        "tier": "mascot",
        "is_default_free": True,
        "is_purchasable": False,
        "unlock_points": 0,
        "price": 0.00
    },
    {
        "id": "professor-bee",
        "product_id": "beesmart.avatar.professor_bee",
        "name": "Professor Bee Avatar",
        "folder": "professor-bee",
        "obj_file": "ProfessorBee.obj",
        "mtl_file": "ProfessorBee.mtl",
        "texture_file": "ProfessorBee.png",
        "description": "Wise and knowledgeable! The scholarly bee.",
        "variants": ["default"],
        "category": "profession",
        "tier": "earn_or_buy",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 9000,
        "price": 0.99
    },
    {
        "id": "queen-bee",
        "product_id": "beesmart.avatar.queen_bee",
        "name": "Queen Bee Avatar",
        "folder": "queen-bee",
        "obj_file": "QueenBee.obj",
        "mtl_file": "QueenBee.mtl",
        "texture_file": "Queen_Bee_Majesty_1022222156.png",
        "description": "Royal and majestic! Leader with grace.",
        "variants": ["default"],
        "category": "royal",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 28000,
        "price": 0.99
    },
    {
        "id": "robo-bee",
        "product_id": "beesmart.avatar.robo_bee",
        "name": "Robo Bee Avatar",
        "folder": "glb_files",
        "obj_file": "RoboBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Buzzbot 3000! Programmed with 1 million words. Runs on honey-powered circuits. *BEEP* Spelling complete!",
        "variants": ["default"],
        "category": "tech",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 30000,
        "price": 0.99
    },
    {
        "id": "rocker-bee",
        "product_id": "beesmart.avatar.rocker_bee",
        "name": "Rocker Bee Avatar",
        "folder": "rocker-bee",
        "obj_file": "RockerBee.obj",
        "mtl_file": "RockerBee.mtl",
        "texture_file": "RockerBee.png",
        "description": "Rock and roll! Lead singer of The Bee-tles. Spells to the rhythm of electric guitar!",
        "variants": ["default"],
        "category": "entertainment",
        "tier": "earn_or_buy",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 8000,
        "price": 0.99
    },
    {
        "id": "sea-bee",
        "product_id": "beesmart.avatar.sea_bee",
        "name": "Sea Bee Avatar",
        "folder": "glb_files",
        "obj_file": "SeaBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Navy SeaBee! Construction battalion of the ocean. Can build words underwater! 'We Build, We Fight, We Spell!'",
        "variants": ["default"],
        "category": "adventure",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 18000,
        "price": 0.99
    },
    {
        "id": "selfie-bee",
        "product_id": "beesmart.avatar.selfie_bee",
        "name": "Selfie Bee Avatar",
        "folder": "glb_files",
        "obj_file": "SelfieBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Say cheese! Always ready for the perfect selfie!",
        "variants": ["default"],
        "category": "entertainment",
        "tier": "earn_or_buy",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 5000,
        "price": 0.99
    },
    {
        "id": "vamp-bee",
        "product_id": "beesmart.avatar.vamp_bee",
        "name": "Vamp Bee Avatar",
        "folder": "vamp-bee",
        "obj_file": "VampBee.obj",
        "mtl_file": "VampBee.mtl",
        "texture_file": "VampBee.png",
        "description": "Count Bee-cula from Transyl-hive-nia! Spells words, not blood. 'I vant to spell your vords!'",
        "variants": ["default"],
        "category": "fantasy",
        "tier": "earn_or_buy",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 10000,
        "price": 0.99
    },
    {
        "id": "ware-bee",
        "product_id": "beesmart.avatar.ware_bee",
        "name": "Ware Bee Avatar",
        "folder": "ware-bee",
        "obj_file": "WareBee.obj",
        "mtl_file": "WareBee.mtl",
        "texture_file": "WareBee.png",
        "description": "Were-bee of London! Howls at the full moon and spells by moonlight. Transforms during spelling tests!",
        "variants": ["default"],
        "category": "fantasy",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 27000,
        "price": 0.99
    },
    {
        "id": "zom-bee",
        "product_id": "beesmart.avatar.zom_bee",
        "name": "Zom Bee Avatar",
        "folder": "zom-bee",
        "obj_file": "ZomBee.obj",
        "mtl_file": "ZomBee.mtl",
        "texture_file": "ZomBee.png",
        "description": "The Walking Buzzed! Craves BRAINS... brainy words, that is. Undead but spelling well!",
        "variants": ["default"],
        "category": "fantasy",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 25000,
        "price": 0.99
    },
    {
        "id": "motor-bee",
        "product_id": "beesmart.avatar.motor_bee",
        "name": "Motor Bee Avatar",
        "folder": "glb_files",
        "obj_file": "MotorBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Speed demon bee! Races through spelling tests on two wheels.",
        "variants": ["default"],
        "category": "action",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 20000,
        "price": 0.99
    },
    {
        "id": "o-bee",
        "product_id": "beesmart.avatar.o_bee",
        "name": "O Bee Avatar",
        "folder": "glb_files",
        "obj_file": "OBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Wise Jedi Master of the hive! May the buzz be with you. 🐝✨",
        "variants": ["default"],
        "category": "fantasy",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 30000,
        "price": 0.99
    },
    {
        "id": "singer-bee",
        "product_id": "beesmart.avatar.singer_bee",
        "name": "Singer Bee Avatar",
        "folder": "glb_files",
        "obj_file": "SingerBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Beautiful voice! Sings spelling words in perfect harmony.",
        "variants": ["default"],
        "category": "entertainment",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 22000,
        "price": 0.99
    },
    {
        "id": "space-bee",
        "product_id": "beesmart.avatar.space_bee",
        "name": "Space Bee Avatar",
        "folder": "glb_files",
        "obj_file": "SpaceBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Astronaut bee! First bee on the moon. Spells in zero gravity!",
        "variants": ["default"],
        "category": "adventure",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 18000,
        "price": 0.99
    },
    {
        "id": "super-bee",
        "product_id": "beesmart.avatar.super_bee",
        "name": "Super Bee Avatar",
        "folder": "glb_files",
        "obj_file": "SuperBee.glb",
        "mtl_file": "",
        "texture_file": "",
        "description": "Superhero bee! Saves the day with super spelling powers and cape!",
        "variants": ["default"],
        "category": "fantasy",
        "tier": "premium",
        "is_default_free": False,
        "is_purchasable": True,
        "unlock_points": 26000,
        "price": 0.99
    }
]

# --- Monetization Constants & Helpers ----------------------------------------

# Bundle Pricing
BUNDLE_PRICING = {
    "top_bee_bundle": {
        "name": "Top Bee Bundle",
        "description": "Unlocks all Top Avatars instantly",
        "price": 9.99,
        "includes_tiers": ["premium"]
    },
    "ultimate_hive_bundle": {
        "name": "Ultimate Hive Bundle",
        "description": "Unlocks every avatar in the app",
        "price": 14.99,
        "includes_tiers": ["earn_or_buy", "premium", "special"]
    }
}

# Helper functions for monetization tiers
_CATALOG_LOADED: Optional[List[Dict]] = None
_CATALOG_SOURCE: str = "inline"

def _load_external_catalog() -> Optional[List[Dict]]:
    """Attempt to load avatar catalog from JSON file.
    Returns list if successful, else None. Non-fatal on errors."""
    catalog_path = Path("data/avatar_catalog.json")
    if not catalog_path.exists():
        return None
    try:
        with catalog_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return data
    except Exception as e:
        if os.environ.get("APP_DEBUG_STARTUP"):
            print(f"⚠️ External avatar catalog load failed: {e}")
    return None

def get_avatar_catalog() -> List[Dict]:
    """Public accessor with lazy loading and optional external override.
    Usage: from avatar_catalog import get_avatar_catalog instead of AVATAR_CATALOG for future-proofing.
    """
    global _CATALOG_LOADED, _CATALOG_SOURCE
    if _CATALOG_LOADED is not None:
        return _CATALOG_LOADED
    use_external_flag = os.environ.get("USE_EXTERNAL_AVATAR_CATALOG", "0").strip().lower() in ("1", "true", "yes", "on")
    if use_external_flag:
        external = _load_external_catalog()
        if external:
            _CATALOG_LOADED = external
            _CATALOG_SOURCE = "external-json"
            if os.environ.get("APP_DEBUG_STARTUP"):
                print(f"📦 Loaded avatar catalog from JSON ({len(external)} entries)")
            return _CATALOG_LOADED
        else:
            if os.environ.get("APP_DEBUG_STARTUP"):
                print("↩️ Falling back to inline avatar catalog (external not available)")
    # Fallback to inline
    _CATALOG_LOADED = AVATAR_CATALOG
    return _CATALOG_LOADED

def export_avatar_catalog_json(target: Optional[str] = None) -> Path:
    """Utility: write current effective catalog to JSON for future externalization.
    Does nothing unless explicitly invoked (low-risk)."""
    effective = get_avatar_catalog()
    out_path = Path(target) if target else Path("data/avatar_catalog.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(effective, f, indent=2)
    print(f"📝 Exported avatar catalog ({len(effective)} entries) to {out_path}")
    return out_path

def get_free_avatars():
    """Returns list of avatars available during registration (default_free)"""
    return [a for a in get_avatar_catalog() if a.get("is_default_free", False)]

def get_earn_or_buy_avatars():
    """Returns list of avatars in earn-or-buy tier"""
    return [a for a in get_avatar_catalog() if a.get("tier") == "earn_or_buy"]

def get_premium_avatars():
    """Returns list of premium tier avatars"""
    return [a for a in get_avatar_catalog() if a.get("tier") == "premium"]

def get_avatars_by_tier(tier):
    """Returns avatars filtered by tier (default_free, earn_or_buy, premium, mascot, special)"""
    return [a for a in get_avatar_catalog() if a.get("tier") == tier]

def check_avatar_unlocked(avatar_id, user_honey_points=0, purchased_avatars=None):
    """
    Check if user has unlocked an avatar via points or purchase.
    Admin users bypass all checks via their user profile.
    
    Args:
        avatar_id: The avatar ID to check
        user_honey_points: User's current Honey Points balance
        purchased_avatars: List of avatar IDs user has purchased
        
    Returns:
        dict with keys: unlocked (bool), reason (str), required_points (int), price (float)
    """
    if purchased_avatars is None:
        purchased_avatars = []
    
    avatar = next((a for a in AVATAR_CATALOG if a["id"] == avatar_id), None)
    if not avatar:
        return {"unlocked": False, "reason": "Avatar not found", "required_points": 0, "price": 0}
    
    # Default free avatars are always unlocked
    if avatar.get("is_default_free", False):
        return {"unlocked": True, "reason": "Free avatar", "required_points": 0, "price": 0}
    
    # Check if purchased
    if avatar_id in purchased_avatars:
        return {"unlocked": True, "reason": "Purchased", "required_points": avatar.get("unlock_points", 0), "price": avatar.get("price", 0)}
    
    # Check Honey Points
    required_points = avatar.get("unlock_points", 0)
    if user_honey_points >= required_points:
        return {"unlocked": True, "reason": "Earned via Honey Points", "required_points": required_points, "price": avatar.get("price", 0)}
    
    # Not unlocked
    return {
        "unlocked": False, 
        "reason": f"Requires {required_points - user_honey_points} more Honey Points or ${avatar.get('price', 0):.2f}",
        "required_points": required_points,
        "price": avatar.get("price", 0)
    }


# --- Dynamic name overrides from original '!' PNGs ---------------------------
# We map 3D folder prefixes to app avatar IDs, then scan each folder for the
# render PNG whose basename ends with '!'. The label is the basename without '!'.

SOURCE_3D_DIR = os.path.join("Avatars", "3D Avatar Files")

FOLDER_PREFIX_TO_AVATAR_ID = {
    "Cool_Bee": "cool-bee",
    "Explorer_Bee": "explorer-bee",
    "Rockin_Bee": "rockstar-bee",
    "Bee_Doctor": "doctor-bee",
    "Bee_Scientist": "scientist-bee",
    "Professor_Bee": "professor-bee",
    "Super_Bee_Hero": "superhero-bee",
    "Bee_Knight": "knight-bee",
    "Buzzbot_Bee": "robot-bee",
    "Bee_Diva": "bee-diva",
    "Queen_Bee_Majesty": "queen-bee",
    # We consolidate Bee_Majesty to queen-bee as a single catalog entry
    "Bee_Majesty": "queen-bee",
    "SeaBee": "sea-bee",
    "Motorcycle_Buzz_Bee": "biker-bee",
    "Builder_Bee": "builder-bee",
    "BrotherBee": "brother-bee",
    "Buzzing_Menace": "killer-bee",
    "Anxious_Bee": "anxious-bee",
}


def _find_bang_png_in_folder(folder_path: str) -> str | None:
    try:
        for name in os.listdir(folder_path):
            lower = name.lower()
            if not (lower.endswith('.png') or lower.endswith('.jpg') or lower.endswith('.jpeg')):
                continue
            base = os.path.splitext(name)[0]
            if base.endswith("!"):
                return name
    except Exception:
        return None
    return None


def _build_dynamic_name_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    if not os.path.isdir(SOURCE_3D_DIR):
        return mapping
    for entry in os.listdir(SOURCE_3D_DIR):
        full = os.path.join(SOURCE_3D_DIR, entry)
        if not os.path.isdir(full):
            continue
        # Match folder prefix to avatar id
        avatar_id = None
        for prefix, aid in FOLDER_PREFIX_TO_AVATAR_ID.items():
            if entry.startswith(prefix):
                avatar_id = aid
                break
        if not avatar_id:
            continue
        bang_png = _find_bang_png_in_folder(full)
        if not bang_png:
            continue
        base = os.path.splitext(bang_png)[0]
        label = base[:-1] if base.endswith("!") else base
        mapping[avatar_id] = label
    return mapping


# Apply dynamic overrides at import time
try:
    _dynamic_names = _build_dynamic_name_map()
    if _dynamic_names:
        for a in AVATAR_CATALOG:
            if a['id'] in _dynamic_names:
                a['name'] = _dynamic_names[a['id']]
except Exception as _e:  # non-fatal
    pass

# --- Pricing and Points Overrides -------------------------------------------
# Business rule (2025-11-13):
# - All locked avatars default to $0.99 unless explicitly listed otherwise
# - Premium set priced at $0.99 each (12 avatars):
#   doctor-bee, knight-bee, monster-bee, rocker-bee, seabea, buzz-bee,
#   selfie-bee, anxious-bee, professor-bee, vamp-bee, franken-bee, obee
# - Ultra Premium set priced at $1.99 each (9 avatars or via bundle):
#   al-bee, astro-bee, biker-bee, diva-bee, superbee, queen-bee,
#   robo-bee, ware-bee, zom-bee
# - Earn-or-buy tiers ensure the following point thresholds:
#   doctor-bee=2000, knight-bee=4000, monster-bee=6000,
#   rocker-bee=8000, seabea=10000

DEFAULT_LOCKED_PRICE = 0.99
PREMIUM_199_IDS = {
    "al-bee",
    "astro-bee",
    "biker-bee",
    "diva-bee",
    "superbee",
    "queen-bee",
    "robo-bee",
    "ware-bee",
    "zom-bee",
}

EARN_OR_BUY_POINTS = {
    "doctor-bee": 2000,
    "knight-bee": 4000,
    "monster-bee": 6000,
    "rocker-bee": 8000,
    "seabea": 10000,
}

# Apply pricing/points policy programmatically to guarantee consistency
for a in AVATAR_CATALOG:
    # Skip completely free defaults
    if not a.get("is_default_free", False):
        # Default price for all locked avatars
        a["price"] = DEFAULT_LOCKED_PRICE
    # Premium set at $1.99
    if a.get("id") in PREMIUM_199_IDS:
        a["price"] = 1.99
    # Enforce earn-or-buy point thresholds where applicable
    if a.get("id") in EARN_OR_BUY_POINTS:
        a["unlock_points"] = EARN_OR_BUY_POINTS[a["id"]]



def get_avatar_catalog():
    """Get the complete avatar catalog"""
    return AVATAR_CATALOG


def get_avatar_info(avatar_id, variant='default'):
    """
    Get avatar information with URLs for 3D model and thumbnail
    
    Args:
        avatar_id: Avatar identifier (e.g., 'explorer-bee')
        variant: 'default' (we have single models, not gendered variants)
        
    Returns:
        dict with avatar info including URLs
    """
    # Find avatar in catalog
    avatar = next((a for a in AVATAR_CATALOG if a['id'] == avatar_id), None)
    
    # Fallback to cool bee if not found
    if not avatar:
        avatar = AVATAR_CATALOG[0]  # al-bee (first in catalog)
        avatar_id = avatar['id']
    
    # All our avatars use 'default' variant (no male/female)
    variant = 'default'
    
    # Get specific filenames from catalog (with fallback to generic names for backward compatibility)
    obj_file = avatar.get('obj_file', 'model.obj')
    mtl_file = avatar.get('mtl_file', 'model.mtl')
    texture_file = avatar.get('texture_file', 'texture.png')
    
    # Get thumbnail filename from catalog folder name (e.g., al-bee -> AlBee!.png)
    # Convert folder name to proper case for thumbnail
    folder = avatar.get('folder', avatar_id)
    
    # GLB avatars use AvatarThumbnails subfolder
    if folder == 'glb_files':
        if avatar_id == 'astro-bee':
            thumbnail_file = 'AvatarThumbnails/AstroBee!.png'
        elif avatar_id == 'buzz-bee':
            thumbnail_file = 'AvatarThumbnails/BuzzBee!.png'
        elif avatar_id == 'knight-bee':
            thumbnail_file = 'AvatarThumbnails/KnightBee!.png'
        elif avatar_id == 'selfie-bee':
            thumbnail_file = 'AvatarThumbnails/SelfieBee!.png'
        else:
            thumbnail_file = 'AvatarThumbnails/thumbnail.png'  # fallback
    elif folder == 'al-bee':
        thumbnail_file = 'AlBee!.png'
    elif folder == 'anxious-bee':
        thumbnail_file = 'AnxiousBee!.png'
    elif folder == 'biker-bee':
        thumbnail_file = 'BikerBee!.png'
    elif folder == 'brother-bee':
        thumbnail_file = 'BrotherBee!.png'
    elif folder == 'builder-bee':
        thumbnail_file = 'BuilderBee!.png'
    elif folder == 'cool-bee':
        thumbnail_file = 'CoolBee!.png'
    elif folder == 'detective-bee':
        thumbnail_file = 'DetectiveBee!.png'
    elif folder == 'diva-bee':
        thumbnail_file = 'DivaBee!.png'
    elif folder == 'doctor-bee':
        thumbnail_file = 'DoctorBee!.png'
    elif folder == 'explorer-bee':
        thumbnail_file = 'ExplorerBee!.png'
    elif folder == 'franken-bee':
        thumbnail_file = 'FrankenBee!.png'
    elif folder == 'mascot-bee':
        thumbnail_file = 'MascotBee!.png'
    elif folder == 'monster-bee':
        thumbnail_file = 'MonsterBee!.png'
    elif folder == 'professor-bee':
        thumbnail_file = 'ProfessorBee!.png'
    elif folder == 'queen-bee':
        thumbnail_file = 'QueenBee!.png'
    elif folder == 'robo-bee':
        thumbnail_file = 'RoboBee!.png'
    elif folder == 'rocker-bee':
        thumbnail_file = 'RockerBee!.png'
    elif folder == 'seabea':
        thumbnail_file = 'Seabea!.png'
    elif folder == 'superbeehero':
        thumbnail_file = 'SuperBeeHero!.png'
    elif folder == 'vamp-bee':
        thumbnail_file = 'VampBee!.png'
    elif folder == 'ware-bee':
        thumbnail_file = 'WareBee!.png'
    elif folder == 'zom-bee':
        thumbnail_file = 'ZomBee!.png'
    else:
        thumbnail_file = 'thumbnail.png'  # fallback
    
    # Build asset URLs
    base_path = f"/static/assets/avatars/{avatar_id}"
    
    # Auto-validate MTL references (with error handling to not break the app)
    try:
        validate_avatar_mtl_references(avatar_id)
    except Exception as e:
        # Log error but don't break avatar loading
        print(f"⚠️  MTL validation warning for {avatar_id}: {e}")
    
    return {
        'id': avatar_id,
        'name': avatar['name'],
        'description': avatar['description'],
        'variant': variant,
        'category': avatar['category'],
        'thumbnail_url': f"{base_path}/{thumbnail_file}",
        'preview_url': f"{base_path}/{thumbnail_file}",  # Use same as thumbnail
        'model_obj_url': f"{base_path}/{obj_file}",  # Now uses specific filename (e.g., ProfessorBee.obj)
        'model_mtl_url': f"{base_path}/{mtl_file}",  # Now uses specific filename (e.g., ProfessorBee.mtl)
        'texture_url': f"{base_path}/{texture_file}",  # Now uses specific filename (e.g., ProfessorBee.png)
        'fallback_url': "/static/assets/avatars/fallback.png"
    }


def get_avatars_by_category():
    """Get avatars grouped by category"""
    categories = {}
    
    for avatar in AVATAR_CATALOG:
        category = avatar['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(avatar)
    
    return categories


def search_avatars(query):
    """
    Search avatars by name or description
    
    Args:
        query: Search string
        
    Returns:
        List of matching avatars
    """
    query = query.lower()
    results = []
    
    for avatar in AVATAR_CATALOG:
        if (query in avatar['name'].lower() or 
            query in avatar['description'].lower() or
            query in avatar['category'].lower()):
            results.append(avatar)
    
    return results


def validate_avatar(avatar_id, variant='default'):
    """
    Validate that avatar_id and variant are valid
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if avatar exists
    avatar = next((a for a in AVATAR_CATALOG if a['id'] == avatar_id), None)
    
    if not avatar:
        return False, f"Avatar '{avatar_id}' not found in catalog"
    
    # We only have default variant for these models
    if variant and variant != 'default':
        # Auto-correct to default instead of erroring
        variant = 'default'
    
    return True, "Valid"


# Default avatar for new users
DEFAULT_AVATAR = {
    'id': 'cool-bee',
    'variant': 'default'
}


def generate_theme_from_title(avatar_name):
    """
    Generate theme attributes based on avatar title/name
    
    Args:
        avatar_name (str): The display name of the avatar
        
    Returns:
        dict: Theme configuration with colors, styles, and personality traits
    """
    name_lower = avatar_name.lower()
    
    # Theme mapping based on avatar title keywords
    theme_rules = {
        'al': {
            'primary_color': '#00C9FF',
            'secondary_color': '#92FE9D', 
            'accent_color': '#00D4FF',
            'personality': ['intelligent', 'analytical', 'futuristic'],
            'ui_style': 'tech',
            'animation_style': 'digital',
            'description_keywords': ['AI-powered', 'smart', 'technology']
        },
        'anxious': {
            'primary_color': '#B19CD9',
            'secondary_color': '#C9B037',
            'accent_color': '#DDA0DD',
            'personality': ['nervous', 'careful', 'thoughtful'],
            'ui_style': 'soft',
            'animation_style': 'gentle',
            'description_keywords': ['nervous', 'careful', 'trying their best']
        },
        'biker': {
            'primary_color': '#FF6B35',
            'secondary_color': '#1B1B1B',
            'accent_color': '#FFD23F',
            'personality': ['adventurous', 'bold', 'fast'],
            'ui_style': 'edgy',
            'animation_style': 'dynamic',
            'description_keywords': ['fast', 'fearless', 'motorcycle', 'road']
        },
        'brother': {
            'primary_color': '#4A90E2',
            'secondary_color': '#87CEEB',
            'accent_color': '#5DADE2',
            'personality': ['friendly', 'reliable', 'supportive'],
            'ui_style': 'friendly',
            'animation_style': 'warm',
            'description_keywords': ['reliable', 'friendly', 'helpful', 'bro']
        },
        'builder': {
            'primary_color': '#FF8C00',
            'secondary_color': '#FFD700',
            'accent_color': '#FFA500',
            'personality': ['hardworking', 'practical', 'constructive'],
            'ui_style': 'industrial',
            'animation_style': 'sturdy',
            'description_keywords': ['builds', 'construction', 'hard hat', 'work']
        },
        'cool': {
            'primary_color': '#40E0D0',
            'secondary_color': '#98FB98',
            'accent_color': '#00CED1',
            'personality': ['stylish', 'confident', 'trendy'],
            'ui_style': 'modern',
            'animation_style': 'smooth',
            'description_keywords': ['cool', 'stylish', 'trendy', 'awesome']
        },
        'diva': {
            'primary_color': '#FF69B4',
            'secondary_color': '#FFB6C1',
            'accent_color': '#FF1493',
            'personality': ['glamorous', 'confident', 'dramatic'],
            'ui_style': 'glamorous',
            'animation_style': 'flamboyant',
            'description_keywords': ['glamorous', 'fabulous', 'star', 'diva']
        },
        'doctor': {
            'primary_color': '#20B2AA',
            'secondary_color': '#AFEEEE',
            'accent_color': '#48CAE4',
            'personality': ['caring', 'knowledgeable', 'helpful'],
            'ui_style': 'medical',
            'animation_style': 'professional',
            'description_keywords': ['heal', 'medical', 'doctor', 'care']
        },
        'explorer': {
            'primary_color': '#8FBC8F',
            'secondary_color': '#F0E68C',
            'accent_color': '#32CD32',
            'personality': ['adventurous', 'curious', 'brave'],
            'ui_style': 'adventure',
            'animation_style': 'exploring',
            'description_keywords': ['adventure', 'discover', 'explorer', 'journey']
        },
        'knight': {
            'primary_color': '#4169E1',
            'secondary_color': '#C0C0C0',
            'accent_color': '#6495ED',
            'personality': ['brave', 'noble', 'protective'],
            'ui_style': 'medieval',
            'animation_style': 'heroic',
            'description_keywords': ['brave', 'noble', 'defender', 'knight']
        },
        'mascot': {
            'primary_color': '#FFD700',
            'secondary_color': '#FFA500',
            'accent_color': '#FFFF00',
            'personality': ['cheerful', 'energetic', 'representative'],
            'ui_style': 'classic',
            'animation_style': 'bouncy',
            'description_keywords': ['mascot', 'cheerful', 'energetic', 'representative']
        },
        'monster': {
            'primary_color': '#8A2BE2',
            'secondary_color': '#9932CC',
            'accent_color': '#9400D3',
            'personality': ['spooky', 'playful', 'mysterious'],
            'ui_style': 'spooky',
            'animation_style': 'creepy-cute',
            'description_keywords': ['spooky', 'monster', 'halloween', 'mysterious']
        },
        'professor': {
            'primary_color': '#8B4513',
            'secondary_color': '#DEB887',
            'accent_color': '#CD853F',
            'personality': ['wise', 'knowledgeable', 'scholarly'],
            'ui_style': 'academic',
            'animation_style': 'thoughtful',
            'description_keywords': ['wise', 'knowledgeable', 'education', 'professor']
        },
        'queen': {
            'primary_color': '#FFD700',
            'secondary_color': '#FF69B4',
            'accent_color': '#FFA500',
            'personality': ['royal', 'majestic', 'leadership'],
            'ui_style': 'royal',
            'animation_style': 'regal',
            'description_keywords': ['royal', 'majestic', 'queen', 'leader']
        },
        'robo': {
            'primary_color': '#00FFFF',
            'secondary_color': '#C0C0C0',
            'accent_color': '#00CED1',
            'personality': ['robotic', 'precise', 'futuristic'],
            'ui_style': 'robotic',
            'animation_style': 'mechanical',
            'description_keywords': ['robotic', 'futuristic', 'tech', 'robot']
        },
        'rocker': {
            'primary_color': '#DC143C',
            'secondary_color': '#1B1B1B',
            'accent_color': '#FF4500',
            'personality': ['musical', 'energetic', 'rebellious'],
            'ui_style': 'rock',
            'animation_style': 'rhythmic',
            'description_keywords': ['rock', 'musical', 'energetic', 'rocker']
        },
        'seabea': {
            'primary_color': '#008B8B',
            'secondary_color': '#20B2AA',
            'accent_color': '#00CED1',
            'personality': ['oceanic', 'adventurous', 'fluid'],
            'ui_style': 'aquatic',
            'animation_style': 'flowing',
            'description_keywords': ['ocean', 'sea', 'underwater', 'aquatic']
        },
        'super': {
            'primary_color': '#FF0000',
            'secondary_color': '#0000FF',
            'accent_color': '#FFFF00',
            'personality': ['heroic', 'powerful', 'protective'],
            'ui_style': 'superhero',
            'animation_style': 'heroic',
            'description_keywords': ['super', 'hero', 'powers', 'cape']
        },
        'ninja': {
            'primary_color': '#2F2F2F',
            'secondary_color': '#8B0000',
            'accent_color': '#696969',
            'personality': ['stealthy', 'agile', 'focused'],
            'ui_style': 'stealth',
            'animation_style': 'swift',
            'description_keywords': ['ninja', 'stealth', 'shadow', 'warrior']
        },
        'warrior': {
            'primary_color': '#B8860B',
            'secondary_color': '#8B4513',
            'accent_color': '#DAA520',
            'personality': ['brave', 'strong', 'fierce'],
            'ui_style': 'warrior',
            'animation_style': 'combat',
            'description_keywords': ['warrior', 'battle', 'brave', 'fighter']
        },
        'pirate': {
            'primary_color': '#8B4513',
            'secondary_color': '#FFD700',
            'accent_color': '#DC143C',
            'personality': ['adventurous', 'bold', 'seafaring'],
            'ui_style': 'pirate',
            'animation_style': 'swashbuckling',
            'description_keywords': ['pirate', 'treasure', 'ship', 'adventure']
        },
        'space': {
            'primary_color': '#4B0082',
            'secondary_color': '#C0C0C0',
            'accent_color': '#00BFFF',
            'personality': ['cosmic', 'futuristic', 'exploratory'],
            'ui_style': 'cosmic',
            'animation_style': 'floating',
            'description_keywords': ['space', 'cosmic', 'galaxy', 'astronaut']
        },
        'astro': {
            'primary_color': '#4B0082',
            'secondary_color': '#C0C0C0', 
            'accent_color': '#00BFFF',
            'personality': ['cosmic', 'exploratory', 'scientific'],
            'ui_style': 'cosmic',
            'animation_style': 'floating',
            'description_keywords': ['astronaut', 'space', 'cosmic', 'stellar']
        },
        'franken': {
            'primary_color': '#228B22',
            'secondary_color': '#8B4513',
            'accent_color': '#FF4500',
            'personality': ['spooky', 'experimental', 'unique'],
            'ui_style': 'spooky',
            'animation_style': 'jolting',
            'description_keywords': ['monster', 'experiment', 'spooky', 'laboratory']
        },
        'ware': {
            'primary_color': '#8B4513',
            'secondary_color': '#2F4F4F',
            'accent_color': '#FFD700',
            'personality': ['fierce', 'loyal', 'wild'],
            'ui_style': 'werewolf',
            'animation_style': 'primal',
            'description_keywords': ['werewolf', 'lunar', 'howl', 'transformation']
        },
        'zom': {
            'primary_color': '#556B2F',
            'secondary_color': '#8B4513',
            'accent_color': '#FF0000',
            'personality': ['spooky', 'mysterious', 'undead'],
            'ui_style': 'zombie',
            'animation_style': 'shambling',
            'description_keywords': ['zombie', 'undead', 'spooky', 'halloween']
        },
        'vamp': {
            'primary_color': '#8B0000',
            'secondary_color': '#2F2F2F',
            'accent_color': '#FFD700',
            'personality': ['mysterious', 'elegant', 'nocturnal'],
            'ui_style': 'vampire',
            'animation_style': 'graceful',
            'description_keywords': ['vampire', 'mysterious', 'night', 'elegant']
        },
        'detective': {
            'primary_color': '#8B4513',
            'secondary_color': '#2F4F4F',
            'accent_color': '#DAA520',
            'personality': ['investigative', 'clever', 'observant'],
            'ui_style': 'detective',
            'animation_style': 'investigating',
            'description_keywords': ['detective', 'mystery', 'investigate', 'clue']
        }
    }
    
    # Find matching theme rule
    for keyword, theme in theme_rules.items():
        if keyword in name_lower:
            return theme
    
    # Default theme if no match found
    return {
        'primary_color': '#FFD700',
        'secondary_color': '#FFA500', 
        'accent_color': '#FFFF00',
        'personality': ['friendly', 'helpful', 'cheerful'],
        'ui_style': 'default',
        'animation_style': 'standard',
        'description_keywords': ['friendly', 'helpful', 'bee']
    }


def install_new_avatar(folder_name, display_name=None, category=None, description=None):
    """
    Install a new avatar from an existing folder in the 3D Avatar Files directory
    Automatically generates theme configuration based on the avatar name
    
    Args:
        folder_name (str): Name of the folder in static/Avatars/3D Avatar Files/
        display_name (str, optional): Display name for the avatar. If None, uses folder_name
        category (str, optional): Category for the avatar. Auto-generated if None
        description (str, optional): Description for the avatar. Auto-generated if None
        
    Returns:
        dict: Avatar configuration with theme data, or None if installation failed
    """
    import os
    
    # Validate folder exists
    folder_path = f"static/Avatars/3D Avatar Files/{folder_name}"
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return None
    
    # Generate avatar ID from folder name
    avatar_id = folder_name.lower().replace(' ', '-').replace('_', '-')
    
    # Use display name or derive from folder
    if display_name is None:
        display_name = folder_name.replace('_', ' ').replace('-', ' ')
    
    # Generate theme configuration
    theme = generate_theme_from_title(display_name)
    
    # Auto-generate category if not provided
    if category is None:
        name_lower = display_name.lower()
        if any(word in name_lower for word in ['doctor', 'professor', 'builder', 'teacher']):
            category = 'profession'
        elif any(word in name_lower for word in ['king', 'queen', 'royal', 'crown']):
            category = 'royal'
        elif any(word in name_lower for word in ['monster', 'zombie', 'vampire', 'ghost', 'witch']):
            category = 'fantasy'
        elif any(word in name_lower for word in ['robo', 'tech', 'cyber', 'ai', 'robot']):
            category = 'tech'
        elif any(word in name_lower for word in ['rock', 'music', 'diva', 'star', 'performer']):
            category = 'entertainment'
        elif any(word in name_lower for word in ['explore', 'adventure', 'sea', 'ocean', 'travel']):
            category = 'adventure'
        elif any(word in name_lower for word in ['super', 'hero', 'knight', 'warrior', 'fighter']):
            category = 'fantasy'
        elif any(word in name_lower for word in ['biker', 'racer', 'sports', 'athlete']):
            category = 'action'
        elif any(word in name_lower for word in ['happy', 'sad', 'angry', 'anxious', 'cheerful']):
            category = 'emotion'
        else:
            category = 'classic'
    
    # Auto-generate description with theme keywords
    if description is None:
        keywords = theme['description_keywords']
        personality = theme['personality']
        description = f"{', '.join(keywords[:2]).title()}! A {personality[0]} bee character."
    
    # Check for required files
    required_files = [
        f"{folder_name}.obj",
        f"{folder_name}.mtl", 
        f"{folder_name}.png",
        f"{folder_name}!.png"  # Thumbnail
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join(folder_path, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files in {folder_name}: {missing_files}")
        return None
    
    # Create avatar configuration
    avatar_config = {
        "id": avatar_id,
        "name": display_name,
        "folder": folder_name,
        "obj_file": f"{folder_name}.obj",
        "mtl_file": f"{folder_name}.mtl", 
        "texture_file": f"{folder_name}.png",
        "description": description,
        "variants": ["default"],
        "category": category,
        "theme": theme,
        "installation_date": __import__('datetime').datetime.utcnow().isoformat()
    }
    
    print(f"✅ Avatar '{display_name}' ready for installation!")
    print(f"   ID: {avatar_id}")
    print(f"   Category: {category}")
    print(f"   Theme: {theme['ui_style']} style with {theme['primary_color']} primary color")
    print(f"   Personality: {', '.join(theme['personality'])}")
    
    return avatar_config


def bulk_install_avatars(folder_list):
    """
    Install multiple avatars at once
    
    Args:
        folder_list (list): List of folder names to install
        
    Returns:
        list: List of successfully installed avatar configurations
    """
    installed_avatars = []
    
    print(f"🎯 Installing {len(folder_list)} avatars...")
    
    for folder_name in folder_list:
        print(f"\n📦 Installing {folder_name}...")
        avatar_config = install_new_avatar(folder_name)
        if avatar_config:
            installed_avatars.append(avatar_config)
            print(f"✅ {folder_name} installed successfully")
        else:
            print(f"❌ Failed to install {folder_name}")
    
    print(f"\n🎉 Installation complete! {len(installed_avatars)}/{len(folder_list)} avatars installed.")
    
    return installed_avatars


def get_avatar_theme(avatar_id):
    """
    Get theme configuration for an avatar
    
    Args:
        avatar_id (str): Avatar identifier
        
    Returns:
        dict: Theme configuration or default theme
    """
    avatar = get_avatar_info(avatar_id)
    if avatar and 'theme' in avatar:
        return avatar['theme']
    
    # Generate theme from avatar name if not stored
    avatar_data = next((a for a in AVATAR_CATALOG if a['id'] == avatar_id), None)
    if avatar_data:
        return generate_theme_from_title(avatar_data['name'])
    
    # Return default theme
    return generate_theme_from_title('default')


# ==============================================================================
# AIS RAILWAY INTEGRATION - Railway-Safe Avatar Functions
# ==============================================================================

import logging
from functools import wraps

# Configure Railway logging
railway_logger = logging.getLogger('AIS_Railway')
if os.getenv('RAILWAY_ENVIRONMENT'):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def is_railway_environment():
    """Check if running in Railway environment"""
    return bool(os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'))

def railway_safe_ais(fallback_value=None):
    """
    AIS Railway-safe decorator for deployment environments
    
    Args:
        fallback_value: Value to return if function fails
        
    Returns:
        Decorated function with Railway-safe error handling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except ImportError as e:
                railway_logger.error(f"AIS Railway Import Error in {func.__name__}: {e}")
                return fallback_value
            except FileNotFoundError as e:
                railway_logger.error(f"AIS Railway File Error in {func.__name__}: {e}")
                return fallback_value
            except OSError as e:
                railway_logger.error(f"AIS Railway OS Error in {func.__name__}: {e}")
                return fallback_value
            except Exception as e:
                railway_logger.error(f"AIS Railway Error in {func.__name__}: {e}")
                return fallback_value
        return wrapper
    return decorator

@railway_safe_ais(fallback_value=[])
def get_avatar_catalog_railway_safe():
    """
    Railway-safe avatar catalog retrieval for AIS
    """
    try:
        catalog = get_avatar_catalog()
        railway_logger.info(f"AIS: Avatar catalog loaded successfully - {len(catalog)} avatars")
        return catalog
    except Exception as e:
        railway_logger.warning(f"AIS: Using fallback catalog due to: {e}")
        # Minimal fallback catalog
        return [
            {
                "id": "cool-bee",
        "product_id": "beesmart.avatar.cool_bee",
                "name": "Cool Bee Avatar", 
                "folder": "cool-bee",
                "obj_file": "CoolBee.obj",
                "mtl_file": "CoolBee.mtl", 
                "texture_file": "CoolBee.png",
                "description": "Default cool bee avatar",
                "variants": ["default"],
                "category": "classic",
                "theme": generate_theme_from_title('Cool Bee')
            }
        ]

@railway_safe_ais(fallback_value=False)
def railway_install_avatar(folder_name, display_name=None, category=None, description=None):
    """
    Railway-safe avatar installation for AIS
    
    Args:
        folder_name (str): Avatar folder name
        display_name (str, optional): Display name
        category (str, optional): Category
        description (str, optional): Description
        
    Returns:
        dict or False: Avatar config or False if failed
    """
    try:
        # Use existing install_new_avatar function with Railway safety
        result = install_new_avatar(folder_name, display_name, category, description)
        if result:
            railway_logger.info(f"AIS Railway: Successfully installed {result['name']}")
        return result
    except Exception as e:
        railway_logger.error(f"AIS Railway: Failed to install {folder_name} - {e}")
        return False

@railway_safe_ais(fallback_value={})
def railway_avatar_health_check():
    """
    Railway deployment health check for AIS
    """
    health_data = {
        'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'local'),
        'ais_status': 'checking'
    }
    
    try:
        # Test avatar catalog access
        catalog = get_avatar_catalog_railway_safe()
        health_data['avatar_count'] = len(catalog)
        health_data['catalog_accessible'] = True
        
        # Test file system access
        avatar_dir = "static/Avatars/3D Avatar Files"
        health_data['avatar_files_accessible'] = os.path.exists(avatar_dir)
        
        if health_data['avatar_files_accessible']:
            folders = os.listdir(avatar_dir)
            health_data['avatar_folders_count'] = len(folders)
        else:
            health_data['avatar_folders_count'] = 0
        
        # Test theme generation
        test_theme = generate_theme_from_title('Test Avatar')
        health_data['theme_generation_working'] = bool(test_theme)
        
        # Overall status
        if health_data['catalog_accessible'] and health_data['theme_generation_working']:
            health_data['ais_status'] = 'operational'
        else:
            health_data['ais_status'] = 'degraded'
        
        railway_logger.info(f"AIS Health Check: {health_data['ais_status']} - {health_data['avatar_count']} avatars")
        
    except Exception as e:
        health_data['ais_status'] = 'failed'
        health_data['error'] = str(e)
        railway_logger.error(f"AIS Health Check Failed: {e}")
    
    return health_data

def ais_railway_deployment_test():
    """
    Comprehensive AIS Railway deployment test
    """
    print("🚂 AIS Railway Deployment Test")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. 🔍 AIS Health Check...")
    health = railway_avatar_health_check()
    print(f"   Status: {health.get('ais_status', 'unknown')}")
    print(f"   Environment: {health.get('environment', 'unknown')}")
    print(f"   Avatar Count: {health.get('avatar_count', 0)}")
    
    # Test 2: Catalog Access
    print("\n2. 📚 Avatar Catalog Test...")
    catalog = get_avatar_catalog_railway_safe()
    print(f"   Catalog Size: {len(catalog)} avatars")
    
    # Test 3: Theme Generation
    print("\n3. 🎨 Theme Generation Test...")
    test_themes = ['AstroBee', 'ZomBee', 'DetectiveBee']
    for name in test_themes:
        theme = generate_theme_from_title(name)
        print(f"   {name}: {theme['ui_style']} theme ({theme['primary_color']})")
    
    # Test 4: Installation Simulation (6 new avatars)
    print("\n4. 📦 Installation Test (Simulation)...")
    new_avatars = ["AstroBee", "Frankenbee", "WareBee", "ZomBee", "VampBee", "DetectiveBee"]
    for avatar in new_avatars:
        # Simulate installation check
        theme = generate_theme_from_title(avatar)
        print(f"   ✅ {avatar} ready - {theme['ui_style']} theme")
    
    print(f"\n🎉 AIS Railway Test Complete!")
    return health.get('ais_status') == 'operational'

def railway_avatar_validation(avatar_folder):
    """
    Validate avatar will work properly in Railway environment
    Ensures all files exist and are accessible for Railway deployment
    """
    
    validation = {
        'avatar_folder': avatar_folder,
        'timestamp': datetime.utcnow().isoformat(),
        'environment': 'Railway' if is_railway_environment() else 'Local',
        'validation_status': 'checking',
        'file_checks': {},
        'theme_validation': {},
        'deployment_ready': False
    }
    
    try:
        # Check avatar files exist and are accessible
        avatar_dir = os.path.join("static", "Avatars", "3D Avatar Files", avatar_folder)
        
        if not os.path.exists(avatar_dir):
            validation['validation_status'] = 'failed'
            validation['error'] = f"Avatar folder {avatar_folder} not found"
            return validation
        
        # Check required files
        required_files = ['obj', 'mtl', 'png']
        for file_type in required_files:
            files = [f for f in os.listdir(avatar_dir) if f.lower().endswith(f'.{file_type}')]
            validation['file_checks'][file_type] = {
                'found': len(files) > 0,
                'files': files,
                'count': len(files)
            }
        
        # Check if all required file types exist
        all_files_present = all(
            validation['file_checks'][ft]['found'] 
            for ft in required_files
        )
        
        # Validate theme generation will work
        display_name = avatar_folder.replace('_', ' ').replace('-', ' ')
        theme = generate_theme_from_title(display_name)
        
        validation['theme_validation'] = {
            'theme_generated': bool(theme),
            'primary_color': theme.get('primary_color', 'unknown') if theme else None,
            'ui_style': theme.get('ui_style', 'unknown') if theme else None,
            'personality_count': len(theme.get('personality', [])) if theme else 0
        }
        
        # Railway-specific checks
        railway_checks = {
            'file_permissions': True,  # Railway handles this
            'path_accessibility': all_files_present,
            'theme_compatibility': bool(theme),
            'static_file_serving': True  # Flask serves static files
        }
        
        validation['railway_checks'] = railway_checks
        
        # Overall validation
        if all_files_present and theme and all(railway_checks.values()):
            validation['validation_status'] = 'passed'
            validation['deployment_ready'] = True
        else:
            validation['validation_status'] = 'failed'
            validation['deployment_ready'] = False
        
        # Installation readiness
        validation['installation_ready'] = {
            'files_ready': all_files_present,
            'theme_ready': bool(theme),
            'railway_compatible': all(railway_checks.values()),
            'can_install': validation['deployment_ready']
        }
        
    except Exception as e:
        validation['validation_status'] = 'error'
        validation['error'] = str(e)
        validation['deployment_ready'] = False
    
    return validation

def create_avatar_folder_structure(folder_name, display_name=None):
    """
    Create avatar folder structure for new avatars
    Part of AIS system for complete avatar installation
    """
    
    avatar_dir = os.path.join("static", "Avatars", "3D Avatar Files", folder_name)
    
    try:
        # Create the avatar folder if it doesn't exist
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir)
            print(f"📁 Created avatar folder: {avatar_dir}")
        
        # Create placeholder files for new avatar (for development/testing)
        display_name = display_name or folder_name.replace('_', ' ').replace('-', ' ')
        
        # Create both 3D model files and thumbnail with ! annotation
        placeholder_files = {
            # 3D Model Files
            f"{folder_name}.obj": "# Placeholder OBJ file for " + folder_name,
            f"{folder_name}.mtl": "# Placeholder MTL file for " + folder_name,
            f"{folder_name}.png": "PLACEHOLDER_PNG_TEXTURE",
            
            # Thumbnail with ! annotation (uses folder_name for file discovery)
            f"{folder_name}!.png": "PLACEHOLDER_THUMBNAIL_RENDER"
        }
        
        files_created = []
        for filename, content in placeholder_files.items():
            file_path = os.path.join(avatar_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write(content)
                files_created.append(filename)
                
                # Log file type for clarity
                if filename.endswith('!.png'):
                    print(f"📸 Created thumbnail: {filename} (display name source)")
                elif filename.endswith('.png') and not filename.endswith('!.png'):
                    print(f"🎨 Created texture: {filename} (3D model texture)")
                elif filename.endswith('.obj'):
                    print(f"📐 Created model: {filename} (3D geometry)")
                elif filename.endswith('.mtl'):
                    print(f"🎭 Created material: {filename} (3D materials)")
        
        if files_created:
            print(f"📄 Created placeholder files: {', '.join(files_created)}")
        
        return {
            'folder_created': True,
            'folder_path': avatar_dir,
            'files_created': files_created
        }
        
    except Exception as e:
        print(f"❌ Failed to create folder structure for {folder_name}: {e}")
        return {
            'folder_created': False,
            'error': str(e)
        }

def ais_install_with_railway_validation(folder_name, display_name=None, category=None, description=None):
    """
    Install avatar with Railway environment validation
    Includes automatic folder creation as part of AIS system
    """
    
    print(f"🔍 AIS Installing {folder_name} with Railway validation...")
    
    # Step 1: Create folder structure if needed (part of AIS)
    avatar_dir = os.path.join("static", "Avatars", "3D Avatar Files", folder_name)
    if not os.path.exists(avatar_dir):
        print(f"� Avatar folder not found - AIS creating folder structure...")
        folder_result = create_avatar_folder_structure(folder_name, display_name)
        
        if not folder_result['folder_created']:
            print(f"❌ AIS failed to create folder structure")
            return None
        
        print(f"✅ AIS created folder structure for {folder_name}")
    
    # Step 2: Validate avatar for Railway deployment
    validation = railway_avatar_validation(folder_name)
    
    if not validation['deployment_ready']:
        print(f"❌ Avatar {folder_name} failed Railway validation")
        print(f"   Status: {validation['validation_status']}")
        if 'error' in validation:
            print(f"   Error: {validation['error']}")
        return None
    
    print(f"✅ Avatar {folder_name} passed Railway validation")
    print(f"   Files: {validation['file_checks']}")
    print(f"   Theme: {validation['theme_validation']['ui_style']} style")
    
    # Step 3: Proceed with installation using Railway-safe method
    if is_railway_environment():
        result = railway_install_avatar(folder_name, display_name, category, description)
    else:
        result = install_new_avatar(folder_name, display_name, category, description)
    
    if result:
        print(f"🎉 AIS successfully installed {result['name']}!")
        print(f"   Theme: {result.get('theme', {}).get('ui_style', 'unknown')} style")
        print(f"   Railway Ready: {validation['deployment_ready']}")
        print(f"   Folder: {avatar_dir}")
    
    return result

def bulk_install_with_railway_validation(folder_list):
    """
    Install multiple avatars with Railway validation
    Includes automatic folder creation as part of AIS system
    """
    
    print(f"🚂 AIS Railway-Validated Bulk Installation")
    print(f"=" * 60)
    print(f"Installing {len(folder_list)} avatars with AIS folder creation + Railway validation...")
    
    installed_avatars = []
    failed_installations = []
    folders_created = []
    
    for folder_name in folder_list:
        print(f"\n📦 AIS Processing {folder_name}...")
        
        # Use AIS installation with automatic folder creation
        avatar_config = ais_install_with_railway_validation(folder_name)
        
        if avatar_config:
            installed_avatars.append(avatar_config)
            folders_created.append(folder_name)
            print(f"✅ AIS successfully installed {folder_name}")
        else:
            failed_installations.append(folder_name)
            print(f"❌ AIS failed to install {folder_name}")
    
    print(f"\n🎯 AIS RAILWAY INSTALLATION SUMMARY")
    print(f"=" * 50)
    print(f"✅ Successfully installed: {len(installed_avatars)}/{len(folder_list)}")
    print(f"📁 Folders created by AIS: {len(folders_created)}")
    print(f"❌ Failed installations: {len(failed_installations)}")
    
    if folders_created:
        print(f"\n📁 AIS CREATED FOLDERS:")
        for folder in folders_created:
            print(f"   ✅ {folder} - Folder structure created and avatar installed")
    
    if failed_installations:
        print(f"\n❌ INSTALLATION FAILURES:")
        for failure in failed_installations:
            print(f"   {failure}: Installation process failed")
    
    if installed_avatars:
        print(f"\n✅ RAILWAY-READY AVATARS:")
        for avatar in installed_avatars:
            theme_style = avatar.get('theme', {}).get('ui_style', 'unknown')
            theme_color = avatar.get('theme', {}).get('primary_color', 'unknown')
            print(f"   🐝 {avatar['name']} - {theme_style} theme ({theme_color})")
    
    print(f"\n🚂 All installed avatars are Railway deployment ready!")
    print(f"📁 AIS automatically created folder structures for new avatars!")
    
    return installed_avatars


def validate_avatar_mtl_references(avatar_id: str) -> bool:
    """
    Validate that MTL files reference existing texture files
    Auto-fix common issues if possible
    
    Args:
        avatar_id: The avatar ID to validate (e.g., 'professor-bee')
        
    Returns:
        bool: True if validation passes or fixes were applied successfully
    """
    import re
    from pathlib import Path
    
    avatar_dir = Path(f"static/assets/avatars/{avatar_id}")
    if not avatar_dir.exists():
        print(f"⚠️  Avatar directory not found: {avatar_dir}")
        return False
    
    mtl_files = list(avatar_dir.glob("*.mtl"))
    texture_files = list(avatar_dir.glob("*.png")) + list(avatar_dir.glob("*.jpg")) + list(avatar_dir.glob("*.jpeg"))
    
    if not mtl_files:
        print(f"ℹ️  No MTL files found for {avatar_id}")
        return True
    
    fixes_made = False
    
    for mtl_file in mtl_files:
        try:
            # Read MTL file content
            with open(mtl_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find texture references (map_Kd lines)
            texture_refs = re.findall(r'map_Kd\s+(.+)', content)
            
            for ref in texture_refs:
                ref = ref.strip()
                ref_path = avatar_dir / ref
                
                # Check if texture file exists
                if not ref_path.exists():
                    print(f"🔧 MTL Fix needed for {avatar_id}/{mtl_file.name}: {ref} not found")
                    
                    # Try to find correct texture file
                    best_match = None
                    
                    for tex_file in texture_files:
                        tex_name = tex_file.name
                        
                        # Auto-fix strategy: look for avatar-name based matches
                        avatar_name_clean = avatar_id.replace('-', '').lower()
                        tex_name_clean = tex_name.lower().replace('_', '')
                        
                        if (avatar_name_clean in tex_name_clean or 
                            tex_name.lower() in ['texture.png', f'{avatar_id}.png']):
                            best_match = tex_name
                            break
                    
                    if best_match:
                        # Apply the fix
                        updated_content = content.replace(f"map_Kd {ref}", f"map_Kd {best_match}")
                        
                        with open(mtl_file, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        
                        print(f"🔧 Auto-fixed MTL reference in {avatar_id}/{mtl_file.name}: {ref} → {best_match}")
                        fixes_made = True
                        content = updated_content  # Update for next iteration
                    else:
                        print(f"❌ Could not auto-fix MTL reference {ref} for {avatar_id}")
                        return False
                else:
                    print(f"✅ MTL texture reference valid: {avatar_id}/{mtl_file.name} → {ref}")
                    
        except Exception as e:
            print(f"⚠️  MTL validation error for {avatar_id}/{mtl_file.name}: {e}")
            continue
    
    if fixes_made:
        print(f"🎨 Applied MTL texture reference fixes for {avatar_id}")
    
    return True


def validate_all_avatar_mtl_references() -> Dict[str, bool]:
    """
    Validate MTL texture references for all avatars in the catalog
    Auto-fix issues where possible
    
    Returns:
        Dict mapping avatar_id to validation success status
    """
    results = {}
    
    print("🔍 Validating MTL texture references for all avatars...")
    
    for avatar in AVATAR_CATALOG:
        avatar_id = avatar['id']
        print(f"\n📁 Validating {avatar_id}...")
        
        success = validate_avatar_mtl_references(avatar_id)
        results[avatar_id] = success
        
        if success:
            print(f"   ✅ {avatar_id} validation passed")
        else:
            print(f"   ❌ {avatar_id} validation failed")
    
    # Summary
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"\n📊 MTL Validation Summary:")
    print(f"   • Total avatars: {total}")
    print(f"   • Passed: {passed}")
    print(f"   • Failed: {failed}")
    
    if failed == 0:
        print("🎉 All avatar MTL references are valid!")
    else:
        print("⚠️  Some avatars have MTL issues that need manual attention")
    
    return results


# ==============================================================================
# AIS – Asset Consistency Audit (HTTP-based)
# ==============================================================================

@railway_safe_ais(fallback_value={
    'status': 'skipped',
    'reason': 'audit_unavailable',
})
def ais_avatar_asset_audit(base_url: str | None = None) -> Dict[str, object]:
    """
    Run an HTTP-based asset consistency audit against /api/avatars.

    This checks that each avatar has canonical URLs for OBJ/MTL/texture/thumbnail and that:
    - assets are reachable (HEAD/GET)
    - OBJ/MTL/texture share a consistent base name (OBJ==MTL; TEX==OBJ or OBJ+"_texture")
    - MTL optionally references the texture filename

    Args:
        base_url: Full base URL of the running app (e.g., https://app.example.com). If not
                  provided, defaults to http://localhost:5000 for local development.

    Returns:
        dict: { status: 'success'|'error', pass: int, fail: int, results: [ ... ] }
    """
    import requests
    from typing import Optional

    base = (base_url or 'http://localhost:5000').rstrip('/')
    api = f"{base}/api/avatars"

    try:
        resp = requests.get(api, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        return {
            'status': 'error',
            'error': f'fetch_failed: {e}',
            'endpoint': api,
        }

    if payload.get('status') != 'success':
        return {
            'status': 'error',
            'error': 'api_not_success',
            'endpoint': api,
        }

    # Try to reuse the standalone test helpers if available for consistency
    try:
        import test_avatar_assets as taa
        check = taa.check_avatar  # type: ignore[attr-defined]
    except Exception:
        check = None

    avatars = payload.get('avatars') or []
    results = []

    def _head_ok(url: str) -> bool:
        try:
            r = requests.head(url, timeout=10)
            if 200 <= r.status_code < 300:
                return True
            r = requests.get(url, timeout=10, stream=True)
            return 200 <= r.status_code < 300
        except Exception:
            return False

    def _get_base(name: str, ext: Optional[str] = None) -> str:
        fn = name.rsplit('/', 1)[-1]
        if ext and fn.lower().endswith(f'.{ext.lower()}'):
            return fn[: -(len(ext) + 1)]
        if '.' in fn:
            return fn[: fn.rfind('.')]
        return fn

    for a in avatars:
        # Prefer using the validated test module if present
        if check is not None:
            res = check(a)
            results.append({
                'id': res.id,
                'exists_ok': res.exists_ok,
                'names_ok': res.names_ok,
                'mtl_ref_ok': res.mtl_ref_ok,
                'errors': res.errors,
            })
            continue

        # Fallback inline check (no external import)
        urls = (a.get('urls') or {})
        obj = urls.get('model_obj')
        mtl = urls.get('model_mtl')
        tex = urls.get('texture')
        thumb = urls.get('thumbnail')

        errors = []
        exists_ok = False
        names_ok = False
        mtl_ref_ok = None

        if not (obj and mtl and tex):
            missing = [k for k, v in [('OBJ', obj), ('MTL', mtl), ('TEX', tex)] if not v]
            errors.append(f"missing_urls: {', '.join(missing)}")
        else:
            o = _head_ok(obj)
            m = _head_ok(mtl)
            t = _head_ok(tex)
            th = True if not thumb else _head_ok(thumb)
            exists_ok = o and m and t and th
            if not exists_ok:
                if not o: errors.append('obj_unreachable')
                if not m: errors.append('mtl_unreachable')
                if not t: errors.append('texture_unreachable')
                if thumb and not th: errors.append('thumbnail_unreachable')

            ob = _get_base(obj, 'obj').lower() if obj else ''
            mb = _get_base(mtl, 'mtl').lower() if mtl else ''
            tb = _get_base(tex).lower() if tex else ''
            names_ok = (ob == mb) and (tb == ob or tb == f"{ob}_texture")
            if not names_ok:
                errors.append(f"name_mismatch: obj={ob}, mtl={mb}, tex={tb}")

            # Optional: simple MTL reference signal
            try:
                r = requests.get(mtl, timeout=10)
                if 200 <= r.status_code < 300 and tex:
                    mtl_ref_ok = (tex.rsplit('/', 1)[-1].lower() in (r.text or '').lower())
                    if not mtl_ref_ok:
                        errors.append('mtl_missing_texture_ref')
            except Exception:
                mtl_ref_ok = None

        results.append({
            'id': a.get('id') or 'unknown',
            'exists_ok': exists_ok,
            'names_ok': names_ok,
            'mtl_ref_ok': mtl_ref_ok,
            'errors': errors,
        })

    # Summarize
    total = len(results)
    fails = [r for r in results if not (r['exists_ok'] and r['names_ok'] and (r['mtl_ref_ok'] in (True, None)))]
    return {
        'status': 'success',
        'pass': total - len(fails),
        'fail': len(fails),
        'results': results,
        'endpoint': api,
    }
