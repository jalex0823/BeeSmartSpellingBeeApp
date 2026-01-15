# 🧪 TestFlight & Sandbox Testing Checklist
## Priority Testing Guide for Today's Updates (January 2026)

---

## 🎯 **CRITICAL PRIORITY - Apple Review Requirements**

### 1. **In-App Purchase (IAP) Testing - SANDBOX ONLY**
**Why:** Apple rejected the app because reviewers couldn't locate IAPs

#### ✅ **Avatar IAP Testing:**
- [ ] Navigate to main menu → Click "Avatars" tile
- [ ] Verify avatar tile is same size as other menu tiles
- [ ] Browse all 41 avatars without logging in (guest access)
- [ ] Click on a locked avatar (premium avatar)
- [ ] Verify purchase flow initiates WITHOUT requiring login/registration
- [ ] Complete a sandbox purchase as guest user
- [ ] Verify purchase succeeds and avatar unlocks
- [ ] After purchase, verify optional registration prompt appears (not forced)
- [ ] Test "Restore Purchases" button functionality
- [ ] Verify all avatar IAPs are accessible and purchasable

#### ✅ **Subscription IAP Testing:**
- [ ] Navigate to subscription page
- [ ] Attempt to purchase subscription without logging in
- [ ] Verify purchase flow works (no forced registration)
- [ ] Complete sandbox subscription purchase
- [ ] Verify subscription unlocks premium features
- [ ] Test subscription restore functionality

#### ✅ **IAP Navigation for Apple Reviewers:**
- [ ] Document exact steps to find IAPs:
  1. Main Menu → "Avatars" tile
  2. Browse avatars → Click locked avatar
  3. Purchase button appears
- [ ] Verify these steps work in sandbox environment
- [ ] Test with fresh sandbox account (no previous purchases)

---

### 2. **Registration Requirements (Guideline 5.1.1)**
**Why:** Apple requires IAPs to work without forced registration

#### ✅ **Guest User IAP Flow:**
- [ ] Start app without logging in
- [ ] Navigate to Avatars section
- [ ] Attempt to purchase avatar as guest
- [ ] Verify purchase completes successfully
- [ ] Verify registration is suggested (not required) after purchase
- [ ] Verify user can skip registration and continue using app

#### ✅ **Subscription Guest Flow:**
- [ ] Start app without logging in
- [ ] Navigate to subscription page
- [ ] Purchase subscription as guest
- [ ] Verify purchase completes
- [ ] Verify registration is optional (not forced)

---

### 3. **Stats Display (Guideline 2.1)**
**Why:** Apple thought app was non-functional due to zero stats

#### ✅ **Zero Stats Explanation Messages:**
- [ ] Login as new user (or user with 0 quizzes)
- [ ] Check **Student Dashboard** - verify explanation message appears
- [ ] Check **Main Menu** welcome card - verify explanation appears
- [ ] Check **Teacher Dashboard** - verify class stats explanation (if 0 quizzes)
- [ ] Check **Parent Dashboard** - verify family stats explanation (if 0 quizzes)
- [ ] Verify messages are kid-friendly and clear
- [ ] Verify messages explain stats populate after quiz completion

#### ✅ **Stats After Quiz:**
- [ ] Complete a quiz as new user
- [ ] Verify stats update correctly (points, grade, GPA, accuracy)
- [ ] Verify explanation messages disappear after stats populate
- [ ] Verify all dashboards show correct stats

---

## 🐛 **BUG FIXES - Today's Updates**

### 4. **UI Responsiveness Fixes**

#### ✅ **Tile Click Responsiveness:**
- [ ] Test all menu tiles (Dictionary, Avatars, Saved Lists, etc.)
- [ ] Verify tiles respond immediately to clicks (no long press required)
- [ ] Test on iPhone (various models)
- [ ] Test on iPad
- [ ] Verify no sluggishness or delay

#### ✅ **Avatar Tile Sizing:**
- [ ] Verify "Avatars" tile matches size of other menu tiles
- [ ] Check on different screen sizes (iPhone SE, iPhone 14, iPad)
- [ ] Verify consistent appearance across devices

#### ✅ **Preview Loader:**
- [ ] Navigate to avatar picker
- [ ] Select an avatar to preview
- [ ] Verify loading text is readable (dark brown, not gold)
- [ ] Verify loading indicator fades out smoothly at 100%
- [ ] Verify no loading text remains visible after avatar loads

---

### 5. **JavaScript Errors Fixed**

#### ✅ **Duplicate Script Declarations:**
- [ ] Navigate from main menu to quiz page
- [ ] Navigate from quiz to avatar picker
- [ ] Navigate back to main menu
- [ ] Check browser console - verify NO errors:
  - ❌ "Identifier 'SmartyBee3D' has already been declared"
  - ❌ "Identifier 'Badge3DRenderer' has already been declared"
  - ❌ "Identifier 'avatarInitialized' has already been declared"
  - ❌ "Multiple instances of Three.js being imported"
- [ ] Verify 3D avatars still render correctly after navigation

#### ✅ **Speed Round Error Fix:**
- [ ] Start a speed round challenge
- [ ] Verify no 500 errors occur
- [ ] Test with different difficulty levels
- [ ] Test with different word counts (10, 20, 30)
- [ ] Verify words generate correctly
- [ ] Complete a speed round and verify results save

---

### 6. **Music Icon Removal (Guideline 2.5.4)**

