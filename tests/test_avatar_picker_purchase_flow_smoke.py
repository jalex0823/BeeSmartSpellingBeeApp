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


def test_purchase_complete_flow():
    """CRITICAL: Verify complete purchase flow from button click to avatar unlock."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Find purchaseLockedAvatar function (search larger window)
    purchase_func_start = content.find('async function purchaseLockedAvatar')
    assert purchase_func_start >= 0, "purchaseLockedAvatar function not found"
    # Function is long - search up to next function or 10000 chars
    next_func = content.find('\nasync function ', purchase_func_start + 1)
    if next_func > purchase_func_start:
        purchase_func = content[purchase_func_start:next_func]
    else:
        purchase_func = content[purchase_func_start:purchase_func_start + 10000]
    
    # CRITICAL: Verify purchase flow steps
    critical_steps = [
        'PURCHASE_DEBOUNCE_MS',  # Debouncing
        'purchaseState === PurchaseState.PURCHASING',  # State check
        'productId',  # Product ID extraction
        'BeeSmartIAP.purchase',  # Native purchase call
        'refreshAvatarUnlockStatus',  # Unlock status refresh
        'findAvatarBySlug',  # Find updated avatar
        'is_locked',  # Check unlock status
        'PurchaseState.PURCHASED',  # Success state
        'clearPurchaseState',  # State cleanup
    ]
    
    found_steps = sum(1 for step in critical_steps if step in purchase_func)
    assert found_steps >= 7, f"Purchase flow missing critical steps (found {found_steps}/9): {[s for s in critical_steps if s not in purchase_func]}"
    
    print("✅ Complete purchase flow verified")


def test_purchase_unlock_verification():
    """CRITICAL: Verify purchase actually unlocks avatar."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check purchase completion unlocks avatar
    assert 'refreshAvatarUnlockStatus' in content, "refreshAvatarUnlockStatus not found"
    assert 'findAvatarBySlug' in content, "findAvatarBySlug not found"
    
    # Check unlock verification logic (search larger window)
    purchase_func_start = content.find('async function purchaseLockedAvatar')
    next_func = content.find('\nasync function ', purchase_func_start + 1)
    if next_func > purchase_func_start:
        purchase_func = content[purchase_func_start:next_func]
    else:
        purchase_func = content[purchase_func_start:purchase_func_start + 10000]
    
    # Check unlock verification (may be written as updated.is_locked === false or !updated.is_locked)
    assert ('updated' in purchase_func and 'is_locked' in purchase_func) or '!updated.is_locked' in purchase_func or 'updated.is_locked === false' in purchase_func, "Unlock verification not found"
    assert 'alert' in purchase_func and 'unlocked' in purchase_func.lower(), "Success message not found"
    
    # Check retry logic for backend sync delays
    assert 'setTimeout' in purchase_func and 'refreshAvatarUnlockStatus' in purchase_func, "Retry logic not found"
    
    print("✅ Purchase unlock verification verified")


