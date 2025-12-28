#!/usr/bin/env python3
"""Export App Store Connect metadata for promoted avatar IAPs.

Apple constraints (per ASC guidance):
- Display Name: <= 30 characters
- Description: <= 45 characters

Important compliance notes:
- Do NOT include pricing/currency in display name or description.
- Keep text plain and user-friendly.
- For avatars in this repo, names must end with " Avatar".

Outputs a CSV you can paste into App Store Connect workflows.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from avatar_catalog import AVATAR_CATALOG


DEFAULT_OUT = REPO_ROOT / "app_store_avatar_iap_metadata.csv"

MAX_DISPLAY_NAME = 30
MAX_DESCRIPTION = 45


_PRICE_LIKE_RE = re.compile(r"\$|\bUSD\b|\bEUR\b|\bGBP\b|\bprice\b|\bpricing\b", re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"\s+")


def _clean_text(s: str) -> str:
    s = (s or "").strip()
    s = s.replace("\u2014", "-")  # em dash
    s = s.replace("\u2013", "-")  # en dash
    s = s.replace("\"", "'")
    s = s.replace("\n", " ")
    s = _WHITESPACE_RE.sub(" ", s).strip()
    # App Store Connect metadata must not include pricing references.
    s = _PRICE_LIKE_RE.sub("", s)
    s = _WHITESPACE_RE.sub(" ", s).strip(" -")
    return s


def _truncate_words(s: str, max_len: int) -> str:
    s = _clean_text(s)
    if len(s) <= max_len:
        return s
    # Try to cut on a word boundary.
    cut = s[: max_len + 1]
    last_space = cut.rfind(" ")
    if last_space >= max_len * 0.6:
        return cut[:last_space].rstrip(" -")
    return s[:max_len].rstrip(" -")


def _make_display_name(base_name: str) -> str:
    base_name = _clean_text(base_name)

    # Ensure Apple naming convention in this repo.
    if not base_name.endswith(" Avatar"):
        base_name = (base_name + " Avatar").strip()

    # Prefer tying to the app name when it fits.
    candidate = f"BeeSmart {base_name}".strip()
    if len(candidate) <= MAX_DISPLAY_NAME:
        return candidate

    # Fall back to plain avatar name.
    return _truncate_words(base_name, MAX_DISPLAY_NAME)


def _make_description(long_desc: str, tier: str) -> str:
    long_desc = _clean_text(long_desc)

    # Use first sentence-ish chunk if possible.
    for sep in (".", "!", "?"):
        if sep in long_desc:
            long_desc = long_desc.split(sep, 1)[0]
            break

    # Keep it benefit-focused, not technical. Avoid tier words like "premium".
    if not long_desc:
        long_desc = "Unlock this avatar for your profile"

    # Remove tier-ish words if they appear.
    long_desc = re.sub(r"\b(premium|tier|sku|product id|iap)\b", "", long_desc, flags=re.IGNORECASE)
    long_desc = _WHITESPACE_RE.sub(" ", long_desc).strip(" -")

    return _truncate_words(long_desc, MAX_DESCRIPTION)


def main() -> int:
    rows: list[dict[str, str]] = []

    for a in AVATAR_CATALOG:
        product_id = (a.get("product_id") or "").strip()
        if not product_id:
            # Skip entries without a product_id.
            continue

        name = a.get("name", "")
        tier = a.get("tier", "")
        desc = a.get("description", "")

        display_name = _make_display_name(name)
        description = _make_description(desc, tier)

        rows.append(
            {
                "product_id": product_id,
                "display_name": display_name,
                "display_name_len": str(len(display_name)),
                "description": description,
                "description_len": str(len(description)),
            }
        )

    out_path = DEFAULT_OUT
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "product_id",
                "display_name",
                "display_name_len",
                "description",
                "description_len",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    # Guardrails: fail if any row exceeds limits.
    bad = [
        r
        for r in rows
        if int(r["display_name_len"]) > MAX_DISPLAY_NAME or int(r["description_len"]) > MAX_DESCRIPTION
    ]
    if bad:
        print(f"❌ Generated {len(rows)} rows but {len(bad)} exceed ASC limits")
        for r in bad[:10]:
            print(
                f"  - {r['product_id']}: name_len={r['display_name_len']} desc_len={r['description_len']}"
            )
        print(f"Output written (but needs fixes): {out_path}")
        return 2

    print(f"✅ Wrote {len(rows)} rows to: {out_path}")
    print(f"   Display Name <= {MAX_DISPLAY_NAME}, Description <= {MAX_DESCRIPTION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
