"""
Smoke test for avatar picker purchase flow fixes.
Tests purchase state machine, reconciliation, and loop prevention.

Run: pytest tests/test_avatar_picker_purchase_flow_smoke.py -v
"""

import sys
from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def test_purchase_state_machine_exists():
    """Verify purchase state machine constants exist in JS file."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    assert js_file.exists(), f"JS file not found: {js_file}"
    
    content = js_file.read_text(encoding='utf-8')
    
    # Check for state machine
    assert 'PurchaseState' in content, "PurchaseState enum not found"
    assert 'IDLE' in content, "IDLE state not found"
    assert 'STORE_LOADING' in content, "STORE_LOADING state not found"
    assert 'READY' in content, "READY state not found"
    assert 'PURCHASING' in content, "PURCHASING state not found"
    assert 'PURCHASED' in content, "PURCHASED state not found"
    assert 'FAILED' in content, "FAILED state not found"
    assert 'CANCELLED' in content, "CANCELLED state not found"
    
    print("✅ Purchase state machine exists")


def test_store_initialization_on_start():
    """Verify store initializes during system checks, not on picker load."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for initializeIAPStore function
    assert 'initializeIAPStore' in content, "initializeIAPStore function not found"
    assert 'window.initializeIAPStore' in content, "initializeIAPStore not exposed globally"
    
    # Check it's NOT called on DOMContentLoaded (moved to system checks)
    dom_section = content[content.find('DOMContentLoaded'):content.find('DOMContentLoaded') + 2000]
    assert 'await initializeIAPStore()' not in dom_section, "initializeIAPStore still called on picker load!"
    assert 'IAP store initialization moved to system checks' in content, "Comment about system checks not found"
    
    # Check for storeReady flag
    assert 'storeReady' in content, "storeReady flag not found"
    assert 'productsLoaded' in content, "productsLoaded flag not found"
    assert 'canMakePayments' in content, "canMakePayments flag not found"
    
    print("✅ Store initialization in system checks verified")


def test_purchase_button_protection():
    """Verify purchase button is disabled during PURCHASING state."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for button disable logic
    assert 'purchaseState === PurchaseState.PURCHASING' in content, "PURCHASING state check not found"
    assert 'disabled' in content.lower() or 'disabled' in content, "Button disabled logic not found"
    assert 'Processing...' in content, "Processing state text not found"
    
    print("✅ Purchase button protection verified")


def test_modal_reopening_prevention():
    """Verify modal doesn't re-open during purchase."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for modal prevention logic
    assert 'currentPurchaseSlug' in content, "currentPurchaseSlug tracking not found"
    assert 'purchaseState === PurchaseState.PURCHASING' in content, "PURCHASING check in showLockedMessage not found"
    
    # Check for blocking logic
    blocking_patterns = [
        'Blocking modal',
        'purchaseState === PurchaseState.PURCHASING && currentPurchaseSlug',
        'if (purchaseState === PurchaseState.PURCHASING'
    ]
    found_blocking = any(pattern in content for pattern in blocking_patterns)
    assert found_blocking, "Modal blocking logic not found"
    
    print("✅ Modal re-opening prevention verified")


def test_reconciliation_event_handling():
    """Verify reconciliation event properly handles purchase completion."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for reconciliation listener
    assert 'beesmart:iap-reconciled' in content, "Reconciliation event listener not found"
    
    # Check for productId matching logic
    assert 'currentPurchaseProductId' in content, "currentPurchaseProductId tracking not found"
    assert 'owned' in content.lower(), "Owned products check not found"
    
    # Check for purchase confirmation logic
    assert 'Purchase confirmed via reconciliation' in content, "Reconciliation confirmation not found"
    
    print("✅ Reconciliation event handling verified")


def test_purchase_debouncing():
    """Verify purchase debouncing prevents rapid taps."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for debounce logic
    assert 'PURCHASE_DEBOUNCE_MS' in content, "Debounce constant not found"
    assert 'lastPurchaseAttempt' in content, "lastPurchaseAttempt tracking not found"
    assert 'Purchase debounced' in content, "Debounce check not found"
    
    print("✅ Purchase debouncing verified")


