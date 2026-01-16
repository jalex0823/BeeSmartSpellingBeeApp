# Manual Validation Checklist - Apple Rejection Fixes

**Date:** January 16, 2025  
**Build:** 46/46  
**Status:** ✅ App Icons Verified

---

## ✅ Already Verified

- [x] **App Icons** - BeeSmart branding confirmed (all sizes present)
- [x] **UIBackgroundModes** - Not present in Info.plist (verified)
- [x] **Code Fixes** - All IAP error handling and database fixes implemented

---

## ⚠️ Manual Validation Required

### 1. IAP Purchase Flow Testing (CRITICAL)

**Why:** Apple rejected because "unable to purchase in app purchase"

**Testing Steps:**

#### A. Sandbox Environment Setup
- [ ] **Sign out of App Store** on test device
  - Settings → [Your Name] → Media & Purchases → Sign Out
  - **CRITICAL:** Must sign out of production App Store

- [ ] **Create/Verify Sandbox Test Account**
  - App Store Connect → Users and Access → Sandbox Testers
  - Create new sandbox tester (unique email, not your real Apple ID)
  - Note: Sandbox accounts are separate from production

#### B. Test Avatar Purchase Flow
- [ ] **Launch app** (in TestFlight or development build)
- [ ] **Navigate to Avatars**
  - Main menu → Tap "Avatars" tile (🐝 icon, gold theme)
  - Should open `/honeycomb-picker` page

- [ ] **Browse avatars**
  - Verify all avatars are visible
  - Locked avatars show lock icon 🔒 or "Unlock" button
  - Unlocked avatars are fully visible

- [ ] **Attempt purchase**
  - Tap a locked avatar
  - Tap "Unlock" or purchase button
  - **Expected:** Native StoreKit purchase dialog appears

- [ ] **Complete purchase**
  - When prompted, sign in with sandbox test account
  - Complete purchase flow
  - **Expected:** Purchase succeeds, avatar unlocks

- [ ] **Verify purchase**
  - Avatar should now be unlocked
  - Can select the avatar
  - Purchase record should be saved

#### C. Test Restore Purchases
- [ ] **Tap "Restore Purchases"** button (if available)
- [ ] **Expected:** Previously purchased avatars restore
- [ ] **Verify:** No 500 errors, graceful error handling

#### D. Test Guest Purchase (Apple Guideline 5.1.1)
- [ ] **Launch app without logging in**
- [ ] **Navigate to Avatars** (should work without login)
- [ ] **Attempt purchase as guest**
- [ ] **Expected:** Purchase works without forced registration
- [ ] **After purchase:** Registration suggested (not required)

#### E. Test Subscription Purchase
- [ ] **Navigate to subscription page**
- [ ] **Attempt subscription purchase**
- [ ] **Complete purchase in sandbox**
- [ ] **Verify:** Subscription unlocks premium features

**Success Criteria:**
- ✅ All purchases complete successfully
- ✅ No crashes or 500 errors
- ✅ Avatars unlock after purchase
- ✅ Works without login (guest mode)
- ✅ Restore purchases works

---

### 2. IAP Navigation Verification

**Why:** Apple couldn't locate IAP products

**Verification Steps:**

- [ ] **Launch app** → Main menu appears
- [ ] **Locate "Avatars" tile**
  - Should be prominently displayed
  - Gold/yellow theme with 🐝 icon
  - Text: "Avatars" with subtitle "Browse & unlock bee characters"
  - Position: Between "Dictionary Search" and "Saved Word Lists"

- [ ] **Tap "Avatars" tile**
  - Should navigate to `/honeycomb-picker`
  - Avatar picker page loads
  - All avatars visible in grid

- [ ] **Verify locked avatars show purchase option**
  - Tap locked avatar
  - Purchase button/option appears
  - Clear call-to-action

**Success Criteria:**
- ✅ Avatars tile visible on main menu
- ✅ Navigation works correctly
- ✅ Purchase options clearly visible
- ✅ No login required to browse

---

### 3. Info.plist Verification (UIBackgroundModes)

**Why:** Apple says audio background mode is declared

**Verification Steps:**

- [ ] **Open Xcode**
- [ ] **Navigate to:** App → Info.plist
- [ ] **Search for:** `UIBackgroundModes`
- [ ] **Verify:** Key does NOT exist
- [ ] **If found:** Remove the key and all its values

