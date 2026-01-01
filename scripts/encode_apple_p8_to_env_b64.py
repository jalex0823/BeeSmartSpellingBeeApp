"""Encode an App Store Connect AuthKey_*.p8 file to a single-line base64 string.

Use-case: DigitalOcean App Platform sometimes fails to save multiline env vars.
Instead of APPLE_PRIVATE_KEY (multiline), you can set APPLE_PRIVATE_KEY_B64.

This script prints ONLY the base64 string (no extra text) for copy/paste.

Example:
  python3 scripts/encode_apple_p8_to_env_b64.py ~/Downloads/AuthKey_XXXXXX.p8
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/encode_apple_p8_to_env_b64.py /path/to/AuthKey_*.p8", file=sys.stderr)
        return 2

    p = Path(sys.argv[1]).expanduser()
    if not p.exists() or not p.is_file():
        print(f"File not found: {p}", file=sys.stderr)
        return 2

    pem = p.read_text(encoding="utf-8")
    b64 = base64.b64encode(pem.encode("utf-8")).decode("ascii")

    # Print only the value for easy paste into DO.
    sys.stdout.write(b64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
