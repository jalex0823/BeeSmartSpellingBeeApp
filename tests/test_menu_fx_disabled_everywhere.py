def test_unified_menu_disables_background_and_overlay_fx_everywhere():
    html = open('templates/unified_menu.html', 'r', encoding='utf-8').read()

    # Ensure we force-disable background/overlay FX.
    assert 'window.__beesmartDisableSweepOverlays = true;' in html
    assert 'window.__beesmartDisableLogoFairyDust = true;' in html
    assert "document.documentElement.classList.add('beesmart-no-sweep-overlays');" in html

    # We should NOT be globally disabling background animations anymore.
    assert 'window.__beesmartDisableBackgroundAnimations = true' not in html
    assert "document.documentElement.classList.add('beesmart-no-sweep-overlays', 'beesmart-no-bg-anim')" not in html

    # Floating decor kill-switch may still be present; it's unrelated to the two specific FX.


def test_unified_menu_keeps_button_audio_and_press_fx():
    html = open('templates/unified_menu.html', 'r', encoding='utf-8').read()
    assert "js/button-press-sfx.js" in html
