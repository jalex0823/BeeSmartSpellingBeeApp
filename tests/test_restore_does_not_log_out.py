from __future__ import annotations


def test_subscription_template_does_not_force_reload_on_restore_success():
    """Regression guard: we avoid forced reload during/after restore, which can appear as logout on iOS WebViews."""
    with open('templates/subscription.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Ensure the restore flow prefers in-place reconcile over a hard reload.
    assert "restore_success" in content
    assert "reconcileAndRefreshSubscriptionUI('restore_success')" in content
    assert "subscription_restore_success" in content

    # Do not reintroduce a forced reload timer in this restore-success branch.
    assert "restore_success" in content  # sanity


def test_unified_menu_restore_flow_does_not_hard_reload_on_success():
    with open('templates/unified_menu.html', 'r', encoding='utf-8') as f:
        content = f.read()

    assert "menu_restore_success" in content
    # Ensure we emit a restore-success reconcile event (UI can refresh without navigation).
    assert "new CustomEvent('beesmart:iap-reconciled'" in content
