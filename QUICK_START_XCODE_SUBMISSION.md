# 🚀 BeeSmart - Quick Xcode Submission Steps

## ✅ COMPLETED:
1. ✅ Info.plist updated with all required permissions
2. ✅ App category set to Education
3. ✅ Privacy manifest added (iOS 17+)
4. ✅ Camera, microphone, photo library permissions with kid-friendly descriptions
5. ✅ App Transport Security configured for beesmartspelling.app
6. ✅ Background audio mode enabled
7. ✅ IAP plugin ready (BeeSmartIAPPlugin.swift)

---

## 🎯 YOUR NEXT 3 STEPS:

### STEP 1: Open in Xcode (2 minutes)
```bash
cd /Users/jalex0823/Dropbox/BeeSmartSpellingBeeApp/mobile
npx cap sync ios
npx cap open ios
```

### STEP 2: Configure Signing (5 minutes)
In Xcode:
1. Select "App" target (top left)
2. Go to "Signing & Capabilities" tab
3. Check "Automatically manage signing"
4. Select your Apple Developer Team from dropdown
5. Verify Bundle ID shows: `com.beesmart.spelling`
6. Set Version to: `1.7.0`
7. Set Build to: `1`

### STEP 3: Create Archive (10 minutes)
1. In Xcode, select "Any iOS Device (arm64)" from device dropdown (NOT Simulator)
2. Menu: Product → Clean Build Folder (Cmd+Shift+K)
3. Menu: Product → Archive (wait 2-5 minutes)
4. When Organizer opens:
   - Click "Validate App" (checks for errors)
   - If validation passes, click "Distribute App"
   - Select "App Store Connect"
   - Click "Upload"
   - Wait for upload to complete

---

## 📋 BEFORE UPLOADING - VERIFY:

### In Xcode:
- [ ] Bundle ID: `com.beesmart.spelling`
- [ ] Version: `1.7.0`
- [ ] Build: `1` (or higher)
- [ ] iOS Deployment Target: 15.0
- [ ] Signing Team: Your Apple Developer account
- [ ] Build target: "Any iOS Device (arm64)" - NOT Simulator

### In Code:
- [ ] Backend URL in capacitor.config.ts: `https://beesmartspelling.app`
- [ ] Health endpoint working: https://beesmartspelling.app/health returns v1.7
- [ ] IAP endpoints ready: `/api/iap/verify/apple` and `/api/iap/restore`

---

## 🏪 APP STORE CONNECT - AFTER UPLOAD:

### 1. Create App Listing (if not done):
- Go to: https://appstoreconnect.apple.com
- Click "My Apps" → "+" → "New App"
- Bundle ID: `com.beesmart.spelling`
- Name: BeeSmart Spelling Bee
- Primary Language: English (U.S.)

### 2. Fill Required Info:
```
Category: Education
Age Rating: 4+ (complete questionnaire)
Price: Free (with In-App Purchases)
Privacy Policy: https://beesmartspelling.app/privacy
```

### 3. Configure IAP Products:
**All avatar names MUST end with " Avatar"** (Apple requirement)

Example products:
```
com.beesmart.avatar.superbee → "Super Bee Avatar" - $0.99
com.beesmart.avatar.queen → "Queen Bee Avatar" - $0.99
beesmart.premium.monthly → "Premium Monthly" - $4.99
```

Mark ALL products as "Cleared for Sale"

### 4. Add Screenshots:
Required sizes:
- 6.7" Display (iPhone 14 Pro Max): 1290x2796
- iPad Pro (12.9"): 2048x2732

Screenshots to capture:
1. Home screen with 3D bees
2. Word upload screen
3. Quiz in progress
4. Results/achievements
5. Avatar selection

### 5. Submit for Review:
- Add build (the one you just uploaded)
- Demo Account: `student_demo` / `REVIEW-ONLY`
- What's New: "Initial release - spelling practice with 3D bee avatars"
- Click "Submit for Review"

---

## ⚠️ COMMON ISSUES & FIXES:

### "No signing identity found"
**Fix:** Go to Xcode Preferences → Accounts → Download Manual Profiles

### "The bundle identifier is invalid"
**Fix:** Must match exactly in Xcode AND App Store Connect: `com.beesmart.spelling`

### Archive menu is grayed out
**Fix:** Select "Any iOS Device (arm64)" NOT a simulator or specific device

### "Missing compliance"
**Fix:** In App Store Connect, under "App Information", set ITSAppUsesNonExemptEncryption to No

### IAP products not showing
**Fix:** Wait 2-4 hours after creating products, must be "Cleared for Sale"

---

## 📞 TROUBLESHOOTING COMMANDS:

### Clean and rebuild Capacitor:
```bash
cd /Users/jalex0823/Dropbox/BeeSmartSpellingBeeApp/mobile
rm -rf ios/App/Pods ios/App/Podfile.lock
npx cap sync ios
cd ios/App && pod install
npx cap open ios
```

### Check backend is live:
```bash
curl https://beesmartspelling.app/health
# Should return: {"status":"ok","version":"1.7"}
```

### Verify IAP endpoint:
```bash
curl -X POST https://beesmartspelling.app/api/iap/verify/apple \
  -H "Content-Type: application/json" \
  -d '{"receipt":"test"}'
# Should return 200 or 400 (not 500/404)
```

---

## 🎯 SUCCESS CHECKLIST:

- [ ] Info.plist updated ✅ (DONE)
- [ ] Xcode project opens without errors
- [ ] Signing configured with your Apple Developer team
- [ ] Archive validates without errors
- [ ] Upload to App Store Connect completes
- [ ] Build appears in App Store Connect (wait 5-15 min)
- [ ] All IAP products created and "Cleared for Sale"
- [ ] Screenshots uploaded
- [ ] App metadata filled (description, keywords, etc.)
- [ ] Demo account works: student_demo / REVIEW-ONLY
- [ ] Privacy policy accessible: https://beesmartspelling.app/privacy
- [ ] Submitted for review

---

## 📚 FULL DOCUMENTATION:

For detailed instructions, see:
- `XCODE_APP_STORE_SUBMISSION_GUIDE.md` - Complete step-by-step guide
- `APP_STORE_SMOKE_TEST_REPORT.md` - Testing checklist
- `/mobile/IOS_PACKAGING.md` - Capacitor build instructions

---

## ⏱️ ESTIMATED TIME:

- **Xcode Setup:** 10 minutes
- **Archive & Upload:** 15-20 minutes  
- **App Store Connect Setup:** 30-60 minutes (first time)
- **Review Wait:** 24-48 hours

**Total:** ~1-2 hours to submit, 1-2 days for Apple review

---

🐝 **You're ready to submit! Start with STEP 1 above.**
