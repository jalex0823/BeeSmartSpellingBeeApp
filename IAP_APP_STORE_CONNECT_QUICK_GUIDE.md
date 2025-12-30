# App Store Connect IAP Quick Guide
**Date**: December 29, 2025  
**Status**: Product IDs Fixed ✅

---

## ✅ FIXES COMPLETED

### 1. Product ID Format (avatar_skus.py)
- **Before**: `com.beesmart.avatar.brother-bee` (hyphens)
- **After**: `com.beesmart.avatar.brother_bee` (underscores)
- **Status**: ✅ Now matches App Store Connect

### 2. Diva Bee Product ID (avatar_catalog.py)
- **Before**: `beesmart.avatar.diva_bee`
- **After**: `beesmart.avatar.diva_bee2`
- **Status**: ✅ Now matches App Store Connect

### 3. Subscription Product ID
- **Product ID**: `beesmart.premium.monthly`
- **Status**: ✅ Perfect match (no changes needed)

---

## 📱 YOUR APP STORE CONNECT STATUS

### Subscription (1 product)
- **BeeSmart Premium – Monthly**
- Product ID: `beesmart.premium.monthly`
- Status: 🔴 Developer Action Needed
- **Why**: Must be submitted WITH an app version

### Avatar IAPs (37 products)
- All showing: 🔴 Developer Action Needed
- **Issue**: Includes 5 FREE avatars that shouldn't have IAP products
- **Action**: Delete free avatar IAPs OR complete all 37

---

## 🎯 IMMEDIATE ACTIONS

### Action 1: Upload Archive (HIGH PRIORITY)
```
File: BeeSmartApp-v9.0-Build9-5Fixes.xcarchive
Location: ~/Desktop/

Steps:
1. Double-click archive to open in Xcode Organizer
2. Click "Distribute App"
3. Select "App Store Connect"
4. Follow upload wizard
5. Wait for processing (10-30 minutes)
```

### Action 2: Fix Subscription Status (HIGH PRIORITY)
```
Why: Subscriptions MUST be attached to an app version

Steps:
1. Go to App Store Connect → BeeSmart Spelling
2. Select your app version (or create new one)
3. Scroll to "In-App Purchases and Subscriptions"
4. Click + (Add)
5. Search: BeeSmart Premium – Monthly
6. Click Add
7. Save version
```

### Action 3: Clean Up Avatar IAPs (MEDIUM PRIORITY)

**Option A: Delete Free Avatar IAPs** ⭐ RECOMMENDED

