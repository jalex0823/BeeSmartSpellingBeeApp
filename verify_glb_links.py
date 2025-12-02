"""
Verify GLB existence and generate model links per avatar.
- Prefers DB-backed streaming route when glb_data exists
- Falls back to local static file under static/assets/avatars/glb_files/

Usage:
  python verify_glb_links.py                 # audit all avatars
  python verify_glb_links.py --slug cool-bee # audit one avatar

Exit code 0 when all avatars have at least one valid source (DB or FS), else 1.
"""
from __future__ import annotations
import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# Lazy imports for app/db so script also works without DB present
def _init_app_and_db():
    try:
        from flask import Flask
        from config import get_config
        from models import db
        app = Flask(__name__)
        app.config.from_object(get_config())
        db.init_app(app)
        return app, db
    except Exception:
        return None, None


def _get_db_avatar(slug: str) -> Optional[Any]:
    try:
        from models import Avatar, db
        return Avatar.query.filter_by(slug=slug).first()
    except Exception:
        return None


def _has_db_glb(slug: str) -> bool:
    try:
        av = _get_db_avatar(slug)
        return bool(av and getattr(av, "glb_data", None))
    except Exception:
        return False


def _fs_glb_path(glb_filename: str) -> Path:
    return Path("static/assets/avatars/glb_files") / glb_filename


def _build_link(slug: str, glb_filename: str, prefer_db: bool) -> str:
    if prefer_db:
        # DB-backed streaming endpoint added in app: /api/avatars/<slug>/glb
        return f"/api/avatars/{slug}/glb"
    # Filesystem fallback
    return f"/static/assets/avatars/glb_files/{glb_filename}"


def audit_avatar(avatar: Dict[str, Any]) -> Dict[str, Any]:
    slug = avatar.get("id") or avatar.get("slug")
    glb_filename = avatar.get("obj_file") or avatar.get("glb_file") or ""

    result = {
        "slug": slug,
        "name": avatar.get("name", slug),
        "glb_filename": glb_filename,
        "db": False,
        "fs": False,
        "link": None,
        "notes": []
    }

    if not slug:
        result["notes"].append("missing slug/id")
        return result

    if not glb_filename:
        result["notes"].append("missing glb filename in catalog (obj_file)")

    # Check DB glb
    prefer_db = False
    try:
        prefer_db = _has_db_glb(slug)
        result["db"] = prefer_db
    except Exception as e:
        result["notes"].append(f"db check error: {e}")

    # Check filesystem glb
    if glb_filename:
        p = _fs_glb_path(glb_filename)
        if p.exists():
            result["fs"] = True
        else:
            result["notes"].append(f"missing file: {p}")

    # Build best link
    if prefer_db:
        result["link"] = _build_link(slug, glb_filename, True)
    elif result["fs"]:
        result["link"] = _build_link(slug, glb_filename, False)
    else:
        result["link"] = None

    return result


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Audit a single avatar by slug/id", default=None)
    args = parser.parse_args(argv)

    app, db = _init_app_and_db()
    if app and db:
        ctx = app.app_context()
        ctx.push()
    else:
        ctx = None

    try:
        from avatar_catalog import get_avatar_catalog
        catalog = get_avatar_catalog()
    except Exception:
        # Fallback: try legacy AVATAR_CATALOG
        try:
            from avatar_catalog import AVATAR_CATALOG as catalog  # type: ignore
        except Exception as e:
            print(f"❌ Unable to load avatar catalog: {e}")
            return 2

    items = catalog
    if args.slug:
        items = [a for a in catalog if a.get("id") == args.slug]
        if not items:
            print(f"❌ Avatar with slug '{args.slug}' not found in catalog")
            return 2

    ok = 0
    missing = 0

    print("\n🐝 GLB Verification & Link Builder")
    print("=" * 60)

    for a in items:
        info = audit_avatar(a)
        slug = info["slug"]
        name = info["name"]
        db_ok = "✅" if info["db"] else "❌"
        fs_ok = "✅" if info["fs"] else "❌"
        link = info["link"] or "(none)"
        print(f"{name:28s} | {slug:18s} | DB {db_ok} | FS {fs_ok}")
        print(f"   ↪ link: {link}")
        if info["notes"]:
            for n in info["notes"]:
                print(f"   • {n}")
        if info["link"]:
            ok += 1
        else:
            missing += 1

    print("\n" + "=" * 60)
    print(f"✅ with link: {ok}")
    print(f"❌ missing   : {missing}")

    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
