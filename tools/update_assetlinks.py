"""
Update static/.well-known/assetlinks.json with your Android package name and SHA-256 certificate fingerprint.

Usage (PowerShell):
  python tools/update_assetlinks.py --package app.beesmartspelling --sha256 "AB:CD:...:EF"

Notes:
- Fingerprint format must be colon-separated uppercase hex (as shown by Play Console or keytool -list -v)
- This script will preserve the overall structure and only replace package_name and sha256_cert_fingerprints[0]
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETLINKS_PATH = ROOT / "static/.well-known/assetlinks.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Update assetlinks.json for Android App Links")
    parser.add_argument("--package", required=True, help="Android package name (e.g. app.beesmartspelling)")
    parser.add_argument("--sha256", required=True, help="SHA-256 certificate fingerprint (colon-separated)")
    args = parser.parse_args()

    if not ASSETLINKS_PATH.exists():
        print(f"ERROR: {ASSETLINKS_PATH} not found.")
        return 1

    try:
        data = json.loads(ASSETLINKS_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, list) or not data:
            raise ValueError("Unexpected assetlinks.json structure: expected non-empty list")

        entry = data[0]
        target = entry.setdefault("target", {})
        target["namespace"] = "android_app"
        target["package_name"] = args.package
        target["sha256_cert_fingerprints"] = [args.sha256]

        ASSETLINKS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {ASSETLINKS_PATH} with package={args.package} and SHA-256 fingerprint.")
        return 0
    except Exception as e:
        print(f"ERROR updating assetlinks.json: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
