from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_buttonpress_sfx_fallback_asset_exists():
    # The optional ButtonPresses folder may or may not be present in a given deploy.
    # The UI must still have a valid click sound to play.
    fallback = REPO_ROOT / "static" / "sounds" / "button-click.mp3"
    assert fallback.exists(), "Expected fallback button click sound: static/sounds/button-click.mp3"


def test_base_wires_global_buttonpress_sfx():
    base = REPO_ROOT / "templates" / "base.html"
    txt = _read_text(base)

    assert "Global randomized button press SFX" in txt
    # Ensure the optional playlist endpoint is wired
    assert "/api/button-press-sfx" in txt
    # Ensure fallback path is referenced
    assert "/static/sounds/button-click.mp3" in txt
    # Ensure the global API object exists (used by page soundboards)
    assert "window.BeeSmartButtonSfx" in txt


def test_restore_modals_have_extended_timing():
    sub = REPO_ROOT / "templates" / "subscription.html"
    menu = REPO_ROOT / "templates" / "unified_menu.html"

    sub_txt = _read_text(sub)
    menu_txt = _read_text(menu)

    # Subscription page: success flow reload is now longer
    assert "setTimeout(() => { try { window.location.reload();" in sub_txt
    assert ", 3200);" in sub_txt, "Expected 3200ms reload delay in subscription.html"

    # Menu page: restore flow reload and modal auto-reload default increased
    assert "autoReloadMs" in menu_txt
    assert "3200" in menu_txt, "Expected 3200ms timing in unified_menu.html"


def test_speed_round_results_has_crest_logo():
    page = REPO_ROOT / "templates" / "speed_round_results.html"
    txt = _read_text(page)

    assert "BeeSmartCrestLogo1.png" in txt
    assert "crest-logo" in txt
