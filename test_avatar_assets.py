"""
Avatar Assets Consistency Test

Checks that /api/avatars returns entries whose OBJ/MTL/texture/thumbnail:
- exist (HTTP 200; tries HEAD then GET)
- have consistent base names (OBJ base == MTL base; texture base == OBJ base or OBJ base + "_texture")
- optionally validates MTL references contain the texture filename

Usage:
  python test_avatar_assets.py --base http://localhost:5000

Environment variables:
  BASE_URL  default http://localhost:5000

Exit codes:
  0 = all checks pass
  1 = one or more failures
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import requests


def _get_base(url: str, ext: Optional[str] = None) -> str:
    name = url.rsplit('/', 1)[-1]
    if ext:
        if name.lower().endswith(f".{ext.lower()}"):
            name = name[: -(len(ext) + 1)]
    else:
        # strip any one extension
        if '.' in name:
            name = name[: name.rfind('.')]
    return name


def _http_ok(url: str, timeout: float = 10.0) -> bool:
    try:
        r = requests.head(url, timeout=timeout)
        if 200 <= r.status_code < 300:
            return True
        # Some servers don’t support HEAD for static; fallback to GET (range small)
        r = requests.get(url, timeout=timeout, stream=True)
        return 200 <= r.status_code < 300
    except requests.RequestException:
        return False


def _fetch_text(url: str, timeout: float = 10.0) -> Optional[str]:
    try:
        r = requests.get(url, timeout=timeout)
        if 200 <= r.status_code < 300:
            return r.text
        return None
    except requests.RequestException:
        return None


@dataclass
class AvatarCheck:
    id: str
    name: str
    obj: str
    mtl: str
    texture: str
    thumbnail: Optional[str] = None
    exists_ok: bool = False
    names_ok: bool = False
    mtl_ref_ok: Optional[bool] = None
    errors: List[str] = field(default_factory=list)


def check_avatar(entry: Dict) -> AvatarCheck:
    aid = entry.get('id') or entry.get('avatar_id') or 'unknown'
    name = entry.get('name') or aid
    urls = entry.get('urls') or {}

    obj = urls.get('model_obj')
    mtl = urls.get('model_mtl')
    texture = urls.get('texture')
    thumb = urls.get('thumbnail')

    result = AvatarCheck(id=aid, name=name, obj=obj, mtl=mtl, texture=texture, thumbnail=thumb)

    # Existence
    missing = [k for k, v in [('OBJ', obj), ('MTL', mtl), ('TEX', texture)] if not v]
    if missing:
        result.errors.append(f"Missing URLs: {', '.join(missing)}")
        return result

    obj_ok = _http_ok(obj)
    mtl_ok = _http_ok(mtl)
    tex_ok = _http_ok(texture)
    thumb_ok = True if not thumb else _http_ok(thumb)
    result.exists_ok = obj_ok and mtl_ok and tex_ok and thumb_ok
    if not result.exists_ok:
        if not obj_ok:
            result.errors.append('OBJ not reachable')
        if not mtl_ok:
            result.errors.append('MTL not reachable')
        if not tex_ok:
            result.errors.append('Texture not reachable')
        if thumb and not thumb_ok:
            result.errors.append('Thumbnail not reachable')

    # Naming consistency
    obj_base = _get_base(obj, 'obj').lower()
    mtl_base = _get_base(mtl, 'mtl').lower()
    tex_base = _get_base(texture).lower()

    names_ok = (obj_base == mtl_base) and (tex_base == obj_base or tex_base == f"{obj_base}_texture")
    result.names_ok = names_ok
    if not names_ok:
        result.errors.append(f"Name mismatch (obj={obj_base}, mtl={mtl_base}, tex={tex_base})")

    # Optional MTL reference check
    mtl_txt = _fetch_text(mtl)
    if mtl_txt:
        # Look for a map_Kd line that includes the texture file name
        tex_file = texture.rsplit('/', 1)[-1]
        result.mtl_ref_ok = tex_file.lower() in mtl_txt.lower()
        if not result.mtl_ref_ok:
            result.errors.append('MTL does not reference texture filename')
    else:
        result.mtl_ref_ok = None

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description='Verify avatar asset consistency via /api/avatars')
    parser.add_argument('--base', dest='base_url', default=os.environ.get('BASE_URL', 'http://localhost:5000'),
                        help='Base URL of the running app (default: %(default)s)')
    args = parser.parse_args()

    base = args.base_url.rstrip('/')
    api = f"{base}/api/avatars"

    print(f"🐝 Fetching avatar catalog: {api}")
    try:
        r = requests.get(api, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"❌ Failed to fetch {api}: {e}")
        return 1

    if data.get('status') != 'success':
        print('❌ API did not return success status')
        return 1

    avatars = data.get('avatars') or []
    print(f"📦 Avatars returned: {len(avatars)}")

    results: List[AvatarCheck] = [check_avatar(a) for a in avatars]

    # Report
    pass_count = sum(1 for r in results if r.exists_ok and r.names_ok and (r.mtl_ref_ok in (True, None)))
    fail = [r for r in results if not (r.exists_ok and r.names_ok and (r.mtl_ref_ok in (True, None)))]

    print("\n===== Avatar Asset Report =====")
    for r in results:
        status = 'PASS' if r in results and r.exists_ok and r.names_ok and (r.mtl_ref_ok in (True, None)) else 'FAIL'
        mtl_ref = 'n/a' if r.mtl_ref_ok is None else ('ok' if r.mtl_ref_ok else 'bad')
        print(f"- {r.id:15} {status:4} | exists={r.exists_ok} names={r.names_ok} mtl_ref={mtl_ref}")
        if r.errors:
            for e in r.errors:
                print(f"    • {e}")

    print("===============================\n")
    print(f"✅ PASS: {pass_count} / {len(results)}  |  ❌ FAIL: {len(fail)}")

    return 0 if not fail else 1


if __name__ == '__main__':
    sys.exit(main())
