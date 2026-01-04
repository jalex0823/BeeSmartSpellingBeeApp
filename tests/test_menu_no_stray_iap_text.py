def test_menu_does_not_render_stray_iap_snippet(client):
    """Regression: ensure a JS snippet isn't accidentally rendered as visible text in <head>.

    This happened when a restore-flow comment block was pasted outside of a <script> tag.
    """
    resp = client.get('/app')
    assert resp.status_code == 200

    html = resp.get_data(as_text=True)

    assert 'IMPORTANT: Avoid forcing a full reload on iOS.' not in html
    assert "window.__beesmartForceEntitlementReload('menu_restore_success'" not in html
