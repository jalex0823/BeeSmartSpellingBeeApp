"""Self-check: Verify iOS wrapper is Version 40 / Build 40.

This script is intentionally lightweight and does not require Xcode.
It only inspects the Xcode project file and ensures the Info.plist
uses the MARKETING_VERSION/CURRENT_PROJECT_VERSION placeholders.

Usage:
  python3 scripts/selfcheck_ios_version_40_40.py
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import NoReturn

ROOT = Path(__file__).resolve().parents[1]
PBXPROJ = ROOT / "mobile/ios/App/App.xcodeproj/project.pbxproj"
INFO_PLIST = ROOT / "mobile/ios/App/App/Info.plist"


def _fail(msg: str) -> NoReturn:
    print(f"❌ {msg}")
    raise SystemExit(1)


def main() -> None:
    if not PBXPROJ.exists():
        _fail(f"Missing {PBXPROJ}")
    if not INFO_PLIST.exists():
        _fail(f"Missing {INFO_PLIST}")

    pbx = PBXPROJ.read_text(encoding="utf-8", errors="replace")

    marketing = re.findall(r"\bMARKETING_VERSION\s*=\s*([^;]+);", pbx)
    build = re.findall(r"\bCURRENT_PROJECT_VERSION\s*=\s*([^;]+);", pbx)

    if not marketing:
        _fail("MARKETING_VERSION not found in project.pbxproj")
    if not build:
        _fail("CURRENT_PROJECT_VERSION not found in project.pbxproj")

    marketing_vals = {v.strip() for v in marketing}
    build_vals = {v.strip() for v in build}

    # Expect all configurations to be aligned to 40.
    if marketing_vals != {"40"}:
        _fail(f"MARKETING_VERSION not uniformly 40 (found: {sorted(marketing_vals)})")
    if build_vals != {"40"}:
        _fail(f"CURRENT_PROJECT_VERSION not uniformly 40 (found: {sorted(build_vals)})")

    plist = INFO_PLIST.read_text(encoding="utf-8", errors="replace")
    if "$(MARKETING_VERSION)" not in plist:
        _fail("Info.plist does not contain $(MARKETING_VERSION)")
    if "$(CURRENT_PROJECT_VERSION)" not in plist:
        _fail("Info.plist does not contain $(CURRENT_PROJECT_VERSION)")

    print("✅ iOS wrapper version OK: MARKETING_VERSION=40, CURRENT_PROJECT_VERSION=40")


if __name__ == "__main__":
    main()
