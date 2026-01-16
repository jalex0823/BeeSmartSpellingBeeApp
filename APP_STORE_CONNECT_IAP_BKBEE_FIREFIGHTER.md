# App Store Connect IAP Configuration - BK Bee & Firefighter Bee

**Date:** January 16, 2025  
**Purpose:** IAP product information for App Store Connect setup

---

## 🔥 Firefighter Bee Avatar

### Basic Information
- **Display Name:** Firefighter Bee Avatar
- **Avatar ID:** `firefighter-bee`
- **Product ID:** `beesmart.avatar.firefighter_bee` ✅ **CONFIRMED** (from avatar_catalog.py)
- **Category:** Profession

### Pricing & Unlock
- **IAP Price:** $1.99 USD (Tier 2)
- **Honey Points Unlock:** 30,000 points
- **Tier:** Premium
- **Purchase Type:** Non-Consumable (recommended for avatars)

### Description
"Brave, helpful, and ready to save the day - Firefighter Bee keeps your spelling skills blazing!"

### App Store Connect Setup
1. **Product Type:** Non-Consumable (recommended - one purchase unlocks forever)
2. **Reference Name:** `Firefighter Bee Avatar`
3. **Product ID:** `beesmart.avatar.firefighter_bee` ✅ **MUST MATCH EXACTLY** (no .v2 suffix)
4. **Price:** **Tier 2** ($1.99 USD)
5. **Display Name:** `Firefighter Bee Avatar`
6. **Description:** 
   ```
   Brave, helpful, and ready to save the day - Firefighter Bee keeps your spelling skills blazing! 
   Unlock this premium avatar with 30,000 Honey Points or purchase for $1.99.
   ```

---

## 🎯 BK Bee Avatar

### Basic Information
- **Display Name:** BK Bee Avatar
- **Avatar ID:** `bk-bee`
- **Product ID:** `beesmart.avatar.bk_bee` ✅ **CONFIRMED** (from avatar_catalog.py)
- **Category:** Classic

### Pricing & Unlock
- **IAP Price:** $1.99 USD (Tier 2)
- **Honey Points Unlock:** 30,000 points
- **Tier:** Premium
- **Purchase Type:** Non-Consumable (recommended for avatars)

### Description
"Big style, big confidence - BK Bee brings swagger to your spelling streaks!"

### App Store Connect Setup
1. **Product Type:** Non-Consumable (recommended - one purchase unlocks forever)
2. **Reference Name:** `BK Bee Avatar`
3. **Product ID:** `beesmart.avatar.bk_bee` ✅ **MUST MATCH EXACTLY** (no .v2 suffix)
4. **Price:** **Tier 2** ($1.99 USD)
5. **Display Name:** `BK Bee Avatar`
6. **Description:**
   ```
   Big style, big confidence - BK Bee brings swagger to your spelling streaks! 
   Unlock this premium avatar with 30,000 Honey Points or purchase for $1.99.
   ```

---

## 📋 App Store Connect Configuration Steps

### For Each Avatar:

1. **Go to App Store Connect**
   - Navigate to: Your App → Features → In-App Purchases
   - Click "+" to create new IAP

2. **Select Product Type**
   - Choose: **Non-Consumable** (recommended for avatars)
   - OR: **Consumable** (if you want users to be able to purchase multiple times)

3. **Fill in Product Information**

   **Firefighter Bee:**
   - **Reference Name:** `Firefighter Bee Avatar`
   - **Product ID:** `beesmart.avatar.firefighter_bee` ✅ **MUST MATCH EXACTLY** (confirmed from catalog)
   - **Price:** Select **Tier 2** ($1.99 USD)
   - **Display Name:** `Firefighter Bee Avatar`
   - **Description:** 
     ```
     Brave, helpful, and ready to save the day - Firefighter Bee keeps your spelling skills blazing! 
     Unlock this premium avatar with 30,000 Honey Points or purchase for $1.99.
     ```

   **BK Bee:**
   - **Reference Name:** `BK Bee Avatar`
   - **Product ID:** `beesmart.avatar.bk_bee` ✅ **MUST MATCH EXACTLY** (confirmed from catalog)
   - **Price:** Select **Tier 2** ($1.99 USD)
   - **Display Name:** `BK Bee Avatar`
   - **Description:**
     ```
     Big style, big confidence - BK Bee brings swagger to your spelling streaks! 
     Unlock this premium avatar with 30,000 Honey Points or purchase for $1.99.
     ```

