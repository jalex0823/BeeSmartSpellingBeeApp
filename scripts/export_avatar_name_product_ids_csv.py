#!/usr/bin/env python3
"""Export avatar name -> product_id mapping (with pricing).

Creates a simple CSV for quick copy/paste into App Store Connect workflows.
Columns:
- avatar_name
- product_id
 - price
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from avatar_catalog import AVATAR_CATALOG  # noqa: E402


OUT_PATH = REPO_ROOT / "avatar_name_product_ids.csv"


def main() -> int:
    rows: list[dict[str, str]] = []

    for a in AVATAR_CATALOG:
        name = (a.get("name") or "").strip()
        product_id = (a.get("product_id") or "").strip()
        price = a.get("price", "")
        if not name or not product_id:
            continue
        # Keep price purely numeric (no currency symbol) to avoid any policy issues.
        try:
            price_str = f"{float(price):.2f}" if price != "" else ""
        except Exception:
            price_str = ""

        rows.append({"avatar_name": name, "product_id": product_id, "price": price_str})

    rows.sort(key=lambda r: r["avatar_name"].lower())

    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["avatar_name", "product_id", "price"])
        w.writeheader()
        w.writerows(rows)

    print(f"✅ Wrote {len(rows)} rows to: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
