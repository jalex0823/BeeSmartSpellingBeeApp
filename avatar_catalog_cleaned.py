"""
3D Bee Avatar Catalog - Cleaned Version
Manages the catalog of 11 working bee avatars

Each entry includes folder name and specific file names for obj/mtl/texture
"""

import os
from datetime import datetime
from typing import Dict

# Avatar Catalog: 11 Working Bee Types
# Each entry includes folder name and specific file names for obj/mtl/texture
AVATAR_CATALOG = [
    {
        "id": "al-bee",
        "name": "Al Bee",
        "folder": "al-bee",
        "obj_file": "AlBee.obj",
        "mtl_file": "AlBee.mtl",
        "texture_file": "AlBee.png",
        "description": "Classic bee! Always ready to help with spelling.",
        "variants": ["default"],
        "category": "classic"
    },
    {
        "id": "anxious-bee",
        "name": "Anxious Bee",
        "folder": "anxious-bee",
        "obj_file": "AnxiousBee.obj",
        "mtl_file": "AnxiousBee.mtl",
        "texture_file": "AnxiousBee.png",
        "description": "A little nervous but eager to learn!",
        "variants": ["default"],
        "category": "emotion"
    },
    {
        "id": "diva-bee",
        "name": "Diva Bee",
        "folder": "bee-diva",
        "obj_file": "DivaBee.obj",
        "mtl_file": "DivaBee.mtl",
        "texture_file": "Bee_Diva_1018233351.png",
        "description": "Glamorous and fabulous! Star of the hive.",
        "variants": ["default"],
        "category": "entertainment"
    },
    {
        "id": "doctor-bee",
        "name": "Doctor Bee",
        "folder": "doctor-bee",
        "obj_file": "DoctorBee.obj",
        "mtl_file": "DoctorBee.mtl",
        "texture_file": "Bee_Doctor_1018225148.png",
        "description": "Here to heal and help! Medical professional bee.",
        "variants": ["default"],
        "category": "profession"
    },
    {
        "id": "mascot-bee",
        "name": "Mascot Bee",
        "folder": "mascot-bee",
        "obj_file": "MascotBee.obj",
        "mtl_file": "MascotBee.mtl",
        "texture_file": "MascotBee.png",
        "description": "The original BeeSmart mascot! Cheerful and encouraging.",
        "variants": ["default"],
        "category": "classic"
    },
    {
        "id": "monster-bee",
        "name": "Monster Bee",
        "folder": "monster-bee",
        "obj_file": "MonsterBee.obj",
        "mtl_file": "MonsterBee.mtl",
        "texture_file": "MonsterBee.png",
        "description": "Not scary, just misunderstood! Friendly monster bee.",
        "variants": ["default"],
        "category": "fantasy"
    },
    {
        "id": "professor-bee",
        "name": "Professor Bee",
        "folder": "professor-bee",
        "obj_file": "ProfessorBee.obj",
        "mtl_file": "ProfessorBee.mtl",
        "texture_file": "ProfessorBee.png",
        "description": "Wise and knowledgeable! The scholarly bee.",
        "variants": ["default"],
        "category": "profession"
    },
    {
        "id": "rocker-bee",
        "name": "Rocker Bee",
        "folder": "rocker-bee",
        "obj_file": "RockerBee.obj",
        "mtl_file": "RockerBee.mtl",
        "texture_file": "RockerBee.png",
        "description": "Rock and roll! Music-loving bee with attitude.",
        "variants": ["default"],
        "category": "entertainment"
    },
    {
        "id": "vamp-bee",
        "name": "Vamp Bee",
        "folder": "vamp-bee",
        "obj_file": "VampBee.obj",
        "mtl_file": "VampBee.mtl",
        "texture_file": "VampBee.png",
        "description": "Spooky vampire bee! Perfect for Halloween.",
        "variants": ["default"],
        "category": "fantasy"
    },
    {
        "id": "ware-bee",
        "name": "Ware Bee",
        "folder": "ware-bee",
        "obj_file": "WareBee.obj",
        "mtl_file": "WareBee.mtl",
        "texture_file": "WareBee.png",
        "description": "Howling good at spelling! Werewolf bee.",
        "variants": ["default"],
        "category": "fantasy"
    },
    {
        "id": "zom-bee",
        "name": "Zom Bee",
        "folder": "zom-bee",
        "obj_file": "ZomBee.obj",
        "mtl_file": "ZomBee.mtl",
        "texture_file": "ZomBee.png",
        "description": "Brainy zombie bee! Loves learning words.",
        "variants": ["default"],
        "category": "fantasy"
    }
]


def get_avatar_by_id(avatar_id: str) -> Dict:
    """Get avatar configuration by ID"""
    for avatar in AVATAR_CATALOG:
        if avatar["id"] == avatar_id:
            return avatar
    return None


def get_all_avatars() -> list:
    """Get all available avatars"""
    return AVATAR_CATALOG


def get_avatar_count() -> int:
    """Get total number of avatars"""
    return len(AVATAR_CATALOG)


def get_avatars_by_category(category: str) -> list:
    """Get avatars filtered by category"""
    return [a for a in AVATAR_CATALOG if a.get("category") == category]


if __name__ == "__main__":
    print(f"Avatar Catalog: {get_avatar_count()} avatars available")
    for avatar in AVATAR_CATALOG:
        print(f"  - {avatar['id']}: {avatar['name']}")
