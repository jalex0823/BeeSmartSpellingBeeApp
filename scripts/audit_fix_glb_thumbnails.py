#!/usr/bin/env python3
"""
Audit and optionally fix GLB thumbnail filenames to strict mapping:
- For every GLB at static/assets/avatars/glb_files/<Base>.glb
- The thumbnail must exist: static/assets/avatars/glb_files/AvatarThumbnails/<Base>!.png (exact case)

Usage:
  python scripts/audit_fix_glb_thumbnails.py           # audit only
  python scripts/audit_fix_glb_thumbnails.py --apply   # apply safe renames when an unambiguous match exists

Notes:
- On Windows, a case-only rename requires a two-step rename via a temp name.
- We DO NOT invent thumbnails. If missing completely, we report and skip.
"""
import argparse
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLB_DIR = ROOT / 'static' / 'assets' / 'avatars' / 'glb_files'
THUMB_DIR = GLB_DIR / 'AvatarThumbnails'

def norm(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def two_step_rename(src: Path, dst: Path):
    """Perform a case-sensitive rename safely across platforms."""
    if src.resolve() == dst.resolve():
        return
    temp = src.with_name(src.stem + '.__tmp__' + src.suffix)
    src.rename(temp)
    temp.rename(dst)


def main(apply: bool):
    if not GLB_DIR.is_dir():
        print(f"❌ GLB directory not found: {GLB_DIR}")
        return 2
    THUMB_DIR.mkdir(parents=True, exist_ok=True)

    glbs = [p for p in GLB_DIR.iterdir() if p.suffix.lower() == '.glb']
    print(f"🔎 Found {len(glbs)} GLB files")

    missing = []
    fixed = []
    ambiguous = []

    # Index thumbnails by relaxed keys to suggest matches
    thumbs = [p for p in THUMB_DIR.iterdir() if p.suffix.lower() == '.png']
    by_norm = {}
    for t in thumbs:
        key = norm(t.stem.replace('!', ''))
        by_norm.setdefault(key, []).append(t)

    for glb in glbs:
        base = glb.stem
        expected = THUMB_DIR / f"{base}!.png"
        if expected.exists():
            continue
        # Suggest candidates by normalized name
        key = norm(base)
        cands = by_norm.get(key, [])
        if not cands:
            missing.append((glb, expected))
            print(f"❌ MISSING thumbnail: {glb.name} -> {expected.name}")
            continue
        if len(cands) > 1:
            ambiguous.append((glb, cands))
            print(f"⚠️ AMBIGUOUS: {glb.name} -> {[c.name for c in cands]}")
            continue
        cand = cands[0]
        print(f"➡️  SUGGEST rename: {cand.name} -> {expected.name}")
        if apply:
            try:
                two_step_rename(cand, expected)
                fixed.append((cand, expected))
                print(f"✅ Renamed {cand.name} -> {expected.name}")
            except Exception as e:
                print(f"❌ Rename failed {cand} -> {expected}: {e}")

    print("\nSummary:")
    print(f"  Fixed: {len(fixed)}")
    print(f"  Missing: {len(missing)}")
    print(f"  Ambiguous: {len(ambiguous)}")
    return 0

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Perform renames when a unique match exists')
    args = ap.parse_args()
    raise SystemExit(main(args.apply))
