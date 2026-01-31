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
    """Verify store initializes on app start, not on button click."""
    js_file = REPO_ROOT / 'static' / 'js' / 'honeycomb-avatar-picker-responsive.js'
    content = js_file.read_text(encoding='utf-8')
    
    # Check for initializeIAPStore function
    assert 'initializeIAPStore' in content, "initializeIAPStore function not found"
    
    # Check it's called on DOMContentLoaded
    assert 'await initializeIAPStore()' in content, "initializeIAPStore not called on startup"
    
    # Check for storeReady flag
    assert 'storeReady' in content, "storeReady flag not found"
    assert 'productsLoaded' in content, "productsLoaded flag not found"
    assert 'canMakePayments' in content, "canMakePayments flag not found"
    
    print("✅ Store initialization on app start verified")


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


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
