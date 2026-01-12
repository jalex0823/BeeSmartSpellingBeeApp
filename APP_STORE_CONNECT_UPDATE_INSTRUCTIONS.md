# App Store Connect Update Instructions - January 2026

## Quick Checklist

- [ ] Update demo account credentials
- [ ] Add EULA link to app description
- [ ] Remove price references from all IAP metadata
- [ ] Update promotional images (fix text readability)

---

## 1. Update Demo Account (Guideline 2.1)

**Location**: App Store Connect → Your App → App Information → Demo Account

**Old Credentials** (Invalid):
- Username: `jalex0823@me.com`
- Password: `Galaga911!`

**New Credentials** (Valid):
- Username: `BigDaddy2`
- Password: `Aja123!!`

**Steps**:
1. Go to App Store Connect
2. Select your app
3. Go to "App Information"
4. Scroll to "Demo Account" section
5. Update username and password
6. Save changes

---

## 2. Add EULA Link (Guideline 3.1.2)

**Location**: App Store Connect → Your App → App Information → App Description

**Option A: Add to App Description**
1. Go to App Store Connect → Your App → App Information
2. Edit "App Description"
3. Add at the end:
   ```
   Terms of Use: https://beesmartspelling.app/terms
   Privacy Policy: https://beesmartspelling.app/privacy
   ```

**Option B: Add to EULA Field** (if available)
1. Go to App Store Connect → Your App → App Information
2. Look for "EULA" or "Terms of Use" field
3. Enter: `https://beesmartspelling.app/terms`

**Verification**:
- ✅ EULA page is live: https://beesmartspelling.app/terms
- ✅ Contains all required subscription information
- ✅ Includes developer contact information

---

## 3. Remove Price References from IAP Metadata (Guideline 2.3.2)

**Location**: App Store Connect → Your App → Features → In-App Purchases

**Affected Products** (All need review):
- O Bee Avatar, Plumber Bee Avatar, Rocker Bee Avatar, Robo Bee Avatar
- Techno Bee Avatar, Sea Bee Avatar, Selfie Bee Avatar, Singer Bee Avatar
- Super Bee Avatar, Space Bee Avatar, Explorer Bee Avatar, Umpire Bee Avatar
- Franken Bee Avatar, Ware Bee Avatar, Honey Comb Bee Avatar, X-Ray Bee Avatar
- Inventor Bee Avatar, lumberjack_bee, Vamp Bee Avatar, Knight Bee Avatar
- BeeSmart Premium Monthly, Mascot Bee Avatar, Motor Bee Avatar
- Nurse Bee Avatar, Al Bee Avatar, Brother Bee Avatar, Buda Bee Avatar
- Cool Bee Avatar, Builder Bee Avatar, Cutie Bee Avatar, Buzz Bee Avatar
- Detective Bee Avatar, Diva Bee Avatar, Doc Bee Avatar, Professor Bee Avatar
- Queen Bee Avatar

**What to Remove**:
- ❌ Any mention of price (e.g., "$0.99", "99¢", "Free")
- ❌ Price comparisons
- ❌ Discount percentages

**Display Name Rules**:
- Maximum 30 characters
- No price references
- Example: "Cool Bee Avatar" ✅ (not "Cool Bee Avatar - $0.99" ❌)

**Description Rules**:
- Maximum 45 characters
- No price references
- Focus on features/benefits

**Steps for Each IAP**:
1. Go to App Store Connect → Your App → Features → In-App Purchases
2. Select each IAP product
3. Review "Display Name" - remove price references
4. Review "Description" - remove price references
5. Review "Promotional Image" - remove price references
6. Save changes

---

## 4. Update Promotional Images (Guideline 2.3.2)

**Location**: App Store Connect → Your App → Features → In-App Purchases → [Each Product] → Promotional Image

**Requirements**:
- ✅ Text must be large and readable (minimum 20pt font size)
- ✅ High contrast between text and background
- ✅ Text must not be compressed or pixelated
- ✅ Test readability on actual device screens

**Image Specifications**:
- Format: PNG or JPEG
- Recommended: 1242 x 2208 pixels (iPhone) or 2048 x 2732 pixels (iPad)
- Text size: Minimum 20pt (scaled for image resolution)
- Contrast: White text on dark background OR dark text on light background

**What to Fix**:
- ❌ Small text that's hard to read
- ❌ Low contrast text
- ❌ Compressed/pixelated text
- ❌ Text that's too close to edges

**Steps**:
1. Go to each IAP product
2. Review "Promotional Image"
3. If text is too small or hard to read, replace with new image
4. Ensure all text meets readability requirements
5. Save changes

**Tips**:
- Use bold, sans-serif fonts (e.g., Arial, Helvetica)
- Test images on actual iPhone/iPad screens
- Consider using icons/symbols instead of text where possible
- Keep text minimal - focus on product name/benefit

---

## 5. Verification Checklist

Before resubmitting, verify:

- [ ] Demo account credentials updated and tested
- [ ] EULA link added to app description or EULA field
- [ ] All IAP display names reviewed (no price references)
- [ ] All IAP descriptions reviewed (no price references)
- [ ] All promotional images reviewed (readable text)
- [ ] Test with new demo account in TestFlight
- [ ] Verify EULA link is accessible from app
- [ ] Verify Restore Purchases button is visible
- [ ] Test IAP purchase flow without registration

---

## After Updates

1. **Save all changes** in App Store Connect
2. **Build new version** with code fixes (already done)
3. **Submit for review** with updated metadata
4. **Include notes** in review submission:
   - "Fixed: Removed registration requirement for IAP purchases (Guideline 5.1.1)"
   - "Fixed: Updated demo account credentials (Guideline 2.1)"
   - "Fixed: Added EULA link to app description (Guideline 3.1.2)"
   - "Fixed: Removed price references from IAP metadata (Guideline 2.3.2)"
   - "Fixed: Updated promotional images for readability (Guideline 2.3.2)"

---

## Support

If you need help with any of these steps:
- App Store Connect Help: https://help.apple.com/app-store-connect/
- Apple Developer Support: https://developer.apple.com/contact/
