# BeeSmart Testing Checklist - December 29, 2025

## 🎯 Priority Testing Areas

### 1. ✨ NEW: Fairy Dust Launch Screen Effect
**Location:** App launch screen with BeeSmart logo

**Test Items:**
- [ ] **Visual Appeal:** Does the fairy dust effect look magical and organic (NOT like dots in a circle)?
- [ ] **Performance:** Is the animation smooth (60fps) on your device?
- [ ] **Particle Behavior:** Do particles flow naturally around the logo with varied sizes?
- [ ] **Sparkle Bursts:** Do you see occasional star-shaped sparkles appearing?
- [ ] **Trail Effects:** Do particles leave glowing trails as they move?
- [ ] **Screen Rotation:** Does effect resize properly when rotating device?
- [ ] **Battery Impact:** Does the effect cause noticeable battery drain?
- [ ] **Older Devices:** Test on iPhone 8/X or older - still smooth?

**What to Look For:**
- Golden/yellow particles swirling around logo
- Varied particle sizes (small to medium)
- Organic, flowing movement (like fairy dust)
- Random sparkle bursts appearing
- Subtle glowing trails
- Smooth animation without stuttering

---

### 2. 🔐 In-App Purchase (IAP) Product IDs - CRITICAL
**Location:** Avatar store, subscription pages

**Test Items:**
- [ ] **Avatar Purchases:** Can you successfully purchase premium avatars?
- [ ] **Product Names:** Do all avatars show "Avatar" suffix in purchase prompts?
- [ ] **Price Display:** Do prices show correctly for all avatars?
- [ ] **Purchase Confirmation:** After purchase, does avatar unlock immediately?
- [ ] **Receipt Validation:** Do purchased avatars stay unlocked after app restart?
- [ ] **Subscription Page:** Does subscription page load without errors?
- [ ] **Subscription Purchase:** Can you purchase/restore subscription?
- [ ] **Back Button:** Is there a back button on subscription page?

**Critical Check:**
- ALL avatar names MUST end with " Avatar" (e.g., "Cool Bee Avatar")
- Product IDs must match App Store Connect exactly
- No 500 errors or server crashes

---

### 3. 🎨 Avatar System (39 Total Avatars)
**Location:** Avatar selection, customization pages

**Test Items:**
- [ ] **Avatar Count:** Can you see all 39 avatars in catalog?
- [ ] **GLB Loading:** Do all 3D avatars load and display correctly?
- [ ] **Thumbnails:** Do all avatar thumbnails show (no broken images)?
- [ ] **Tier System:** 
  - 5 free avatars available immediately
  - 7 earn/buy avatars (locked until earned)
  - 26 premium avatars (require purchase)
  - 1 mascot avatar
- [ ] **Purchase Flow:** Premium avatars show price and unlock after purchase
- [ ] **Favorite Feature:** Can you favorite avatars?
- [ ] **Avatar Selection:** Can you select and apply an avatar to your profile?
- [ ] **3D Viewer:** Does avatar rotate/zoom smoothly in viewer?

**Key Avatar Mappings to Verify:**
- Robo Bee Avatar → uses BuzzbotBee.glb
- Super Bee Avatar → uses SuperBee.glb
- Knight Bee Avatar → uses KnightBee.glb

---

### 4. 📝 Word List Upload & Quiz Flow
**Location:** Upload page, quiz page

**Test Items:**
- [ ] **Text Upload:** Upload a .txt file with spelling words
- [ ] **Manual Entry:** Add words manually through input form
- [ ] **OCR Upload (Optional):** If available, test image upload with text
- [ ] **Word Deduplication:** Upload same word twice - only stored once?
- [ ] **Definition Loading:** Do word definitions appear (kid-friendly)?
- [ ] **Quiz Start:** Can you start quiz after uploading words?
- [ ] **Answer Checking:** Correct spelling accepted, wrong spelling rejected?
- [ ] **Pronunciation:** Does text-to-speech pronounce words correctly?
- [ ] **Progress Tracking:** Does quiz track progress (X of Y words)?
- [ ] **Quiz Completion:** Does quiz end properly and show results?

---

### 5. 🔒 Authentication & Account Management
**Location:** Login, signup, password reset

**Test Items:**
- [ ] **New Account:** Can you create a new account?
- [ ] **Login:** Can you log in with existing credentials?
- [ ] **Logout:** Can you log out successfully?
- [ ] **Password Reset:** 
  - Request password reset email
  - Receive reset email with link
  - Click link and reset password
  - Log in with new password
