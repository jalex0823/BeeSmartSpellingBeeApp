"""Selfcheck: premium gating on main menu + avatar default-free locking.

What it checks (no DB required):
- In `templates/unified_menu.html`, specific tiles are marked premium-only and lock when not premium.
- In `AjaSpellBApp.py`, avatar unlock policy treats default_free/mascot_free (and is_default_free) as unlocked,
  and premium/earn_or_buy as locked unless purchased/earned/premium.

This is a static (text-based) check intended to catch regressions in templates/logic.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_text(rel: str) -> str:
    p = REPO_ROOT / rel
    if not p.exists():
        raise SystemExit(f"FAIL: missing file: {rel}")
    return p.read_text(encoding="utf-8", errors="replace")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"FAIL: missing {label}: {needle}")


def main() -> None:
    menu = _read_text("templates/unified_menu.html")
    app = _read_text("AjaSpellBApp.py")

    # ---- Main menu premium locks ----
    # We specifically gate these tiles as premium-only.
    for tile_id in ("tileImageUpload", "tileSavedLists", "tileSpeedRound"):
        assert_contains(menu, f'id="{tile_id}"', f"tile id {tile_id}")

    # Ensure the premium gating attribute exists on those tiles.
    assert_contains(menu, 'data-requires-premium="true"', "premium attribute on tiles")

    # Ensure the class lock condition checks premium as well as auth.
    # (We do a coarse check since the template is large.)
    assert_contains(menu, "_is_premium != 'true'", "premium lock condition")

    # Ensure the shared handler enforces premium.
    assert_contains(menu, "requiresPremium", "shared handler premium flag")
    assert_contains(menu, "!window.IS_PREMIUM", "shared handler premium check")

    # ---- Avatar default-free policy ----
    assert_contains(app, "Default free tiers are unlocked", "avatar policy comment")
    assert_contains(app, "tier in ('default_free', 'mascot_free')", "default free tier unlocking")
    assert_contains(app, "is_default_free", "default free boolean")
    assert_contains(app, "if tier == 'earn_or_buy':", "earn_or_buy policy")
    assert_contains(app, "if tier == 'premium':", "premium policy")

    # ---- Server-side paywall enforcement for premium endpoints ----
    # These checks ensure premium-only features can't be accessed by calling
    # APIs/URLs directly (bypassing the main menu locks).
    assert_contains(app, "def _require_premium_json", "premium enforcement helper")

    # Saved Lists API must be premium-gated.
    assert_contains(app, "@app.route(\"/api/saved-lists\", methods=[\"GET\"])", "saved-lists GET route")
    assert_contains(app, "_require_premium_json(\"saved_lists\")", "saved-lists premium enforcement")

    # Upload API must be premium-gated.
    assert_contains(app, "@app.route(\"/api/upload\", methods=[\"POST\"])", "upload route")
    assert_contains(app, "_require_premium_json(\"upload\")", "upload premium enforcement")

    # OCR/Image upload must be premium-gated.
    assert_contains(app, "@app.route('/api/upload/image', methods=['GET', 'POST'])", "OCR route")
    assert_contains(app, "_require_premium_json(\"image_upload\")", "OCR premium enforcement")

    # Speed Round APIs/pages must be premium-gated.
    assert_contains(app, "@app.route(\"/api/speed-round/start\", methods=[\"POST\"])", "speed-round start route")
    assert_contains(app, "_require_premium_json(\"speed_round\")", "speed-round premium enforcement")

    print("OK: premium menu tiles are gated and avatar default-free policy present")


if __name__ == "__main__":
    main()
