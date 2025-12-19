# 🍎 BeeSmart Spelling Bee - Xcode & App Store Submission Checklist
**Date:** December 19, 2025  
**Version:** 1.7  
**Target:** iOS App Store Submission

---

## 📱 CURRENT STATUS: iOS Wrapper Ready

### ✅ What's Already Configured:
- ✅ Capacitor wrapper in `/mobile/ios/App/`
- ✅ Bundle ID: `com.beesmart.spelling`
- ✅ Server URL: `https://beesmartspelling.app`
- ✅ IAP Plugin: `BeeSmartIAPPlugin.swift` (StoreKit 2)
- ✅ Info.plist with basic permissions
- ✅ Launch screen configured

---

## 🚀 STEP-BY-STEP SUBMISSION GUIDE

### STEP 1: Update Info.plist ⚡ REQUIRED
**Location:** `/mobile/ios/App/App/Info.plist`

#### Add Missing Required Keys:

```xml
<!-- Add these to your Info.plist BEFORE <key>NSPhotoLibraryUsageDescription</key> -->

<!-- App Category (Required for App Store) -->
<key>LSApplicationCategoryType</key>
<string>public.app-category.education</string>

<!-- Privacy - Camera Usage (for word list OCR) -->
<key>NSCameraUsageDescription</key>
<string>BeeSmart Spelling uses your camera to scan word lists from paper or whiteboards, making it easy to create custom spelling quizzes.</string>

<!-- Privacy - Microphone Usage (for speech recognition) -->
<key>NSMicrophoneUsageDescription</key>
<string>BeeSmart Spelling uses your microphone for voice-based spelling practice and pronunciation features.</string>

<!-- App Transport Security (allow your Railway backend) -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>beesmartspelling.app</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <false/>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSExceptionRequiresForwardSecrecy</key>
            <true/>
            <key>NSExceptionMinimumTLSVersion</key>
            <string>TLSv1.2</string>
        </dict>
    </dict>
</dict>

<!-- Privacy Manifest (iOS 17+ requirement) -->
<key>NSPrivacyTracking</key>
<false/>
<key>NSPrivacyTrackingDomains</key>
<array/>
<key>NSPrivacyCollectedDataTypes</key>
<array/>
<key>NSPrivacyAccessedAPITypes</key>
<array>
    <dict>
        <key>NSPrivacyAccessedAPIType</key>
        <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
        <key>NSPrivacyAccessedAPITypeReasons</key>
        <array>
            <string>CA92.1</string>
        </array>
    </dict>
</array>

<!-- Background Modes (if using audio in background) -->
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array>

<!-- Required Device Capabilities -->
<key>UIRequiredDeviceCapabilities</key>
<array>
    <string>arm64</string>
</array>
```

**Update existing key:**
```xml
<!-- Change from empty to education category -->
<key>LSApplicationCategoryType</key>
<string>public.app-category.education</string>
```

---

### STEP 2: Open Xcode Project

```bash
cd /Users/jalex0823/Dropbox/BeeSmartSpellingBeeApp/mobile
npx cap sync ios
npx cap open ios
```

---

### STEP 3: Configure Project Settings in Xcode

#### A. General Tab:
- **Display Name:** `BeeSmart Spelling`
- **Bundle Identifier:** `com.beesmart.spelling`
- **Version:** `1.7.0` (matches backend version)
- **Build:** `1` (increment for each upload: 2, 3, 4...)
- **Deployment Target:** iOS 15.0 (minimum for StoreKit 2)

#### B. Signing & Capabilities:
- **Team:** Select your Apple Developer Team
- **Signing Certificate:** Apple Distribution
- **Provisioning Profile:** App Store (automatic or manual)

**Required Capabilities:**
- [x] In-App Purchase
- [x] Push Notifications (if using)
- [x] Background Modes → Audio (for voice features)

#### C. Build Settings:
- **Swift Language Version:** Swift 5
- **Marketing Version:** `1.7.0`
- **Current Project Version:** `1`
- **iOS Deployment Target:** 15.0
- **Targeted Device Family:** iPhone, iPad
- **Supported Platforms:** iOS

---

### STEP 4: Verify Native IAP Plugin

**Location:** `/mobile/ios/App/App/BeeSmartIAPPlugin.swift`