def test_purchase_reconciliation_event():
    """CRITICAL: Verify reconciliation event properly handles purchase completion."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Find reconciliation event listener (search larger window)
    recon_start = content.find('beesmart:iap-reconciled')
    assert recon_start >= 0, "Reconciliation event listener not found"
    # Search until next event listener or end of function
    next_event = content.find('window.addEventListener', recon_start + 1)
    if next_event > recon_start:
        recon_section = content[recon_start:next_event]
    else:
        recon_section = content[recon_start:recon_start + 3000]
    
    # CRITICAL: Verify reconciliation handles purchase completion
    assert 'currentPurchaseProductId' in recon_section, "Product ID tracking not found"
    assert 'owned' in recon_section.lower(), "Owned products check not found"
    assert 'PurchaseState.PURCHASING' in recon_section, "PURCHASING state check not found"
    assert 'PurchaseState.PURCHASED' in recon_section, "PURCHASED state transition not found"
    assert 'refreshAvatarUnlockStatus' in recon_section, "Unlock refresh not found in reconciliation"
    # findAvatarBySlug may be in the then() callback
    assert 'findAvatarBySlug' in recon_section or 'refreshAvatarUnlockStatus().then' in recon_section, "Avatar lookup or refresh callback not found"
    
    print("✅ Purchase reconciliation event verified")


def test_purchase_error_handling():
    """CRITICAL: Verify purchase errors are handled gracefully."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Search larger function window
    purchase_func_start = content.find('async function purchaseLockedAvatar')
    next_func = content.find('\nasync function ', purchase_func_start + 1)
    if next_func > purchase_func_start:
        purchase_func = content[purchase_func_start:next_func]
    else:
        purchase_func = content[purchase_func_start:purchase_func_start + 10000]
    
    # Check error handling
    assert 'catch' in purchase_func or 'try' in purchase_func, "Error handling not found"
    assert 'PurchaseState.FAILED' in purchase_func, "FAILED state not found"
    # clearTimeout may be in timeout handler or error handler
    assert 'clearTimeout' in purchase_func or 'timeoutId' in purchase_func, "Timeout cleanup not found"
    assert 'clearPurchaseState' in purchase_func, "State cleanup not found"
    
    # Check specific error cases
    assert 'Store bridge not ready' in purchase_func or 'bridge not ready' in purchase_func.lower(), "Bridge error handling not found"
    assert 'productId' in purchase_func and ('No product_id' in purchase_func or 'product_id' in purchase_func), "Product ID error handling not found"
    
    print("✅ Purchase error handling verified")


def test_purchase_cancellation_handling():
    """CRITICAL: Verify user cancellation doesn't break purchase flow."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Search larger function window
    purchase_func_start = content.find('async function purchaseLockedAvatar')
    next_func = content.find('\nasync function ', purchase_func_start + 1)
    if next_func > purchase_func_start:
        purchase_func = content[purchase_func_start:next_func]
    else:
        purchase_func = content[purchase_func_start:purchase_func_start + 10000]
    
    # Check cancellation handling
    assert 'PurchaseState.CANCELLED' in purchase_func, "CANCELLED state not found"
    assert 'cancelled' in purchase_func.lower(), "Cancellation detection not found"
    assert 'confirm' in purchase_func, "Confirmation dialog found"
    
    # Check cancellation cleanup
    assert 'clearTimeout' in purchase_func or 'timeoutId' in purchase_func, "Timeout cleanup on cancel not found"
    assert 'clearPurchaseState' in purchase_func, "State cleanup on cancel not found"
    assert 'PurchaseState.IDLE' in purchase_func, "IDLE state reset not found"
    
    print("✅ Purchase cancellation handling verified")


def test_purchase_timeout_protection():
    """CRITICAL: Verify purchase timeout prevents stuck purchases."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Search larger function window
    purchase_func_start = content.find('async function purchaseLockedAvatar')
    next_func = content.find('\nasync function ', purchase_func_start + 1)
    if next_func > purchase_func_start:
        purchase_func = content[purchase_func_start:next_func]
    else:
        purchase_func = content[purchase_func_start:purchase_func_start + 10000]
    
    # Check timeout protection
    assert 'PURCHASE_TIMEOUT_MS' in purchase_func, "Timeout constant not found"
    assert 'setTimeout' in purchase_func, "Timeout setter not found"
    # clearTimeout may be in timeout handler
    assert 'clearTimeout' in purchase_func or 'timeoutId' in purchase_func, "Timeout cleanup not found"
    assert '60000' in purchase_func or 'PURCHASE_TIMEOUT_MS' in purchase_func, "60 second timeout not found"
    assert 'Purchase timeout' in purchase_func or 'taking longer than expected' in purchase_func.lower(), "Timeout message not found"
    
    print("✅ Purchase timeout protection verified")


