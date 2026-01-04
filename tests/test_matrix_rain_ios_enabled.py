def test_menu_does_not_disable_matrix_rain_on_ios_or_mobile_by_default():
    """Regression: matrix rain should show on iOS Safari + iOS WebView.

    The menu template previously disabled background FX on iOS/mobile.
    We want matrix rain to remain enabled there, while still honoring
    standalone/PWA and prefers-reduced-motion.
    """

    html = open('templates/unified_menu.html', 'r', encoding='utf-8').read()

    # The gating expression should not include iOS/mobile/standalone anymore.
    assert 'const disableBgFx = !!(isIOS || isMobile' not in html

    # Menu now force-disables non-matrix background/overlay FX everywhere.
    assert 'window.__beesmartDisableSweepOverlays = true' in html
    assert 'window.__beesmartDisableLogoFairyDust = true' in html


def test_matrix_rain_still_honors_reduced_motion_and_explicit_kill_switches():
    js = open('static/js/matrix-rain.js', 'r', encoding='utf-8').read()

    # Ensure reduced-motion guard still exists
    assert "prefers-reduced-motion: reduce" in js

    # Ensure we still respect explicit app-level kill switches
    assert "window.__beesmartDisableBackgroundAnimations" in js
    assert "window.__beesmartDisableSweepOverlays" in js