✅ Already implemented! Verify these methods exist:
- `getOwnedProducts()` - Returns owned product IDs
- `purchase(productId)` - Initiates purchase, returns JWS receipt

**Test in JavaScript console:**
```javascript
// Should be available in your web app
window.BeeSmartIAP?.getOwnedProducts()
window.BeeSmartIAP?.purchase({productId: 'com.beesmart.avatar.superbee'})
```

---

### STEP 5: Create App Icons

**Required Sizes:**
- 1024x1024 (App Store)
- 180x180 (iPhone)
- 167x167 (iPad Pro)
- 152x152 (iPad)
- 120x120 (iPhone)
- 87x87 (iPhone Notification)
- 80x80 (iPad Spotlight)
- 76x76 (iPad)
- 60x60 (iPhone Spotlight)
- 58x58 (iPhone Notification)
- 40x40 (iPad Spotlight)
- 29x29 (Settings)
- 20x20 (iPad Notification)

**How to Add:**
1. In Xcode, select `App/Assets.xcassets/AppIcon`
2. Drag icons for each size slot
3. Verify all slots filled (no warnings)

**Design Guidelines:**
- Bee theme with yellow/gold colors
- No text or words in icon
- Must be opaque (no transparency)
- Square with rounded corners (iOS auto-applies)

---

### STEP 6: Update Launch Screen

**Location:** `/mobile/ios/App/App/LaunchScreen.storyboard`

Current config in `capacitor.config.ts`:
```typescript
SplashScreen: {
  launchShowDuration: 2000,
  backgroundColor: '#FFD700',  // Gold/yellow
  showSpinner: false
}
```

**Optional Enhancement:**
Add BeeSmart logo to launch screen for branding.

---

### STEP 7: Configure App Store Connect

#### A. Create App Listing:
1. Go to https://appstoreconnect.apple.com
2. Click "My Apps" → "+" → "New App"
3. Fill in:
   - **Platform:** iOS
   - **Name:** BeeSmart Spelling Bee
   - **Primary Language:** English (U.S.)
   - **Bundle ID:** com.beesmart.spelling
   - **SKU:** BEESMART-SPELLING-001
   - **User Access:** Full Access

#### B. App Information:
- **Category:** Education
- **Secondary Category:** Kids (Ages 6-8 or 9-11)
- **Content Rights:** Check "Yes" if you own all content

#### C. Pricing:
- **Price:** Free (with In-App Purchases)
- **Availability:** All countries

#### D. Age Rating:
**Complete questionnaire:**
- **Made for Kids:** Yes (COPPA compliant)
- **Age Range:** 6-8 or 9-11
- **Parental Gate:** Yes (implemented for external links/purchases)
- **Contests/Sweepstakes:** No
- **Violence/Gore:** None
- **Sexual Content:** None
- **Profanity:** None
- **Alcohol/Tobacco/Drugs:** None
- **Mature/Suggestive Themes:** None
- **Horror/Fear Themes:** None
- **Medical/Treatment Info:** No
- **Gambling:** No
- **Unrestricted Web Access:** No
- **User-Generated Content:** No

**Recommended Rating:** **4+**

#### E. App Privacy:
**Data Collection:**
- **Email Address** - Collected for account management (not shared)
- **Purchase History** - Collected for IAP (not shared)
- **User Content** - Word lists (not shared, stored locally)

**Privacy Policy URL:** https://beesmartspelling.app/privacy

**Data Usage:**
- [ ] Data used to track user (NO)
- [x] Data linked to user identity (YES - email, purchases)
- [ ] Data used for third-party advertising (NO)

---

### STEP 8: Configure In-App Purchases

#### A. Create IAP Products in App Store Connect:

**Product IDs (from your catalog):**
```
beesmart.premium.monthly         - $4.99 - Monthly Premium
beesmart.premium.yearly          - $39.99 - Yearly Premium  
beesmart.premium.family.monthly  - $7.99 - Family Monthly

# Individual Avatars ($0.99 each)
com.beesmart.avatar.superbee
com.beesmart.avatar.queen
com.beesmart.avatar.knight
com.beesmart.avatar.rocker
com.beesmart.avatar.pirate
com.beesmart.avatar.ninja
com.beesmart.avatar.detective
# ... (see APPLE_IAP_NAMING_STANDARD.md for full list)

# Avatar Bundles ($4.99 - $9.99)
com.beesmart.bundle.starter
com.beesmart.bundle.premium
com.beesmart.bundle.ultimate
```

