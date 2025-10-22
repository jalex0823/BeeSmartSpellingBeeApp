# iOS Save Word List Fix

## Issue
"Save word list" is not working on iOS devices (iPhone/iPad Safari).

## Root Causes (Common iOS Safari Issues)

1. **Async/Await with User Gestures**: iOS Safari may lose the "user gesture" context when using `await` before API calls
2. **Modal Z-Index**: iOS Safari sometimes doesn't respect z-index with fixed positioning
3. **Touch Events**: iOS requires specific touch event handling
4. **Promise Timing**: iOS Safari has stricter timing requirements for promises initiated by user actions

## Solution Applied

### Fix 1: Remove async confirmation before save (iOS compatibility)
iOS Safari loses the user gesture context when we `await` the confirmation dialog, causing the subsequent `fetch` call to fail.

**Before:**
```javascript
const confirm = await showBeeConfirm({...});
if (!confirm) return;
// Then do fetch...
```

**After** (iOS-compatible):
```javascript
// Check wordbank immediately without await
fetch('/api/wordbank').then(checkData => {
    // Then show confirmation if needed
    showBeeConfirm({...}).then(confirmed => {
        if (confirmed) {
            // Do save immediately in same event loop
            doSave();
        }
    });
});
```

### Fix 2: Add explicit touch event handlers for iOS
```javascript
saveBtn.addEventListener('touchend', (e) => {
    e.preventDefault();
    saveCurrent();
}, {passive: false});
```

### Fix 3: Add iOS-specific meta tags
```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
```

### Fix 4: Ensure modals work on iOS
```css
.modal {
    -webkit-overflow-scrolling: touch;
    transform: translate3d(0,0,0); /* Force GPU acceleration */
}
```

## Files Modified
- `templates/unified_menu.html` - saveCurrent() function

## Testing Checklist
- [ ] Test on iPhone Safari (iOS 15+)
- [ ] Test on iPad Safari
- [ ] Test with default word list
- [ ] Test with custom uploaded list
- [ ] Verify confirmation dialog appears
- [ ] Verify save completes successfully
- [ ] Check saved list appears in "Your Saved Lists"
