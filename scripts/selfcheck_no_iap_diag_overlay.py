"""Selfcheck: ensure no IAP diagnostics overlay UI ships in the iOS wrapper.

Why this exists
- The iOS wrapper can bundle a JS file under `ios/App/App/public/js/`.
- A prior version injected an on-screen overlay:
    "IAP diag\nCapacitor: YES\nPlatform: ...\nPlugin found: YES\nPlugins: ..."
  and/or a visible "IAP Diag" button / hidden gestures.

This script fails fast if those diagnostics strings are present.

Run:
  python3 scripts/selfcheck_no_iap_diag_overlay.py
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CANDIDATES = [
    ROOT / "ios" / "App" / "App" / "public" / "js" / "native-iap-bridge.js",
    ROOT / "static" / "js" / "native-iap-bridge.js",
]

NEEDLES = [
    "IAP diag",
    "IAP Diag",
    "beesmart-iap-diag",
    "beesmart_iap_diag",
    "iap_diag_btn",
    "Capacitor: YES",
    "Plugin found: YES",
]


def main() -> int:
    missing = [p for p in CANDIDATES if not p.exists()]
    if missing:
        print("WARN: some candidate files do not exist:")
        for p in missing:
            print(f"  - {p}")

    checked_any = False
    problems: list[tuple[Path, str]] = []

    for path in CANDIDATES:
        if not path.exists():
            continue
        checked_any = True
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in NEEDLES:
            if needle in text:
                problems.append((path, needle))

    if not checked_any:
        print("ERROR: no candidate JS files found to scan.")
        return 2

    if problems:
        print("ERROR: IAP diagnostics markers found (should be removed for production/TestFlight):")
        for path, needle in problems:
            print(f"  - {path}: contains {needle!r}")
        return 1

    print("OK: no IAP diagnostics overlay markers found in wrapper/static bridge files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