4. **Review Information**
   - Review Name: Same as Display Name
   - Review Screenshot: Optional (can add later)

5. **Save and Submit**
   - Click "Save"
   - Status will be "Ready to Submit" (if all required fields filled)
   - Submit with your next app version

---

## ⚠️ Critical Requirements

### Product ID Format
- **MUST match exactly:** `beesmart.avatar.firefighter_bee` and `beesmart.avatar.bk_bee`
- **Case-sensitive:** Lowercase only
- **No spaces:** Use underscores instead of hyphens in product ID
- **Format:** `beesmart.avatar.{avatar_id_with_underscores}`

### Pricing Tiers
- **Tier 1:** $0.99 USD
- **Tier 2:** $1.99 USD
- Firefighter Bee: **Tier 2** ($1.99)
- BK Bee: **Tier 2** ($1.99)

### Honey Points Alternative
Both avatars can be unlocked via:
- **Purchase:** IAP (one-time)
- **OR Earn:** Honey Points (30,000 for both avatars)

Users can choose either method - this is Apple Guideline 5.1.1 compliant.

---

## 🔍 Verification Checklist

Before submitting to App Store:

- [ ] Product IDs match exactly: `beesmart.avatar.firefighter_bee` and `beesmart.avatar.bk_bee`
- [ ] Prices set correctly (Tier 2 for Firefighter Bee)
- [ ] Display names are clear and descriptive
- [ ] Descriptions mention both purchase and Honey Points unlock options
- [ ] Product status is "Ready to Submit"
- [ ] Test in sandbox environment
- [ ] Verify purchases unlock avatars correctly

---

## 📱 Testing in Sandbox

After creating IAP products:

1. **Create Sandbox Test Account**
   - App Store Connect → Users and Access → Sandbox Testers
   - Create new tester with unique email

2. **Test Purchase Flow**
   - Launch app in TestFlight or development build
   - Sign out of production App Store
   - Navigate to Avatars → Find Firefighter Bee or BK Bee
   - Tap locked avatar → Purchase
   - Sign in with sandbox account
   - Complete purchase
   - Verify avatar unlocks

3. **Test Honey Points Unlock**
   - Earn 30,000 Honey Points (or required amount)
   - Navigate to Avatars → Find avatar
   - Verify "Unlock with Points" option appears
   - Unlock with points
   - Verify avatar unlocks

---

## 📊 Summary Table

| Avatar | Product ID | Price | Honey Points | Tier |
|--------|-----------|-------|--------------|------|
| **Firefighter Bee** | `beesmart.avatar.firefighter_bee` | $1.99 | 30,000 | Premium |
| **BK Bee** | `beesmart.avatar.bk_bee` | $1.99 | 30,000 | Premium |

---

**Next Steps:**
1. ✅ All information confirmed from `avatar_catalog.py`
2. Create IAP products in App Store Connect using the information above
3. Test in sandbox environment
4. Submit with next app version (Build 46)

---

## 📝 Quick Reference Card

**Copy this for App Store Connect:**

### Firefighter Bee
- **Product ID:** `beesmart.avatar.firefighter_bee`
- **Price:** Tier 2 ($1.99)
- **Honey Points:** 30,000
- **Description:** Brave, helpful, and ready to save the day - Firefighter Bee keeps your spelling skills blazing! Unlock this premium avatar with 30,000 Honey Points or purchase for $1.99.

### BK Bee
- **Product ID:** `beesmart.avatar.bk_bee`
- **Price:** Tier 2 ($1.99)
- **Honey Points:** 30,000
- **Description:** Big style, big confidence - BK Bee brings swagger to your spelling streaks! Unlock this premium avatar with 30,000 Honey Points or purchase for $1.99.