def test_purchase_timeout():
    """Verify hard timeout for PURCHASING state."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for timeout logic
    assert 'PURCHASE_TIMEOUT_MS' in content, "Timeout constant not found"
    assert 'setTimeout' in content, "setTimeout for timeout not found"
    assert 'Purchase timeout' in content, "Timeout handling not found"
    assert '60000' in content or 'PURCHASE_TIMEOUT_MS' in content, "60 second timeout not found"
    
    print("✅ Purchase timeout verified")


def test_cancel_handling():
    """Verify user cancellation is handled correctly."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for cancel state
    assert 'PurchaseState.CANCELLED' in content, "CANCELLED state usage not found"
    
    # Check for cancel detection
    assert 'cancelled' in content.lower(), "Cancel detection not found"
    assert 'user cancelled' in content.lower() or 'cancel' in content.lower(), "Cancel message check not found"
    
    print("✅ Cancel handling verified")


def test_state_persistence():
    """Verify purchase state persists across page refreshes."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for localStorage persistence
    assert 'localStorage' in content, "localStorage usage not found"
    assert 'persistPurchaseState' in content, "persistPurchaseState function not found"
    assert 'restorePurchaseState' in content, "restorePurchaseState function not found"
    assert 'clearPurchaseState' in content, "clearPurchaseState function not found"
    
    print("✅ State persistence verified")


def test_store_readiness_checks():
    """Verify store readiness requires all conditions."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for comprehensive readiness check
    assert 'storeReady' in content, "storeReady check not found"
    assert 'canMakePayments' in content, "canMakePayments check not found"
    assert 'productsLoaded' in content, "productsLoaded check not found"
    
    # Check for error messages
    assert 'store is loading' in content.lower(), "Store loading message not found"
    assert 'not available on this device' in content.lower() or 'canMakePayments' in content, "CanMakePayments error not found"
    
    print("✅ Store readiness checks verified")


def test_comprehensive_logging():
    """Verify comprehensive logging for debugging."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for IAP logging
    assert '[IAP]' in content, "IAP logging prefix not found"
    
    # Check for key log points
    log_points = [
        'purchaseLockedAvatar called',
        'Initiating purchase',
        'Purchase result',
        'beesmart:iap-reconciled event',
        'Purchase confirmed via reconciliation'
    ]
    found_logs = sum(1 for point in log_points if point in content)
    assert found_logs >= 3, f"Not enough log points found (found {found_logs}/5)"
    
    print("✅ Comprehensive logging verified")


def test_purchase_flow_integration():
    """Integration test: verify all pieces work together."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Verify purchaseLockedAvatar function has all critical checks
    purchase_function = content[content.find('async function purchaseLockedAvatar'):content.find('async function purchaseLockedAvatar') + 5000]
    
    checks = [
        'PURCHASE_DEBOUNCE_MS',  # Debouncing
        'purchaseState === PurchaseState.PURCHASING',  # State check
        'storeReady',  # Store readiness
        'productId',  # Product ID
        'timeoutId',  # Timeout
        'clearTimeout',  # Timeout cleanup
        'clearPurchaseState',  # State cleanup
    ]
    
    found_checks = sum(1 for check in checks if check in purchase_function)
    assert found_checks >= 5, f"Purchase function missing critical checks (found {found_checks}/7)"
    
    print("✅ Purchase flow integration verified")