**For Each Product:**
1. Click "In-App Purchases" → "+"
2. Select type: "Consumable" or "Auto-Renewable Subscription"
3. Reference Name: "Super Bee Avatar" (internal only)
4. Product ID: `com.beesmart.avatar.superbee`
5. **Display Name:** "Super Bee Avatar" ⚠️ MUST END WITH "Avatar"
6. Description: Kid-friendly description
7. Price: Select tier ($0.99, $4.99, etc.)
8. Review Screenshot: 640x920 opaque image showing avatar
9. Review Notes: "Unlocks Super Bee character"
10. Status: "Cleared for Sale"

**Subscription Groups (for premium):**
- Group Name: "BeeSmart Premium"
- Products: Monthly, Yearly, Family
- Subscription Duration: 1 month / 1 year
- Free Trial: Optional (7 days)
- Grace Period: 16 days (recommended)

---

### STEP 9: Create App Screenshots

**Required Sizes:**
- **6.7" Display (iPhone 14 Pro Max):** 1290x2796
- **6.5" Display (iPhone 11 Pro Max):** 1284x2778
- **5.5" Display (iPhone 8 Plus):** 1242x2208
- **iPad Pro (12.9"):** 2048x2732

**Screenshots to Capture:**
1. Home screen with 3D bee avatars
2. Word upload screen
3. Quiz in progress with definition
4. Results/achievements screen
5. Avatar selection screen
6. (Optional) IAP purchase screen

**Tools:**
- Use iOS Simulator in Xcode
- Cmd+S to save screenshot
- Or use real device with Cmd+Shift+4 (QuickTime)

**Design:**
- Include device frame (optional)
- Add captions explaining features
- Show happy kids using app (optional)

---

### STEP 10: Write App Store Metadata

#### App Name:
```
BeeSmart Spelling Bee
```

#### Subtitle (30 chars):
```
Fun Spelling Practice for Kids
```

#### Promotional Text (170 chars):
```
🐝 Make spelling fun! Upload word lists, practice with voice, earn bee avatars, and track progress. Perfect for grades 1-5. COPPA compliant & ad-free.
```

#### Description (4000 chars):
```
🐝 **BeeSmart Spelling Bee** - The Fun Way to Master Spelling!

Turn spelling practice into an adventure! BeeSmart Spelling Bee helps kids learn their spelling words through interactive quizzes, voice pronunciation, and adorable 3D bee avatars.

**✨ KEY FEATURES:**

📚 **Easy Word List Upload**
• Import lists from CSV, TXT, or DOCX files
• Scan word lists with your camera (OCR)
• Teacher-created lists ready to go

🎤 **Voice & Audio Support**
• Hear each word pronounced clearly
• Kid-friendly definitions and hints
• Practice at your own pace

🐝 **Collect Bee Avatars**
• Earn Honey Points for correct answers
• Unlock 39 unique 3D bee characters
• Customize your learning experience

📊 **Track Progress**
• View spelling accuracy and streaks
• Celebrate achievements and badges
• Parent dashboard to monitor learning

🎯 **Made for Kids**
• COPPA compliant - no ads or tracking
• Age-appropriate content (grades 1-5)
• Parental controls for safety

🏆 **Educational Benefits:**
• Improves spelling accuracy
• Builds vocabulary
• Enhances reading comprehension
• Boosts confidence

**Perfect for:**
✓ Elementary school students (grades 1-5)
✓ Homeschool families
✓ Teachers creating custom lists
✓ Parents helping with homework

**Safe & Secure:**
• No third-party ads
• COPPA & GDPR compliant
• Privacy-first design
• Parental gate for purchases

Download BeeSmart Spelling Bee today and watch your child's spelling skills soar! 🚀

---

**Privacy Policy:** https://beesmartspelling.app/privacy
**Support:** Contact via app settings or email
**Premium Features:** Optional subscriptions unlock all avatars and advanced features
```

#### Keywords (100 chars):
```
spelling,education,kids,learning,vocabulary,phonics,reading,school,homework,quiz
```

#### Support URL:
```
https://beesmartspelling.app
```

#### Marketing URL:
```
https://beesmartspelling.app
```

#### Privacy Policy URL:
```
https://beesmartspelling.app/privacy
```

---

### STEP 11: Set Up TestFlight (Optional but Recommended)

**Benefits:**
- Test with real users before public release
- Gather feedback and crash reports
- Verify IAP sandbox purchases work

**Steps:**
1. After uploading archive, go to TestFlight tab
2. Add internal testers (up to 100)
3. Add external testers (up to 10,000)
4. Distribute beta to testers
5. Collect feedback

**Test Points:**
- Word upload functionality
- Quiz completion flow
- IAP purchases (sandbox)
- Avatar unlocking
- Permissions (camera, mic, photos)
- Performance on older devices

---

### STEP 12: Build & Archive for App Store

#### A. Prepare Build:
1. Open Xcode project: `npx cap open ios`
2. Select "Any iOS Device (arm64)" as destination
3. Product → Scheme → Edit Scheme → Release configuration
4. Product → Clean Build Folder (Cmd+Shift+K)

#### B. Create Archive:
1. Product → Archive (Cmd+B then Archive)
2. Wait for build to complete (2-5 minutes)
3. Xcode Organizer opens automatically

#### C. Validate Archive:
1. Click "Validate App"
2. Select App Store Connect destination
3. Choose distribution certificate
4. Wait for validation (checks for errors)
5. Fix any issues reported

**Common Issues:**
- Missing icons (add to Assets.xcassets)
- Invalid bundle ID (must match App Store Connect)
- Missing permissions in Info.plist
- Simulator builds (must use real device target)

#### D. Upload to App Store Connect:
1. Click "Distribute App"
2. Select "App Store Connect"
3. Choose "Upload"
4. Select provisioning profile
5. Click "Upload"
6. Wait for upload (5-15 minutes depending on size)

---

### STEP 13: Submit for Review

**After Upload Completes:**

1. Go to App Store Connect → My Apps → BeeSmart Spelling
2. Select version (1.7.0)
3. Fill in "What's New in This Version":
   ```
   🐝 Welcome to BeeSmart Spelling Bee!
   
   • 39 adorable 3D bee avatars to collect
   • Easy word list upload (CSV, TXT, DOCX, images)
   • Voice pronunciation for every word
   • Track progress and earn achievements
   • Parent dashboard for monitoring
   • COPPA compliant - safe for kids
   
   Start your spelling adventure today!
   ```

4. Add build (select from TestFlight builds)
5. App Review Information:
   - **Demo Account Username:** `student_demo`
   - **Demo Account Password:** `REVIEW-ONLY`
   - **Notes:** "Test account pre-loaded with sample words. All features accessible."
   - **Contact Info:** Your email and phone

6. Version Release:
   - **Manually release this version** (recommended)
   - Or: Automatically after approval

7. Click "Submit for Review"

---

### STEP 14: App Review Process

**Timeline:**
- Initial Review: 24-48 hours
- Rejection Response: 24-48 hours after fixes
- Approval: Immediate availability or manual release

**Common Rejection Reasons:**
1. **Missing demo account** - Always provide working credentials
2. **IAP issues** - Products must be "Cleared for Sale"
3. **Privacy policy** - Must be accessible and accurate
4. **Kids category violations** - No ads, tracking, or unsafe content
5. **Metadata mismatch** - Screenshots must match actual app

**If Rejected:**
1. Read rejection reason carefully
2. Fix the specific issue mentioned
3. Increment build number
4. Upload new archive
5. Respond in Resolution Center
6. Resubmit

---

## 📋 PRE-SUBMISSION CHECKLIST

### Xcode Configuration:
- [ ] Info.plist has all required permissions with kid-friendly descriptions
- [ ] Bundle ID matches App Store Connect: `com.beesmart.spelling`
- [ ] Version 1.7.0, Build 1 (or higher)
- [ ] Deployment target iOS 15.0
- [ ] All app icons added (1024x1024 and device sizes)
- [ ] Launch screen configured
- [ ] Signing configured with Distribution certificate
- [ ] In-App Purchase capability enabled

### Code Verification:
- [ ] IAP plugin (BeeSmartIAPPlugin.swift) integrated
- [ ] Server URL points to production: `https://beesmartspelling.app`
- [ ] Backend deployed to Railway and responding
- [ ] Health endpoint returns v1.7: `https://beesmartspelling.app/health`
- [ ] IAP verification endpoint working: `/api/iap/verify/apple`

### App Store Connect:
- [ ] App listing created with com.beesmart.spelling
- [ ] All 20+ IAP products configured and "Cleared for Sale"
- [ ] Avatar names end with " Avatar" (Apple compliance)
- [ ] Screenshots uploaded for all required sizes
- [ ] App description, keywords, categories filled
- [ ] Privacy policy URL accessible
- [ ] Age rating completed (4+)
- [ ] Demo account credentials: student_demo / REVIEW-ONLY

### Testing:
- [ ] App installs and launches on real iPhone
- [ ] Word upload works (CSV, TXT)
- [ ] Quiz flow completes successfully
- [ ] Voice pronunciation works
- [ ] IAP purchases work in sandbox mode
- [ ] IAP restore works correctly
- [ ] Camera permission works (if requesting)
- [ ] No crashes or freezes
- [ ] Accessibility features work (VoiceOver)

### Final Checks:
- [ ] Archive validates without errors
- [ ] Upload to App Store Connect successful
- [ ] Build appears in TestFlight section
- [ ] All metadata fields complete
- [ ] "Submit for Review" button enabled

---

## 🚨 CRITICAL REMINDERS

### ⚠️ Apple Compliance:
1. **All IAP avatar names MUST end with " Avatar"** - Apple trademark requirement
2. **Demo account must work** - Reviewers will test with `student_demo`
3. **IAP products must be "Cleared for Sale"** - Not just "Ready to Submit"
4. **Privacy policy must be accessible** - Link must work from app
5. **Kids category rules** - No ads, no tracking, parental gates required

### ⚠️ Common Mistakes:
- ❌ Simulator builds (must use "Any iOS Device")
- ❌ Development certificates (must use Distribution)
- ❌ Incomplete IAP products
- ❌ Missing icon sizes
- ❌ Invalid bundle ID
- ❌ Expired provisioning profiles

---

## 📞 TROUBLESHOOTING

### Build Fails:
```bash
cd /Users/jalex0823/Dropbox/BeeSmartSpellingBeeApp/mobile
rm -rf ios/App/Pods
rm -rf ios/App/Podfile.lock
npx cap sync ios
cd ios/App
pod install
npx cap open ios
```

### Archive Upload Fails:
- Check Internet connection
- Verify Xcode is latest version
- Try Transporter app instead
- Check App Store Connect status page

### IAP Not Working:
- Verify products are "Cleared for Sale"
- Check bundle ID matches exactly
- Test with sandbox account (Settings → App Store → Sandbox Account)
- Wait 2-4 hours after creating products

---

## 🎯 NEXT IMMEDIATE STEPS

1. **Update Info.plist** - Add missing permission keys (see Step 1)
2. **Open in Xcode** - `cd mobile && npx cap open ios`
3. **Configure Signing** - Select your Apple Developer Team
4. **Create Archive** - Product → Archive
5. **Upload** - Distribute App → App Store Connect
6. **Submit for Review** - Fill metadata and submit

---

## ✅ SUCCESS CRITERIA

**You'll know you're ready when:**
- ✅ Archive validates without errors
- ✅ Upload completes successfully
- ✅ Build appears in App Store Connect
- ✅ All IAP products show "Cleared for Sale"
- ✅ Demo account works when tested
- ✅ App launches on real device
- ✅ No crashes in normal usage
- ✅ IAP sandbox purchases work

---

**Estimated Time to Complete:** 2-4 hours (first time), 30-60 minutes (subsequent updates)

**Questions?** Refer to:
- `/mobile/IOS_PACKAGING.md` - Capacitor build guide
- `/mobile/STORE_CHECKLIST.md` - Store submission guide
- `APP_STORE_SMOKE_TEST_REPORT.md` - Testing checklist

---

🐝 **Good luck with your App Store submission!**