Delete these 5 products (they're free avatars):
- [ ] `beesmart.avatar.brother_bee`
- [ ] `beesmart.avatar.builder_bee`
- [ ] `beesmart.avatar.cool_bee`
- [ ] `beesmart.avatar.detective_bee`
- [ ] `beesmart.avatar.explorer_bee`

**How to delete**:
1. Go to each IAP product page
2. Scroll to bottom
3. Click "Delete In-App Purchase"
4. Confirm

**Option B: Complete All 37 IAPs**

For each avatar product:
- [ ] Add screenshot (640×920px, opaque PNG/JPG)
- [ ] Add description from avatar_catalog.py
- [ ] Verify price tier ($0.99 or $1.99)
- [ ] Save changes
- [ ] Attach to app version when submitting

---

## 📋 AVATAR IAP CHECKLIST (34 Purchasable)

### Earn or Buy ($0.99) - 7 avatars
- [ ] Buzz Bee (`beesmart.avatar.buzz_bee`)
- [ ] Cutie Bee (`beesmart.avatar.cutie_bee`)
- [ ] Knight Bee (`beesmart.avatar.knight_bee`)
- [ ] Professor Bee (`beesmart.avatar.professor_bee`)
- [ ] Rocker Bee (`beesmart.avatar.rocker_bee`)
- [ ] Selfie Bee (`beesmart.avatar.selfie_bee`)
- [ ] Vamp Bee (`beesmart.avatar.vamp_bee`)

### Premium ($0.99-$1.99) - 27 avatars
- [ ] Al Bee (`beesmart.avatar.al_bee`) - $1.99
- [ ] Buda Bee (`beesmart.avatar.buda_bee`) - $0.99
- [ ] Diva Bee (`beesmart.avatar.diva_bee2`) - $1.99 ⚠️ Note: diva_bee2
- [ ] Doc Bee (`beesmart.avatar.doc_bee`) - $0.99
- [ ] Fairy Bee (`beesmart.avatar.fairy_bee`) - $1.99
- [ ] Franken Bee (`beesmart.avatar.franken_bee`) - $0.99
- [ ] Gamer Bee (`beesmart.avatar.gamer_bee`) - $1.99
- [ ] Honey Comb (`beesmart.avatar.honey_comb`) - $0.99
- [ ] Inventor Bee (`beesmart.avatar.inventor_bee`) - $1.99
- [ ] J Rock Bee (`beesmart.avatar.j_rock_bee`) - $0.99
- [ ] Lumberjack Bee (`beesmart.avatar.lumberjack_bee`) - $1.99
- [ ] Motor Bee (`beesmart.avatar.motor_bee`) - $0.99
- [ ] Nurse Bee (`beesmart.avatar.nurse_bee`) - $1.99
- [ ] O Bee (`beesmart.avatar.o_bee`) - $0.99
- [ ] Plumber Bee (`beesmart.avatar.plumber_bee`) - $1.99
- [ ] Queen Bee (`beesmart.avatar.queen_bee`) - $1.99
- [ ] Robo Bee (`beesmart.avatar.robo_bee`) - $1.99
- [ ] Sea Bee (`beesmart.avatar.sea_bee`) - $0.99
- [ ] Singer Bee (`beesmart.avatar.singer_bee`) - $0.99
- [ ] Space Bee (`beesmart.avatar.space_bee`) - $0.99
- [ ] Super Bee (`beesmart.avatar.super_bee`) - $0.99
- [ ] Techno Bee (`beesmart.avatar.techno_bee`) - $1.99
- [ ] Umpire Bee (`beesmart.avatar.umpire_bee`) - $1.99
- [ ] Ware Bee (`beesmart.avatar.ware_bee`) - $1.99
- [ ] Xray Bee (`beesmart.avatar.xray_bee`) - $1.99
- [ ] Yeti Bee (`beesmart.avatar.yeti_bee`) - $1.99
- [ ] Zom Bee (`beesmart.avatar.zom_bee`) - $1.99

---

## 🧪 SANDBOX TESTING READINESS

### Issue #1: Subscription Restore ✅ READY
- [x] Product ID matches code
- [x] Backend `/api/iap/restore` endpoint works
- [x] Native BeeSmartIAPPlugin.swift ready
- [x] JavaScript bridge ready
- [ ] Upload build to ASC
- [ ] Attach subscription to version
- [ ] Create sandbox test account
- [ ] Test on device

### Issue #2: Avatar Purchases ⚠️ NEEDS WORK
- [x] Product IDs fixed (underscores)
- [x] Backend `/api/iap/verify` endpoint works
- [x] Native plugin ready
- [ ] Avatar purchase UI NOT implemented
- [ ] Need buy buttons in avatar picker
- [ ] See: `IAP_SANDBOX_TESTING_CHECKLIST_40_AVATARS.md` for implementation

---

## 📸 SCREENSHOT REQUIREMENTS

### Subscription Screenshots
- **Size**: 1242 × 2208 pixels (iPhone 6.5" Display)
- **Format**: PNG or JPG (opaque, no transparency)
- **Quantity**: At least 1 required
- **Show**: Subscription benefits, premium features, value prop

### Avatar IAP Screenshots
- **Size**: 640 × 920 pixels
- **Format**: PNG or JPG (opaque, no transparency)
- **Quantity**: At least 1 per product
- **Show**: Avatar preview, unlocked state, clear visual

---

## 🚀 SUBMISSION WORKFLOW

### Step 1: Prepare Build
- [x] Archive created: BeeSmartApp-v9.0-Build9-5Fixes.xcarchive
- [ ] Upload to App Store Connect
- [ ] Wait for processing

### Step 2: Attach IAPs to Version
- [ ] Attach subscription: BeeSmart Premium – Monthly
- [ ] Attach avatar IAPs (if using Option B above)
- [ ] Verify all attached products

### Step 3: Complete Version Info
- [ ] Screenshots (app screenshots, not IAP)
- [ ] Description
- [ ] Keywords
- [ ] Support URL
- [ ] Privacy Policy URL
- [ ] App Review notes

### Step 4: Submit for Review
- [ ] Click "Submit for Review"
- [ ] Wait for status change:
  - Developer Action Needed → Waiting for Review → In Review → Ready to Sell

---

## ⚠️ IMPORTANT NOTES

### About "Developer Action Needed"
- **Subscription**: MUST be attached to app version before submission
- **Avatar IAPs**: Can be submitted separately OR with app version
- **Status clears**: Once attached to version and submitted

### About Sandbox Testing
- **Subscription restore**: Can test NOW (after upload + sandbox account)
- **Avatar purchases**: Need UI implementation first
- **Sandbox account**: Settings → App Store → Sandbox Account (NOT Apple ID)

### About Product IDs
- ✅ **Cannot be changed** after creation in App Store Connect
- ✅ **Code now matches** App Store Connect (underscores)
- ⚠️ **Diva Bee exception**: ASC has `diva_bee2`, code now matches

---

## 📞 TROUBLESHOOTING

### "Cannot upload archive"
- Check code signing settings
- Verify provisioning profile
- Try: Clean Build Folder (Cmd+Shift+K)

### "Subscription still shows Developer Action Needed"
- Must attach to app version first
- Cannot submit subscription alone
- Wait until version is submitted

### "Product ID not found in sandbox"
- Wait 1-2 hours after creating product
- Sign out/in to sandbox account
- Restart app

---

## 📚 REFERENCE FILES

- **Full Checklist**: `IAP_SANDBOX_TESTING_CHECKLIST_40_AVATARS.md`
- **Avatar Catalog**: `avatar_catalog.py` (40 avatars)
- **SKU Mapping**: `avatar_skus.py` (Product ID generation)
- **Native Plugin**: `mobile/ios/App/App/BeeSmartIAPPlugin.swift`
- **JS Bridge**: `static/js/native-iap-bridge.js`
- **Backend**: `AjaSpellBApp.py` (lines 1280-1304, 9680-9950)

---

**Last Updated**: December 29, 2025  
**Next Review**: After uploading build to App Store Connect
