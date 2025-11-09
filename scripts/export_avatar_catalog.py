"""Export current effective avatar catalog to JSON.
Safe operation: does not modify existing python catalog — only writes data/avatar_catalog.json.
Usage:
  python scripts/export_avatar_catalog.py
Optionally set USE_EXTERNAL_AVATAR_CATALOG=1 afterward to consume it.
"""
from __future__ import annotations
import os
from pathlib import Path


def main():
    from avatar_catalog import export_avatar_catalog_json, _CATALOG_SOURCE  # type: ignore
    out = export_avatar_catalog_json()
    print(f"Catalog source was: {_CATALOG_SOURCE}")
    print(f"Wrote: {out}")
    print("Set USE_EXTERNAL_AVATAR_CATALOG=1 to enable external JSON loading.")


if __name__ == "__main__":
    main()
