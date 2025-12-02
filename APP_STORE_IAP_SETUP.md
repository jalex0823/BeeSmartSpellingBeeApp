# App Store Connect - In-App Purchase Setup Guide
**Last Updated**: November 13, 2025

## ⚠️ CRITICAL: Current Pricing Structure

Based on `avatar_catalog.py` programmatic pricing override (verified Nov 13, 2025):

### FREE Avatars (6) - No IAP needed
- Brother Bee, Builder Bee, Cool Bee, Detective Bee, Explorer Bee, Mascot Bee

### $0.99 Avatars (11) - Price Tier 1
| Avatar Name | Product ID | Unlock Points |
|-------------|-----------|---------------|
| Doctor Bee | `com.beesmart.avatar.doctor_bee` | 2,000 |
| Buzz Bee | `com.beesmart.avatar.buzz_bee` | 3,000 |
| Knight Bee | `com.beesmart.avatar.knight_bee` | 4,000 |
| Anxious Bee | `com.beesmart.avatar.anxious_bee` | 5,000 |
| Selfie Bee | `com.beesmart.avatar.selfie_bee` | 5,000 |
| Monster Bee | `com.beesmart.avatar.monster_bee` | 6,000 |
| Rocker Bee | `com.beesmart.avatar.rocker_bee` | 8,000 |
| Seabea | `com.beesmart.avatar.seabea` | 10,000 |
| Professor Bee | `com.beesmart.avatar.professor_bee` | 22,000 |
| Vamp Bee | `com.beesmart.avatar.vamp_bee` | 24,000 |
| Franken Bee | `com.beesmart.avatar.franken_bee` | 25,000 |

### $1.99 Avatars (9) - Price Tier 2
| Avatar Name | Product ID | Unlock Points |
|-------------|-----------|---------------|
| Diva Bee | `com.beesmart.avatar.diva_bee` | 12,000 |
| Biker Bee | `com.beesmart.avatar.biker_bee` | 15,000 |
| Astro Bee | `com.beesmart.avatar.astro_bee` | 18,000 |
| Al Bee | `com.beesmart.avatar.al_bee` | 20,000 |
| Zom Bee | `com.beesmart.avatar.zom_bee` | 25,000 |
| Superbee | `com.beesmart.avatar.superbee` | 26,000 |
| Ware Bee | `com.beesmart.avatar.ware_bee` | 27,000 |
| Queen Bee | `com.beesmart.avatar.queen_bee` | 28,000 |
| Robo Bee | `com.beesmart.avatar.robo_bee` | 30,000 |

---

## 📸 Screenshot Requirements

