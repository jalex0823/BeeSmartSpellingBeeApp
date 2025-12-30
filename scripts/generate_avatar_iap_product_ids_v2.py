"""Generate App Store Connect product IDs for avatar IAPs (v2).

User requirement (Dec 2025)
--------------------------
- These are NOT "SKUs"; they are App Store Connect Product IDs.
- Old format example: beesmart.avatar.fairy_bee
- New requirement: create new unique product IDs by appending ".v2"
  to the old product ID: beesmart.avatar.<slug>.v2

This script prints a clean list and can optionally write a text file.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


AVATARS = [
    "Al Bee",
    "Brother Bee",
    "Buda Bee",
    "Builder Bee",
    "Buzz Bee",
    "Cool Bee",
    "Cutie Bee",
    "Detective Bee",
    "Diva Bee",
    "Doc Bee",
    "Explorer Bee",
    "Franken Bee",
    "Gamer Bee",
    "Honey Comb",
    "Inventor Bee",
    "J Rock Bee",
    "Knight Bee",
    "Lumberjack Bee",
    "Mascot Bee",
    "Motor Bee",
    "Nurse Bee",
    "O Bee",
    "Plumber Bee",
    "Professor Bee",
    "Queen Bee",
    "Robo Bee",
    "Rocker Bee",
    "Sea Bee",
    "Selfie Bee",
    "Singer Bee",
    "Space Bee",
    "Super Bee",
    "Techno Bee",
    "Umpire Bee",
    "Vamp Bee",
    "Ware Bee",
    "Xray Bee",
    "Yeti Bee",
    "Zom Bee",
]


def to_old_slug(name: str) -> str:
    """Match the historical beesmart.avatar.<slug> style: lower + underscores."""
    s = name.strip().lower()
    s = s.replace(" ", "_")
    s = s.replace("-", "_")
    s = re.sub(r"[^a-z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def product_id_v2(name: str) -> str:
    return f"beesmart.avatar.{to_old_slug(name)}.v2"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="Optional output file (writes name -> product_id lines)")
    args = ap.parse_args()

    lines = []
    seen = set()

    for n in AVATARS:
        pid = product_id_v2(n)
        if pid in seen:
            raise SystemExit(f"Duplicate pid generated: {pid}")
        seen.add(pid)
        lines.append(f"{n} -> {pid}")

    text = "\n".join(lines) + "\n"
    print(text, end="")

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
