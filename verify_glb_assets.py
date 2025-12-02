"""
Verify GLB existence for all avatars and compute the correct link to use.
- Prefers DB-backed link if glb_data exists for the avatar
- Otherwise falls back to static file under static/assets/avatars/glb_files/
- Writes a JSON mapping to data/avatar_glb_links.json for inspection
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

from flask import Flask

try:
    from config import get_config
    from models import db, Avatar
except Exception:
    get_config = None  # type: ignore
    db = None  # type: ignore
    Avatar = None  # type: ignore

from avatar_catalog import get_avatar_catalog

ROOT = Path(__file__).parent
STATIC_GLB_DIR = ROOT / "static" / "assets" / "avatars" / "glb_files"
OUTPUT_JSON = ROOT / "data" / "avatar_glb_links.json"


def file_exists_rel(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def build_static_url(rel_path: str) -> str:
    # rel_path like "static/assets/avatars/glb_files/CoolBee.glb"
    return "/" + rel_path.replace("\\", "/").lstrip("/")


def init_db_if_possible(app: Flask) -> None:
    global db
    if get_config is None or db is None:
        return
    app.config.from_object(get_config())
    db.init_app(app)


def has_db_glb(app: Flask, slug: str) -> bool:
    if db is None or Avatar is None:
        return False
    with app.app_context():
        try:
            av = Avatar.query.filter_by(slug=slug).first()
            return bool(av and getattr(av, "glb_data", None))
        except Exception:
            return False


def main() -> int:
    print("\n🐝 Verifying GLB existence and links")
    print("=" * 60)

    app = Flask(__name__)
    try:
        init_db_if_possible(app)
    except Exception as e:
        print(f"⚠️ DB init skipped: {e}")

    catalog = get_avatar_catalog()
    results: Dict[str, Dict[str, Any]] = {}

    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "data").mkdir(parents=True, exist_ok=True)

    missing: list[str] = []
    db_backed: list[str] = []
    disk_backed: list[str] = []

    for entry in catalog:
        avatar_id = entry.get("id")
        glb_file = entry.get("obj_file") or entry.get("glb_file") or ""
        slug = avatar_id
        if not avatar_id or not glb_file:
            continue

        # Candidate disk locations (prefer glb_files centralized folder)
        disk_rel_candidates = [
            f"static/assets/avatars/glb_files/{glb_file}",
            f"static/assets/avatars/{avatar_id}/{glb_file}",
        ]
        found_disk_rel = next((p for p in disk_rel_candidates if file_exists_rel(p)), None)

        # DB check
        db_ok = has_db_glb(app, slug)

        # Decide link
        if db_ok:
            link = f"/api/avatars/{slug}/glb"  # requires API route; otherwise use static fallback
            db_backed.append(slug)
        elif found_disk_rel:
            link = build_static_url(found_disk_rel)
            disk_backed.append(slug)
        else:
            link = ""
            missing.append(slug)

        results[slug] = {
            "name": entry.get("name", slug),
            "glb_file": glb_file,
            "db": db_ok,
            "disk": bool(found_disk_rel),
            "disk_path": found_disk_rel or "",
            "link": link,
        }

    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Wrote link map: {OUTPUT_JSON}")
    print(f"   DB-backed:   {len(db_backed)}")
    print(f"   Disk-backed: {len(disk_backed)}")
    print(f"   Missing:     {len(missing)}")
    if missing:
        print("\n❌ Missing avatars (no DB and no file):")
        for m in missing:
            print(f"   - {m}")

    # Show a few examples
    print("\n🔗 Sample links:")
    shown = 0
    for k, v in results.items():
        if v["link"]:
            print(f"   {k:15s} → {v['link']}")
            shown += 1
            if shown >= 8:
                break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
