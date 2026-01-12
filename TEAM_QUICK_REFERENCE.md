# Quick Reference - Apple Rejection Fixes for Team

**TL;DR**: ✅ **YES, NEW XCODE BUILD REQUIRED** - Info.plist was changed

---

## 🎯 What Changed

### Code Changes (Already Done ✅)
1. **Info.plist**: Removed background audio declaration
2. **Main Menu**: Added "Avatars" tile for IAP shop entry
3. **CSS**: Added gold theme styling for Avatars tile
4. **Navigation**: Added handler to navigate to avatar picker

### What Team Needs to Do ⚠️

#### 1. Create New Xcode Build (REQUIRED)
- Pull latest code: `git pull origin main`
- Open in Xcode: `npx cap sync ios && cd ios/App && open App.xcworkspace`
- **Increment build number** (e.g., 1 → 2)
- Create archive and upload to App Store Connect

#### 2. Replace App Icons (REQUIRED)
- Replace all icons in `mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/`
- Start with 1024×1024 master icon
- Generate all required sizes

#### 3. Capture iPad Screenshots (REQUIRED)
- Use iPad Pro (12.9-inch) simulator
- Capture: Home screen, Avatar shop, Quiz, Results
- Upload to App Store Connect

#### 4. Verify App Store Connect
- Paid Apps Agreement: Must be Active
- IAP Products: Must be "Cleared for Sale"
- Add reviewer notes with navigation steps

---

## 📋 Build Checklist

- [ ] Pull latest code
- [ ] Replace app icons
- [ ] Open in Xcode
- [ ] Increment build number
- [ ] Create archive
- [ ] Upload to App Store Connect
- [ ] Capture iPad screenshots
- [ ] Upload screenshots
- [ ] Verify IAP products
- [ ] Update reviewer notes
- [ ] Test in TestFlight
- [ ] Resubmit for review

---

## 📁 Key Files Changed

- `mobile/ios/App/App/Info.plist` ← **REQUIRES NEW BUILD**
- `templates/unified_menu.html` ← Web template (auto-included if bundled)

**Commit**: `5d12eb3`

---

## 📖 Full Details

See `FREELANCE_TEAM_UPDATE_BREAKDOWN.md` for complete instructions.
