# Apple App Store Rejection Fixes - Team Update Breakdown

**Date**: January 12, 2026  
**Purpose**: Summary of code changes for freelance team handling App Store submission  
**Status**: Code changes complete - New Xcode build required

---

## 🎯 Overview

This document outlines all code changes made to address Apple's App Store rejection. **A new Xcode build is REQUIRED** because we modified `Info.plist`, which requires rebuilding the iOS app.

---

## 📋 Apple Rejection Issues Addressed

### Issue 1: Unjustified Background Audio ✅ FIXED
**Problem**: App declared `UIBackgroundModes` with `audio`, but doesn't actually play audio in background.

**Fix Applied**: Removed background audio declaration from `Info.plist`

### Issue 2: IAPs Difficult to Locate ✅ FIXED
**Problem**: Reviewers couldn't find the avatar shop/IAP purchase interface.

**Fix Applied**: Added prominent "Avatars" tile to main menu

### Issue 3: Placeholder App Icons ⚠️ ACTION REQUIRED
**Problem**: App uses placeholder icons instead of BeeSmart branding.

**Status**: **NOT FIXED IN CODE** - Requires manual asset replacement (see below)

### Issue 4: In-App Purchase Flow ⚠️ VERIFICATION REQUIRED
**Problem**: Reviewers couldn't trigger purchases.

**Status**: Code verified correct - Requires App Store Connect configuration check

### Issue 5: Stretched iPad Screenshots ⚠️ ACTION REQUIRED
**Problem**: iPad screenshots appear to be stretched iPhone screens.

**Status**: **NOT FIXED** - Requires new screenshots (see below)

---

## 📝 Code Changes Made

### 1. iOS Info.plist Update ✅
**File**: `mobile/ios/App/App/Info.plist`

**Change**: Removed `UIBackgroundModes` audio declaration

**Before**:
```xml
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array>
```

**After**:
```xml
<!-- UIBackgroundModes removed: app does not play audio in background -->
<!-- <key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array> -->
```

**Impact**: ✅ **REQUIRES NEW XCODE BUILD** - Info.plist changes require rebuild

---

### 2. Main Menu - Avatars Tile Added ✅
**File**: `templates/unified_menu.html`

**Changes Made**:

#### A. Added Avatars Menu Tile (Line ~5157)
```html
<!-- Avatars Shop - Clear entry point for IAP purchases -->
<div id="tileAvatars" class="menu-option theme-gold" 
     onclick="kidSounds.playRandomEffect(); selectOption('avatars', this)" 
     onmouseover="kidSounds.playHappyDing()" 
     title="Browse and unlock adorable bee avatars! Purchase new characters to customize your spelling experience.">
    <div class="option-icon">🐝</div>
    <div class="option-title">Avatars</div>
    <div class="option-description">Browse & unlock bee characters</div>
    <div class="kid-tip">Collect all the bees! 🍯</div>
</div>
```

**Location**: Between "Dictionary Search" and "Saved Word Lists" tiles

#### B. Added CSS Theme Class (Line ~2198)
```css
.menu-option.theme-gold {
    --tile-bg: linear-gradient(135deg, #FFD700 0%, #FFA500 45%, #FF8C00 100%);
    --tile-border: rgba(255, 255, 255, 0.7);
    --tile-shadow: rgba(255, 165, 0, 0.35);
    --tile-hover-shadow: rgba(255, 165, 0, 0.55);
    --tile-text: #5A2C15;
}
```

#### C. Added Navigation Handler (Line ~7116)
```javascript
case 'avatars':
    // Navigate to avatar picker/shop - clear entry point for IAP purchases
    window.location.href = '/honeycomb-picker';
    break;
```

#### D. Added to Option Selector Map (Line ~7082)
```javascript
avatars: '.menu-option[onclick*="avatars"]',
```

**Impact**: ✅ **NO BUILD REQUIRED** - Web template changes, works immediately after server deploy

---

### 3. Smoke Test Fixes ✅
**Files**: 
- `smoke_test.py`
- `smoke_test_quiz_flow.py`
- `smoke_test_import_to_report_card.py`

**Change**: Added UTF-8 console encoding fixes for Windows compatibility

**Impact**: ✅ **NO BUILD REQUIRED** - Development/testing only

---

## 🔨 Action Items for Freelance Team

### ✅ COMPLETED (No Action Needed)
- [x] Info.plist background audio removed
- [x] Avatars tile added to main menu
- [x] CSS styling added
- [x] Navigation handler implemented
- [x] Code committed and pushed to repository

