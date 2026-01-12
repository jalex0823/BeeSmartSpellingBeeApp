# Final Apple Review Actions - January 12, 2026

## Quick Action Checklist

### ✅ Code Fixes Completed
- [x] Splash screens regenerated with BeeSmart branding (Flutter logo removed)
- [x] Info.plist verified (UIBackgroundModes commented out)
- [x] IAP registration requirement removed
- [x] Documentation created

### ⚠️ Manual Actions Required (Must Complete Before Resubmission)

#### 1. Xcode Actions (5 minutes)
- [ ] **Remove Background Modes**:
  - Open `mobile/ios/App/App.xcodeproj` in Xcode
  - Select "App" target → "Signing & Capabilities" tab
  - Remove "Background Modes" capability
  - Clean build folder (Shift+Cmd+K)
  - Rebuild project

- [ ] **Verify Splash Screens**:
  - Launch app in simulator
  - Verify splash screen shows BeeSmart logo (not Flutter)
  - If Flutter logo still appears, rebuild from clean state

#### 2. App Store Connect Actions (30-60 minutes)
- [ ] **Sign Paid Apps Agreement**:
  - Go to: App Store Connect → Agreements, Tax, and Banking
  - Find "Paid Applications Agreement"
  - Complete agreement (accept, tax info, banking info)
  - Wait for "Active" status (24-48 hours)

- [ ] **Capture iPad Screenshots**:
  - Open Xcode → Select iPad Pro (12.9-inch) simulator
  - Run app and navigate through:
    - Home screen with Avatars tile
    - Avatar picker showing IAP products
    - Quiz interface
    - Dashboard/profile screen
  - Capture screenshots (Cmd+S)
  - Upload to App Store Connect → Screenshots → iPad Pro (12.9-inch)

- [ ] **Update Demo Account** (if needed):
  - App Store Connect → App Information → Demo Account
  - Username: `BigDaddy2`
  - Password: `Aja123!!`

#### 3. Testing (15 minutes)
- [ ] **Test IAP in Sandbox**:
  - Create sandbox test account
  - Sign out of production App Store on test device
  - Test avatar purchase flow
  - Verify purchases work correctly

- [ ] **Verify Splash Screen**:
  - Launch app
  - Confirm BeeSmart logo appears (not Flutter)
  - Check launch screen looks correct

---

## Response Text for App Store Connect

Copy and paste this into your App Review response:

```
ISSUE 1 - GUIDELINE 2.1.0 (Flutter Icon):

We have identified and fixed the Flutter icon issue. The Flutter logo was appearing in the splash screen assets. We have:

1. Regenerated all splash screen images with BeeSmart branding
2. Verified Launch Screen storyboard references correct assets
3. Confirmed all app icons are BeeSmart branded
4. Rebuilt the app to ensure cached assets are cleared

The Flutter logo will no longer appear. All visual assets now use BeeSmart branding exclusively.

ISSUE 2 - GUIDELINE 2.3.3 (iPad Screenshots):

We have captured new, genuine iPad screenshots using the iPad Pro (12.9-inch) simulator in Xcode. The new screenshots:

- Show actual iPad interface (not stretched iPhone images)
- Proper resolution (2048 x 2732 pixels for iPad Pro 12.9-inch)
- Display main app features (Home screen, Avatar Picker with IAP products, Quiz interface, Dashboard)
- Meet Apple's screenshot requirements

New screenshots have been uploaded to App Store Connect.

ISSUE 3 - GUIDELINE 2.5.4 (Background Modes):

We have removed the Background Modes capability from the Xcode project. The app does not require persistent background audio - all audio is in-app only (voice announcements during quizzes, sound effects during active use).

Changes made:
1. Removed "Background Modes" from Xcode Capabilities tab
2. Verified Info.plist does not contain UIBackgroundModes key
3. Cleaned build folder and rebuilt project

The app now correctly declares only the capabilities it actually uses.

IAP PURCHASE NAVIGATION:

To locate in-app purchases (bee avatars):
1. Launch app → Home screen appears
2. Tap "Avatars" tile (🐝 icon, gold/yellow theme, prominently displayed on home screen)
3. Avatar picker opens showing all available avatars
4. Locked avatars display lock icon and purchase option
5. Tap any locked avatar → Tap "Unlock" or purchase button
6. Native StoreKit purchase flow initiates

IAP TROUBLESHOOTING:

If reviewers encounter "Purchase could not be completed" errors:
1. Paid Apps Agreement is now active in App Store Connect
2. All IAP products are "Ready to Submit" status
3. Please use sandbox test account (not production Apple ID)
4. Sign out of production App Store before testing

DEMO ACCOUNT:
Username: BigDaddy2
Password: Aja123!!

All fixes have been implemented and tested. The app is ready for review.
```

---

## Priority Order

1. **CRITICAL**: Sign Paid Apps Agreement (blocks IAP testing)
2. **HIGH**: Remove Background Modes in Xcode (review compliance)
3. **HIGH**: Capture iPad screenshots (review compliance)
4. **MEDIUM**: Test IAP flow in sandbox
5. **MEDIUM**: Verify splash screen shows BeeSmart logo

---

## Files Modified

- ✅ `mobile/ios/App/App/Assets.xcassets/Splash.imageset/*.png` - Regenerated with BeeSmart logo
- ✅ `APPLE_REVIEW_RESPONSE_JAN12_FINAL.md` - Comprehensive response document
- ✅ `FINAL_APPLE_REVIEW_ACTIONS.md` - This action checklist

---

## After Completing All Actions

1. **Build new version** in Xcode
2. **Create TestFlight build**
3. **Test all fixes** in TestFlight
4. **Submit for review** with response text above
5. **Monitor** App Store Connect for review status

---

## Support Resources

- **Xcode Background Modes**: See `XCODE_BACKGROUND_MODES_REMOVAL_GUIDE.md`
- **Paid Apps Agreement**: See `PAID_APPS_AGREEMENT_GUIDE.md`
- **iPad Screenshots**: See `APPLE_REVIEW_RESPONSE_JAN12_2026.md` (screenshot section)
- **IAP Navigation**: See `APPLE_REVIEW_RESPONSE_JAN12_2026.md` (IAP section)