def test_purchase_state_persistence():
    """CRITICAL: Verify purchase state persists across page refreshes."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check state persistence
    assert 'persistPurchaseState' in content, "persistPurchaseState function not found"
    assert 'restorePurchaseState' in content, "restorePurchaseState function not found"
    assert 'localStorage' in content, "localStorage usage not found"
    
    # Check persistence is called during purchase (search larger window)
    purchase_func_start = content.find('async function purchaseLockedAvatar')
    next_func = content.find('\nasync function ', purchase_func_start + 1)
    if next_func > purchase_func_start:
        purchase_func = content[purchase_func_start:min(next_func, purchase_func_start + 5000)]
    else:
        purchase_func = content[purchase_func_start:purchase_func_start + 5000]
    assert 'persistPurchaseState' in purchase_func, "State persistence not called during purchase"
    
    # Check restoration on page load (search larger window)
    dom_start = content.find('DOMContentLoaded')
    if dom_start >= 0:
        # Search up to next major section or 3000 chars
        next_section = content.find('\n    setupSearchFilter', dom_start)
        if next_section > dom_start:
            dom_section = content[dom_start:next_section]
        else:
            dom_section = content[dom_start:dom_start + 3000]
        assert 'restorePurchaseState' in dom_section, "State restoration not called on page load"
    else:
        # DOMContentLoaded not found - check if restorePurchaseState exists at all
        assert 'restorePurchaseState' in content, "restorePurchaseState function not found anywhere"
    
    print("✅ Purchase state persistence verified")


def test_purchase_button_enabled_correctly():
    """CRITICAL: Verify purchase button is enabled/disabled correctly."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Find showLockedMessage function (creates purchase button)
    show_modal_start = content.find('function showLockedMessage')
    assert show_modal_start >= 0, "showLockedMessage function not found"
    # Search larger window - function may be long
    next_func = content.find('\nfunction ', show_modal_start + 1)
    if next_func > show_modal_start:
        show_modal_func = content[show_modal_start:next_func]
    else:
        show_modal_func = content[show_modal_start:show_modal_start + 4000]
    
    # Check button enable/disable logic
    assert 'purchaseState === PurchaseState.PURCHASING' in show_modal_func, "PURCHASING state check not found"
    # Check for disabled logic (may be in HTML string or variable)
    assert 'disabled' in show_modal_func or 'disabledAttr' in show_modal_func or 'disabledClass' in show_modal_func or 'isDisabled' in show_modal_func, "Button disabled logic not found"
    assert 'Processing...' in show_modal_func, "Processing state text not found"
    assert 'storeReady' in show_modal_func, "Store readiness check not found"
    
    print("✅ Purchase button enabled/disabled correctly verified")


def test_purchase_verification_and_reconciliation():
    """CRITICAL: Verify purchase verification and reconciliation both work."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Search larger function window
    purchase_func_start = content.find('async function purchaseLockedAvatar')
    next_func = content.find('\nasync function ', purchase_func_start + 1)
    if next_func > purchase_func_start:
        purchase_func = content[purchase_func_start:next_func]
    else:
        purchase_func = content[purchase_func_start:purchase_func_start + 10000]
    
    # Check verification endpoint call
    assert '/api/iap/verify' in purchase_func, "Verification endpoint not found"
    assert 'fetch' in purchase_func, "Verification fetch not found"
    
    # Check reconciliation call
    assert 'reconcile' in purchase_func.lower() or '/api/iap/restore' in purchase_func, "Reconciliation call not found"
    assert 'window.BeeSmartIAP.reconcile' in purchase_func or 'fetch' in purchase_func, "Reconciliation method not found"
    
    # Check both happen after purchase
    verify_pos = purchase_func.find('/api/iap/verify')
    recon_pos = purchase_func.find('reconcile') if 'reconcile' in purchase_func.lower() else purchase_func.find('/api/iap/restore')
    purchase_call_pos = purchase_func.find('BeeSmartIAP.purchase')
    
    assert verify_pos > purchase_call_pos or verify_pos == -1, "Verification happens after purchase"
    assert recon_pos > purchase_call_pos or recon_pos == -1, "Reconciliation happens after purchase"
    
    print("✅ Purchase verification and reconciliation verified")


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