### ⚠️ REQUIRES TEAM ACTION

#### 1. Create New Xcode Build (CRITICAL)
**Why**: `Info.plist` changes require a new iOS build

**Steps**:
1. **Pull latest code**:
   ```bash
   cd mobile
   git pull origin main
   ```

2. **Open in Xcode**:
   ```bash
   npx cap sync ios
   cd ios/App
   open App.xcworkspace
   ```

3. **Verify Info.plist**:
   - Open `App/App/Info.plist` in Xcode
   - Confirm `UIBackgroundModes` is commented out/removed
   - Verify no syntax errors

4. **Increment Build Number**:
   - In Xcode: Select project → General tab
   - Increment "Build" number (e.g., if current is 1, make it 2)
   - Keep "Version" the same unless you're doing a version bump

5. **Create Archive**:
   - Select "Any iOS Device (arm64)" (NOT simulator)
   - Product → Archive
   - Wait for archive to complete

6. **Upload to App Store Connect**:
   - Click "Distribute App"
   - Select "App Store Connect"
   - Follow upload wizard
   - Wait for processing (5-15 minutes)

**Expected Result**: New build appears in App Store Connect TestFlight section

---

#### 2. Replace App Icons (CRITICAL)
**Why**: Apple rejected placeholder icons

**Location**: `mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/`

**Required Sizes** (ALL must be replaced):
- `Icon-App-1024x1024@1x.png` (1024×1024) - **CRITICAL**
- `Icon-App-60x60@2x.png` (120×120)
- `Icon-App-60x60@3x.png` (180×180)
- `Icon-App-40x40@2x.png` (80×80)
- `Icon-App-40x40@3x.png` (120×120)
- `Icon-App-29x29@2x.png` (58×58)
- `Icon-App-29x29@3x.png` (87×87)
- `Icon-App-20x20@2x.png` (40×40)
- `Icon-App-20x20@3x.png` (60×60)
- iPad: `Icon-App-76x76@1x.png`, `Icon-App-76x76@2x.png`, `Icon-App-83.5x83.5@2x.png`

**Steps**:
1. Design/create 1024×1024 master icon (PNG, no transparency, square)
2. Use Xcode's asset catalog to generate sizes, OR
3. Manually create each size from master
4. Replace all files in `AppIcon.appiconset/`
5. Verify in Xcode asset catalog that all sizes show BeeSmart logo

**When**: Before creating the new archive

---

#### 3. Capture New iPad Screenshots (CRITICAL)
**Why**: Apple rejected stretched iPhone screenshots

**Required**:
- **iPad Pro (12.9-inch)**: 2048×2732 pixels
- **iPad Pro (11-inch)**: 1668×2388 pixels (if supporting)

**Steps**:
1. Open Xcode
2. Select **iPad Pro (13-inch)** or **iPad Pro 12.9-inch** simulator
3. Run app: `Product → Run` (or `Cmd+R`)
4. Navigate through key screens:
   - ✅ Home screen showing "Avatars" tile prominently
   - ✅ Avatar picker/shop showing purchasable avatars
   - ✅ Quiz in progress
   - ✅ Results/report card
   - ✅ Word upload interface
5. Capture screenshots: `Device → Screenshot` (or `Cmd+S`)
6. Screenshots auto-save to Desktop
7. Upload to App Store Connect:
   - Go to: App Store Connect → Your App → App Store → Screenshots
   - Select "iPad Pro (12.9-inch)" size
   - Upload all new screenshots
   - Reorder to show key features first

**When**: After new build is uploaded, before resubmission

---

#### 4. Verify App Store Connect Configuration
**Why**: IAP flow may fail if products aren't configured correctly

**Checklist**:
- [ ] **Paid Apps Agreement**: Go to App Store Connect → Agreements, Tax, and Banking
  - Ensure "Paid Apps Agreement" status is **Active**
  - If not active, complete the agreement process

- [ ] **IAP Products**: Go to App Store Connect → Your App → In-App Purchases
  - Verify all product IDs match server configuration
  - All products must be **"Cleared for Sale"** (not just "Ready to Submit")
  - Check file: `avatar_skus.py` or `IAP_DEVELOPER_GUIDE.md` for product ID list

