#!/usr/bin/env python3
"""
Test script to verify the Restore Purchases UI improvements:
1. Button has ID for scrolling
2. Button has hover effects
3. Dialog shows properly with scroll
"""

import re

def test_restore_button():
    """Test that restore button has proper ID and hover effects."""
    with open('templates/subscription.html', 'r') as f:
        content = f.read()
    
    # Check for button ID
    assert 'id="restorePurchasesBtn"' in content, "❌ Button missing ID 'restorePurchasesBtn'"
    print("✅ Restore button has ID for scrolling")
    
    # Check for hover effects
    assert 'onmouseover=' in content and 'onmouseout=' in content, "❌ Button missing hover effects"
    print("✅ Restore button has hover effects")
    
    # Check button has transition
    assert 'transition: all 0.3s ease' in content or 'transition:all 0.3s ease' in content, "❌ Button missing transition"
    print("✅ Restore button has smooth transitions")

def test_restore_function():
    """Test that restore function scrolls button into view."""
    with open('templates/subscription.html', 'r') as f:
        content = f.read()
    
    # Check for scroll functionality
    assert 'scrollIntoView' in content, "❌ Missing scrollIntoView in restore function"
    print("✅ Restore function includes scrollIntoView")
    
    # Check for visual feedback
    assert 'Restoring...' in content, "❌ Missing 'Restoring...' feedback text"
    print("✅ Restore function shows 'Restoring...' feedback")
    
    # Check button is disabled during restore
    assert '.disabled = true' in content, "❌ Button not disabled during restore"
    print("✅ Button is disabled during restore operation")
    
    # Check button is re-enabled after restore
    assert '.disabled = false' in content, "❌ Button not re-enabled after restore"
    print("✅ Button is re-enabled after restore completes")

def test_restore_dialog():
    """Test that restore dialog exists and scrolls into view."""
    with open('templates/subscription.html', 'r') as f:
        content = f.read()
    
    # Check for dialog function
    assert 'function showRestoreDialog' in content, "❌ Missing showRestoreDialog function"
    print("✅ showRestoreDialog function exists")
    
    # Check dialog scrolls into view
    dialog_scroll_pattern = r'dialog\.scrollIntoView'
    assert re.search(dialog_scroll_pattern, content), "❌ Dialog doesn't scroll into view"
    print("✅ Dialog scrolls into view when shown")
    
    # Check for animations
    assert '@keyframes fadeIn' in content, "❌ Missing fadeIn animation"
    assert '@keyframes slideUp' in content, "❌ Missing slideUp animation"
    print("✅ Dialog has smooth animations")

def test_restore_states():
    """Test that restore function handles all states properly."""
    with open('templates/subscription.html', 'r') as f:
        content = f.read()
    
    # Check for success state
    assert 'Restore Successful' in content or 'Successfully restored' in content, "❌ Missing success state"
    print("✅ Restore handles success state")
    
    # Check for failure state
    assert 'Restore Failed' in content or 'Could not restore' in content, "❌ Missing failure state"
    print("✅ Restore handles failure state")
    
    # Check for no purchases state
    assert 'No Purchases Found' in content or 'No previous purchases' in content, "❌ Missing no purchases state"
    print("✅ Restore handles no purchases state")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("TESTING RESTORE PURCHASES UI IMPROVEMENTS")
    print("="*60 + "\n")
    
    try:
        test_restore_button()
        print()
        test_restore_function()
        print()
        test_restore_dialog()
        print()
        test_restore_states()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nKey improvements:")
        print("  • Button scrolls into view when clicked")
        print("  • Visual feedback during restore ('Restoring...')")
        print("  • Dialog scrolls into center view")
        print("  • Smooth animations and transitions")
        print("  • Proper error handling with friendly dialogs")
        print("  • Button disabled during operation to prevent double-clicks")
        print("\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        exit(1)