#### ✅ **Background Audio Removal:**
- [ ] Verify music note icon is NOT visible on main menu
- [ ] Verify no music controls appear anywhere
- [ ] Check all pages (main menu, quiz, dashboard, avatar picker)
- [ ] Verify no audio-related errors in console

---

## 📱 **DEVICE & PLATFORM TESTING**

### 7. **iOS Device Testing**

#### ✅ **iPhone Testing:**
- [ ] iPhone SE (small screen)
- [ ] iPhone 13/14 (standard)
- [ ] iPhone 14 Pro Max (large screen)
- [ ] Verify all UI elements scale correctly
- [ ] Verify touch targets are appropriate size
- [ ] Test portrait and landscape orientations

#### ✅ **iPad Testing:**
- [ ] iPad Air (5th generation) - **Apple's review device**
- [ ] iPad Pro 12.9"
- [ ] Verify screenshots match actual app (not stretched iPhone images)
- [ ] Verify IAPs are accessible on iPad
- [ ] Test split-screen/multitasking

---

## 🔐 **SANDBOX ENVIRONMENT TESTING**

### 8. **Sandbox Account Setup**

#### ✅ **Test Accounts:**
- [ ] Create fresh sandbox test account in App Store Connect
- [ ] Sign out of App Store on test device
- [ ] Sign in with sandbox account when prompted
- [ ] Verify sandbox purchases work correctly

#### ✅ **Sandbox Purchase Flow:**
- [ ] Test avatar purchases (multiple avatars)
- [ ] Test subscription purchase
- [ ] Test bundle purchases (if applicable)
- [ ] Verify purchases persist after app restart
- [ ] Test restore purchases functionality
- [ ] Verify purchases sync across devices (if user registers)

---

## 🎮 **CORE FUNCTIONALITY**

### 9. **Quiz System**

#### ✅ **Quiz Flow:**
- [ ] Start quiz from main menu
- [ ] Complete quiz successfully
- [ ] Verify stats update after completion
- [ ] Verify points are awarded
- [ ] Verify grade/GPA calculation
- [ ] Check quiz history appears in dashboard

### 10. **Speed Round**

#### ✅ **Speed Round Flow:**
- [ ] Start speed round (premium feature)
- [ ] Complete speed round
- [ ] Verify results save correctly
- [ ] Verify points/badges awarded
- [ ] Check speed round history

### 11. **Avatar System**

#### ✅ **Avatar Functionality:**
- [ ] Browse all 41 avatars
- [ ] Preview avatars (3D rendering)
- [ ] Purchase locked avatars
- [ ] Select avatar for use
- [ ] Verify avatar appears on main menu
- [ ] Verify avatar appears in dashboard

---

## 🚨 **EDGE CASES & ERROR HANDLING**

### 12. **Error Scenarios**

#### ✅ **Network Issues:**
- [ ] Test with poor/no internet connection
- [ ] Verify graceful error messages
- [ ] Verify app doesn't crash

#### ✅ **Empty States:**
- [ ] New user with 0 quizzes (verify explanation messages)
- [ ] User with no uploaded word lists
- [ ] User with no saved avatars

#### ✅ **Session Management:**
- [ ] Test app after extended idle time
- [ ] Test app after backgrounding
- [ ] Verify session persistence

---

## 📋 **APPLE REVIEW SPECIFIC CHECKS**

### 13. **Reviewer Navigation**

#### ✅ **IAP Discovery:**
- [ ] Document exact navigation path to IAPs:
  1. Launch app
  2. Main menu → "Avatars" tile
  3. Browse → Click locked avatar
  4. Purchase button visible
- [ ] Verify this works in sandbox
- [ ] Create screenshot guide for App Store Connect reply

#### ✅ **Demo Account:**
- [ ] Verify demo account credentials work
- [ ] Verify demo account has access to all features
- [ ] Test login with demo account
- [ ] Verify demo account can complete quizzes
- [ ] Verify demo account shows populated stats

#### ✅ **Terms of Use Link:**
- [ ] Verify Terms of Use link is functional
- [ ] Verify link appears in subscription page
- [ ] Verify link works in sandbox environment

---

## 📊 **REPORTING TEMPLATE**

### For Each Test:
- **Device:** [iPhone/iPad model]
- **iOS Version:** [version]
- **Test Account:** [sandbox account email]
- **Result:** ✅ Pass / ❌ Fail
- **Notes:** [any issues found]
- **Screenshots:** [attach if issue found]

### Critical Issues to Report Immediately:
1. IAP purchases not working in sandbox
2. Forced registration before IAP
3. 500 errors on any endpoint
4. JavaScript console errors
5. App crashes
6. Stats not updating after quiz completion

---

## 🎯 **PRIORITY ORDER**

1. **HIGHEST:** IAP sandbox testing (Apple's main concern)
2. **HIGH:** Registration requirements (no forced login)
3. **HIGH:** Stats explanation messages (zero values)
4. **MEDIUM:** UI responsiveness fixes
5. **MEDIUM:** JavaScript error fixes
6. **LOW:** Edge cases

---

## 📝 **NOTES FOR FREELANCERS**

- **Test in SANDBOX environment only** - don't use production
- **Use fresh sandbox accounts** for IAP testing
- **Document exact steps** to find IAPs (for Apple reviewers)
- **Take screenshots** of any issues
- **Test on iPad Air (5th gen)** - Apple's review device
- **Focus on guest user experience** - IAPs must work without login
- **Verify all explanation messages** appear for zero stats

---

**Last Updated:** January 2026
**Testing Focus:** Apple Review Requirements + Today's Bug Fixes