- [ ] **Review Information**: Go to App Store Connect → Your App → App Store → App Review Information
  - Add navigation steps:
    ```
    NAVIGATION TO IAP PURCHASES:
    1. From Home screen, tap the "Avatars" tile (🐝 icon, gold theme)
    2. Browse the avatar collection
    3. Tap any locked avatar to see purchase option
    4. Tap "Unlock" or purchase button to initiate purchase
    ```
  - Demo Account: `student_demo` / `REVIEW-ONLY`
  - Notes: "All features accessible without additional setup."

**When**: Before resubmission

---

#### 5. Deploy Web Changes (If Applicable)
**Why**: Avatars tile changes are in web templates

**If using web-based app**:
1. Deploy latest code to production server
2. Verify `templates/unified_menu.html` is updated
3. Test that "Avatars" tile appears and navigates correctly
4. Verify `/honeycomb-picker` route works

**If using bundled web assets**:
- Changes are included in new Xcode build automatically

---

## 📊 Build Requirements Summary

| Change | Requires New Build? | Reason |
|--------|---------------------|--------|
| Info.plist (background audio) | ✅ **YES** | Native iOS config file |
| Avatars tile (HTML/JS) | ❌ No | Web template (unless bundled) |
| CSS theme class | ❌ No | Web template (unless bundled) |
| App icons | ✅ **YES** | Native asset catalog |
| Screenshots | ❌ No | App Store Connect only |

**Answer**: ✅ **YES, NEW XCODE BUILD REQUIRED**

---

## 🚀 Recommended Workflow

### Step 1: Prepare Assets (Before Build)
1. Replace all app icons with BeeSmart branding
2. Verify icons in Xcode asset catalog

### Step 2: Create New Build
1. Pull latest code
2. Open in Xcode
3. Verify Info.plist changes
4. Increment build number
5. Create archive
6. Upload to App Store Connect

### Step 3: Update App Store Connect
1. Capture new iPad screenshots
2. Upload screenshots
3. Verify IAP products are "Cleared for Sale"
4. Update review information with navigation steps
5. Verify Paid Apps Agreement is active

### Step 4: Test New Build
1. Install TestFlight build on test device
2. Verify "Avatars" tile appears on home screen
3. Test navigation to avatar picker
4. Test IAP purchase flow in sandbox

### Step 5: Resubmit
1. Select new build in App Store Connect
2. Add reviewer notes about navigation
3. Submit for review

---

## 📝 Files Changed (Reference)

**Modified Files**:
- `mobile/ios/App/App/Info.plist` - Background audio removed
- `templates/unified_menu.html` - Avatars tile + CSS + handlers added
- `smoke_test.py` - UTF-8 encoding fix
- `smoke_test_quiz_flow.py` - UTF-8 encoding fix
- `smoke_test_import_to_report_card.py` - UTF-8 encoding fix

**New Documentation**:
- `APPLE_REJECTION_RESPONSE.md` - Complete rejection response guide
- `PRE_GIT_PUSH_CHECKLIST.md` - Pre-push verification
- `FREELANCE_TEAM_UPDATE_BREAKDOWN.md` - This document

**Git Commit**: `5d12eb3` - "fix: Address Apple App Store rejection issues"

---

## ⚠️ Critical Reminders

1. **Build Number Must Increment**: Apple requires a new build number for each submission
2. **Icons Must Be Replaced**: Placeholder icons will cause rejection
3. **Screenshots Must Be Genuine**: Stretched iPhone screens will be rejected
4. **IAP Products Must Be "Cleared for Sale"**: Not just "Ready to Submit"
5. **Reviewer Notes Are Critical**: Help reviewers find the IAP shop

---

## 📞 Questions?

If the team has questions about:
- **Code changes**: See `APPLE_REJECTION_RESPONSE.md` for detailed explanations
- **Build process**: See `XCODE_APP_STORE_SUBMISSION_GUIDE.md`
- **IAP configuration**: See `IAP_DEVELOPER_GUIDE.md` and `APP_STORE_IAP_SETUP.md`

---

## ✅ Checklist for Team

Before resubmission, verify:
- [ ] New Xcode build created with incremented build number
- [ ] All app icons replaced with BeeSmart branding
- [ ] Info.plist changes verified (no background audio)
- [ ] New iPad screenshots captured and uploaded
- [ ] IAP products are "Cleared for Sale"
- [ ] Paid Apps Agreement is active
- [ ] Reviewer notes include navigation to Avatars shop
- [ ] TestFlight build tested (Avatars tile works)
- [ ] All changes committed and pushed to repository

---

**Last Updated**: January 12, 2026  
**Status**: Code changes complete - Team action required for build and assets