**Alternative Check:**
```bash
# Terminal check
grep -i "UIBackgroundModes" mobile/ios/App/App/Info.plist
# Should return: nothing (no matches)
```

**Success Criteria:**
- ✅ UIBackgroundModes not present in Info.plist
- ✅ No audio background mode declared

---

### 4. Build Configuration Verification

**Why:** Ensure latest fixes are included in build

**Verification Steps:**

- [ ] **Open Xcode**
- [ ] **Product → Clean Build Folder** (Shift+Cmd+K)
- [ ] **Verify Build Number:** 46 (in project settings)
- [ ] **Verify Version:** 1.0 (in project settings)
- [ ] **Build for Testing:** Product → Build (Cmd+B)
- [ ] **Verify:** Build succeeds with no errors

**Success Criteria:**
- ✅ Clean build successful
- ✅ Build number correct (46)
- ✅ No build errors

---

### 5. App Store Connect Configuration

**Why:** IAP products need proper configuration

**Verification Steps:**

- [ ] **Paid Apps Agreement**
  - App Store Connect → Agreements, Tax, and Banking
  - Verify "Paid Apps Agreement" status is **Active**
  - If not active, complete the agreement

- [ ] **IAP Product Configuration**
  - App Store Connect → Your App → Features → In-App Purchases
  - For each IAP product, verify:
    - Status is **"Ready to Submit"** or **"Cleared for Sale"**
    - Product ID matches exactly what's in app code
    - Price is set correctly
    - Display name and description are complete

- [ ] **Review Notes**
  - App Store Connect → Your App → App Store → App Information
  - Add navigation instructions (see Fix 4 in rejection fixes doc)
  - Include demo account if needed

**Success Criteria:**
- ✅ Paid Apps Agreement active
- ✅ All IAP products ready to submit
- ✅ Product IDs match app code
- ✅ Review notes include navigation steps

---

## 🚨 Critical Issues to Validate

### Priority 1: IAP Purchase Flow
**Impact:** HIGH - App was rejected for this
- [ ] Test complete purchase flow in sandbox
- [ ] Verify no crashes or errors
- [ ] Verify purchases complete successfully

### Priority 2: IAP Navigation
**Impact:** HIGH - Reviewers couldn't find IAPs
- [ ] Verify "Avatars" tile visible on main menu
- [ ] Verify navigation to avatar picker works
- [ ] Verify purchase options are clear

### Priority 3: Guest Access
**Impact:** MEDIUM - Apple Guideline 5.1.1 compliance
- [ ] Verify IAP works without login
- [ ] Verify registration is optional (not forced)

---

## 📝 Pre-Submission Checklist

### Code & Build
- [x] App icons verified (BeeSmart branding)
- [x] UIBackgroundModes removed
- [x] IAP error handling fixed
- [x] Database fixes implemented
- [ ] Clean build successful
- [ ] Build number correct (46)

### Testing
- [ ] IAP purchase flow tested in sandbox
- [ ] Restore purchases tested
- [ ] Guest purchase tested (no login required)
- [ ] Navigation verified (Avatars tile → Purchase)
- [ ] No crashes or 500 errors

### App Store Connect
- [ ] Paid Apps Agreement active
- [ ] IAP products configured correctly
- [ ] Review notes include navigation steps
- [ ] iPad screenshots updated (user action)

---

## 🎯 Quick Validation Script

Run this to verify key files:

```bash
# Check Info.plist for UIBackgroundModes
echo "Checking Info.plist..."
grep -i "UIBackgroundModes" mobile/ios/App/App/Info.plist || echo "✅ UIBackgroundModes not found"

# Check app icons exist
echo "Checking app icons..."
ls mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png && echo "✅ 1024×1024 icon exists"

# Check build number
echo "Checking build number..."
grep "CURRENT_PROJECT_VERSION = 46" mobile/ios/App/App.xcodeproj/project.pbxproj && echo "✅ Build number is 46"
```

---

## ✅ Validation Summary

After completing all checks:

- [ ] All critical tests passed
- [ ] IAP flow works correctly
- [ ] Navigation is clear
- [ ] No blocking issues found
- [ ] Ready for resubmission

---

**Next Steps After Validation:**
1. Fix any issues found during testing
2. Update App Store Connect review notes
3. Capture new iPad screenshots
4. Archive and upload new build
5. Submit for review

---

**Note:** The iPad screenshots issue is an App Store Connect action (not code), so handle that separately when updating metadata.