**App Store Connect requires:**
- **Size**: 640×920 pixels (iPhone 6.5" Display portrait)
- **Format**: PNG or JPG (opaque, no transparency/alpha channel)
- **File Size**: Maximum 500KB each
- **Quantity**: 3-10 screenshots recommended

### How to Take Screenshots:
1. Open iOS Simulator (iPhone 15 Pro or similar)
2. Run your app: `Product > Run` in Xcode
3. Navigate to avatar picker
4. Press **Cmd+S** to save screenshot (auto-saves to Desktop)
5. Screenshots are automatically opaque (no transparency)

---

## 📝 Step-by-Step IAP Creation in App Store Connect

### 1. Navigate to In-App Purchases
1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Click **My Apps** > **BeeSmart Spelling**
3. Sidebar: **Monetization** > **In-App Purchases**
4. Click **+** (Create) button

### 2. Select Purchase Type
- Choose **Consumable** (if users can purchase multiple times)
- OR **Non-Consumable** (one-time unlock forever)
- **Recommended**: Non-Consumable (avatars unlock permanently)

### 3. Fill in Product Information

For each avatar, create product with:

**Reference Name**: `[Avatar Name] Avatar` (e.g., "Doctor Bee Avatar")
**Product ID**: `com.beesmart.avatar.[slug]` (e.g., `com.beesmart.avatar.doctor_bee`)

⚠️ **Product ID cannot be changed after creation!**
⚠️ **Reference Name should match Display Name format with "Avatar" suffix**

### 4. Set Price
- Click **Price Schedule**
- **$0.99 avatars**: Select **Tier 1** ($0.99 USD)
- **$1.99 avatars**: Select **Tier 2** ($1.99 USD)
- Price automatically converts to all regions

### 5. Add Localization (English - US)
**Display Name**: `[Avatar Name] Avatar` (e.g., "Doctor Bee Avatar")
**Description**: Use descriptions from avatar_catalog.py

**⚠️ IMPORTANT: All avatar Display Names MUST end with "Avatar" for Apple approval.**

**Example Display Names:**
- "Doctor Bee Avatar"
- "Knight Bee Avatar"  
- "Astro Bee Avatar"
- "SuperBee Avatar"
- "Queen Bee Avatar"

**Example descriptions:**
- **Doctor Bee Avatar**: "Prescribes the right letters, adds careful commas, and sends wobbly words home feeling better!"
- **Diva Bee**: "Loves center stage and dazzling definitions. Every correct word gets a fabulous 'Bravo!'"
- **Queen Bee**: "Ruler of the hive with royal vocabulary and majestic spelling prowess!"

### 6. Upload Screenshot (640×920px)
- Use avatar thumbnail or in-game screenshot
- Drag and drop opaque PNG/JPG
- **Maximum file size**: 500KB

### 7. Review Information
- **Cleared for Sale**: Toggle ON
- **Availability**: All territories
- Click **Save**

### 8. Submit for Review
- Products must be submitted with app version
- Status will show "Waiting for Review" then "Ready to Sell"

---

## 🔄 Bulk Creation Workflow

**For 20 avatars** ($0.99 and $1.99 tiers):

1. Create first avatar as template
2. Note exact steps taken
3. Repeat for remaining 19 avatars
4. Double-check Product IDs match table above
5. Verify prices: 11 @ Tier 1, 9 @ Tier 2

**Estimated time**: 5-10 minutes per avatar = 100-200 minutes total

---

## ✅ Pre-Submission Checklist

Before submitting app for review:

- [ ] All 20 IAP products created
- [ ] Product IDs match app code (underscore format: `doctor_bee`)
- [ ] Prices correct: 11 @ $0.99, 9 @ $1.99
- [ ] Descriptions added (English localization)
- [ ] Screenshots uploaded (640×920px, opaque)
- [ ] All products set to "Cleared for Sale"
- [ ] App binary uploaded (Build 2 ✅)
- [ ] Privacy Policy URL added: https://beesmartspelling.app/privacy.html
- [ ] Age Rating completed
- [ ] Game Center unchecked or configured
- [ ] New opaque screenshots uploaded (delete old transparent ones)

---

## 🐛 Common Issues

**Issue**: "Product ID already exists"
- **Solution**: Use different ID or check if already created

**Issue**: "Image contains alpha channel"
- **Solution**: Use iOS Simulator Cmd+S screenshots (automatically opaque)

**Issue**: "Price tier not available in region"
- **Solution**: Use Tier 1 ($0.99) or Tier 2 ($1.99) - available globally

**Issue**: "Screenshot wrong size"
- **Solution**: Must be exactly 640×920 pixels (use iOS Simulator or resize)

---

## 📱 App Code Integration

Your app already integrates IAPs correctly via `avatar_catalog.py`:

```python
# Lines 665-697 in avatar_catalog.py
DEFAULT_LOCKED_PRICE = 0.99
PREMIUM_199_IDS = {
    "al-bee", "astro-bee", "biker-bee", "diva-bee",
    "superbee", "queen-bee", "robo-bee", "ware-bee", "zom-bee"
}

# Programmatic override applies pricing at module load
for a in AVATAR_CATALOG:
    if not a.get("is_default_free", False):
        a["price"] = DEFAULT_LOCKED_PRICE  # $0.99 default
    if a.get("id") in PREMIUM_199_IDS:
        a["price"] = 1.99  # Premium tier override
```

**No code changes needed** - pricing already matches App Store Connect structure!

---

## 🚀 Next Steps

1. **Create all 20 IAP products** in App Store Connect (see tables above)
2. **Upload new opaque screenshots** (640×920px from iOS Simulator)
3. **Delete old transparent screenshots** from app version page
4. **Add privacy policy URL**: https://beesmartspelling.app/privacy.html
5. **Complete age rating questionnaire** (likely 4+ or 9+)
6. **Uncheck Game Center** (unless you want to add it)
7. **Click "Submit for Review"**

Estimated total time: 2-3 hours for complete IAP setup + submission.