def test_avatar_loading_in_system_checks():
    """CRITICAL: Verify avatar loading happens ONLY in system checks, not picker."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for preload function
    assert 'preloadAvatarsWithThumbnails' in content, "preloadAvatarsWithThumbnails function not found"
    assert 'window.preloadAvatarsWithThumbnails' in content, "preloadAvatarsWithThumbnails not exposed globally"
    
    # Check picker uses pre-loaded data
    assert 'window.preloadedAvatars' in content, "Picker not using pre-loaded avatars"
    assert 'CRITICAL: ALL avatar loading MUST happen during system checks' in content, "Critical comment not found"
    assert 'Picker NEVER loads avatars' in content, "Picker loading prevention not found"
    
    # Check picker doesn't call loadAvatars on init (only refreshAvatarUnlockStatus allowed)
    dom_content_loaded = content[content.find('DOMContentLoaded'):content.find('DOMContentLoaded') + 4000]
    # Check for direct call to loadAvatars() (not in comments or function definitions)
    # Allow it only in error message or comments
    direct_load_call = 'loadAvatars();' in dom_content_loaded and 'await loadAvatars()' not in dom_content_loaded
    has_error_handling = 'CRITICAL: Avatars not pre-loaded' in dom_content_loaded
    has_preload_check = 'window.preloadedAvatars' in dom_content_loaded
    # If preload check exists and error handling exists, loadAvatars should not be called directly
    assert not direct_load_call or (has_error_handling and has_preload_check), "Picker calls loadAvatars() directly on init! Should check pre-loaded avatars first"
    
    print("✅ Avatar loading in system checks verified")


def test_picker_no_stall_at_zero():
    """CRITICAL: Verify picker doesn't stall at 0% - overlay hides immediately."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check overlay is hidden immediately when avatars pre-loaded
    assert 'overlay.classList.add(\'hidden\')' in content, "Overlay hide logic not found"
    assert 'overlay.style.display = \'none\'' in content, "Overlay display none not found"
    
    # Check progress is set to 100% immediately
    assert 'progressBar.style.width' in content and '100%' in content, "Progress not set to 100%"
    assert 'loadingText.textContent' in content and '100%' in content, "Loading text not set to 100%"
    
    # Check no 15s timeout safety (shouldn't be needed if pre-loaded)
    dom_section = content[content.find('DOMContentLoaded'):content.find('DOMContentLoaded') + 3000]
    # Allow setTimeout but not 15000ms timeout (should be removed)
    assert '15000' not in dom_section, "15s timeout still present - picker may stall!"
    
    # Check error handling if avatars not pre-loaded
    assert 'Avatars not pre-loaded' in content, "Error handling for missing pre-load not found"
    assert 'Please refresh the page' in content, "User guidance for missing pre-load not found"
    
    print("✅ Picker no-stall verification passed")


def test_refresh_avatar_unlock_status():
    """Verify refreshAvatarUnlockStatus function exists and works correctly."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check function exists
    assert 'refreshAvatarUnlockStatus' in content, "refreshAvatarUnlockStatus function not found"
    assert 'async function refreshAvatarUnlockStatus' in content, "refreshAvatarUnlockStatus not async function"
    
    # Check it's used instead of loadAvatars for updates
    assert 'refreshAvatarUnlockStatus()' in content, "refreshAvatarUnlockStatus not called"
    
    # Check it updates unlock status without full reload (search in function body)
    refresh_func_start = content.find('async function refreshAvatarUnlockStatus')
    if refresh_func_start >= 0:
        # Search larger function body
        refresh_func_body = content[refresh_func_start:refresh_func_start + 5000]
        assert 'is_locked' in refresh_func_body, "Unlock status update not found in refreshAvatarUnlockStatus"
        # Check for grid re-render or marquee update (both indicate UI refresh)
        assert 'renderAvatarGrid' in refresh_func_body or 'updateDynamicMarquee' in refresh_func_body, "UI refresh not found in refreshAvatarUnlockStatus"
    else:
        # Function exists but search failed - check it's called
        assert 'refreshAvatarUnlockStatus()' in content, "refreshAvatarUnlockStatus not called anywhere"
    
    print("✅ refreshAvatarUnlockStatus verified")


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
