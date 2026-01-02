from pathlib import Path


# Be robust to symlinks and odd runner working directories.
# Using the current working directory works in CI and local runs, and avoids
# accidentally reading a different checkout when paths are symlinked.
REPO_ROOT = Path.cwd().resolve()


def _read_text(path: Path) -> str:
    # Use strict UTF-8 here so we don't accidentally mangle strings (emoji, smart quotes)
    # and then fail simple substring asserts on otherwise-correct templates.
    return path.read_text(encoding="utf-8")


def test_buttonpress_sfx_fallback_asset_exists():
    # The optional ButtonPresses folder may or may not be present in a given deploy.
    # The UI must still have a valid click sound to play.
    fallback = REPO_ROOT / "static" / "sounds" / "button-click.mp3"
    assert fallback.exists(), "Expected fallback button click sound: static/sounds/button-click.mp3"


def test_base_wires_global_buttonpress_sfx():
    base = REPO_ROOT / "templates" / "base.html"
    txt = _read_text(base)

    # Verify the stable wiring (the functional contract), not an exact comment string.
    # Ensure the optional playlist endpoint is wired (either directly in the template
    # or via the shared script include).
    assert (
        "/api/button-press-sfx" in txt
        or "js/button-press-sfx.js" in txt
    )

    # Ensure fallback path is referenced somewhere (either inline or in the shared script).
    if "/static/sounds/button-click.mp3" not in txt:
        shared = REPO_ROOT / "static" / "js" / "button-press-sfx.js"
        assert shared.exists(), "Expected shared button SFX script: static/js/button-press-sfx.js"
        shared_txt = _read_text(shared)
        assert "/static/sounds/button-click.mp3" in shared_txt
    # Ensure the global API object exists (used by page soundboards).
    # It may be defined inline or via the shared script.
    if "window.BeeSmartButtonSfx" not in txt:
        shared = REPO_ROOT / "static" / "js" / "button-press-sfx.js"
        assert shared.exists(), "Expected shared button SFX script: static/js/button-press-sfx.js"
        shared_txt = _read_text(shared)
        assert "window.BeeSmartButtonSfx" in shared_txt


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