- [ ] **Session Persistence:** Stay logged in after closing/reopening app?
- [ ] **Parent Account:** Can parent/admin access admin dashboard?

---

### 6. 📊 Admin Dashboard (Parent/Teacher Access)
**Location:** Admin/parent dashboard

**Test Items:**
- [ ] **Login:** Can you access dashboard with admin credentials?
- [ ] **User Management:** Can you view student/child accounts?
- [ ] **Word Lists:** Can you create/edit word lists for students?
- [ ] **Progress Reports:** Can you view quiz results and progress?
- [ ] **Avatar Management:** Can you view avatar inventory?
- [ ] **Account Settings:** Can you update profile settings?

---

### 7. 🎮 Speed Round Quiz (If Available)
**Location:** Speed round quiz mode

**Test Items:**
- [ ] **Start Speed Round:** Can you initiate speed round?
- [ ] **Timer:** Does countdown timer work correctly?
- [ ] **Rapid Questions:** Questions appear quickly without lag?
- [ ] **Score Calculation:** Points awarded correctly?
- [ ] **Results:** Final score and stats displayed?

---

### 8. 🔔 Progressive Web App (PWA) Features
**Location:** iOS Safari, home screen

**Test Items:**
- [ ] **Add to Home Screen:** Can you add BeeSmart to home screen?
- [ ] **App Icon:** Does icon show correctly on home screen?
- [ ] **Splash Screen:** Shows BeeSmart splash when launching from home screen?
- [ ] **Offline Mode:** Does app work without internet (cached content)?
- [ ] **Push Notifications (if enabled):** Receive notifications?

---

### 9. 🐛 General Stability & Performance
**Test Items:**
- [ ] **No Crashes:** App doesn't crash during normal use
- [ ] **No 500 Errors:** No server error pages appear
- [ ] **Page Load Speed:** Pages load within 2-3 seconds
- [ ] **Responsive Design:** Works on different screen sizes (iPhone, iPad)
- [ ] **Navigation:** All menu buttons and links work
- [ ] **Back Buttons:** Can navigate back from all pages
- [ ] **Session Management:** Don't get logged out unexpectedly

---

## 📱 Device Coverage Needed
Please test on as many devices as possible:

- [ ] **iPhone 15/16 Pro** (latest)
- [ ] **iPhone 12/13/14** (recent)
- [ ] **iPhone 8/X** (older, performance test)
- [ ] **iPad** (tablet layout)
- [ ] **iOS 17/18** (latest OS)
- [ ] **iOS 15/16** (older OS)

---

## 🚨 Critical Issues to Report Immediately
Report these issues ASAP if found:

1. **App crashes or freezes**
2. **Cannot purchase avatars or subscriptions**
3. **Login/authentication fails**
4. **Word lists don't save**
5. **Quiz doesn't work or score incorrectly**
6. **Fairy dust effect causes lag/battery drain**
7. **500 server errors appear**
8. **Payment failures or receipt validation errors**

---

## 📝 How to Report Issues

**Include in your report:**
1. **Device:** iPhone model and iOS version
2. **Steps to Reproduce:** What did you do before the issue?
3. **Expected Behavior:** What should happen?
4. **Actual Behavior:** What actually happened?
5. **Screenshots/Video:** If possible, capture the issue
6. **Frequency:** Does it happen every time or randomly?

**Example Report:**
```
Device: iPhone 14, iOS 17.2
Issue: Fairy dust effect stutters
Steps: 1) Launch app 2) Watch logo animation
Expected: Smooth 60fps animation
Actual: Animation stutters/lags every few seconds
Frequency: Every time
```

---

## ✅ Sign-Off
Once you've completed testing, please confirm:

- [ ] I tested all priority areas above
- [ ] I tested on device: _______________
- [ ] I found NO critical issues OR reported all issues found
- [ ] Fairy dust effect looks magical ✨
- [ ] Avatar purchases work correctly 🎨
- [ ] Quiz flow works smoothly 📝

**Tester Name:** _______________  
**Date Tested:** _______________  
**Overall Assessment:** ⭐⭐⭐⭐⭐ (circle rating)

---

## 🎯 Build Information
- **Build Date:** December 29, 2025
- **Key Changes:**
  - ✨ New fairy dust particle effect on launch screen
  - 🔧 Fixed IAP Product IDs (critical)
  - 🎨 39 GLB avatars with proper naming
  - 🔙 Added back button to subscription page
  - 📊 Admin dashboard improvements

**Thank you for testing! Your feedback helps make BeeSmart better! 🐝**
