# BeeSmart Premium — Subscription Metadata (Ready to Paste)
**Date**: 2025-12-26  
Use this to clear **Status: Developer Action Needed** for your first auto‑renewable subscription submission.

> Notes
> - **Apple ID** is assigned by App Store Connect after you create/save the subscription. You do not choose it.
> - The **Product ID** must match what the app expects (see below). Product IDs cannot be changed later.
> - Your **first subscription** must be submitted with a **new app version** (App Store Connect requirement).

---

## 1) Subscription Group
- **Reference Name (internal)**: BeeSmart Premium Membership
- **Customer-Facing Group Name**: Premium Membership

Recommended settings:
- **Subscription level order**: Yearly (highest) → Monthly
- **Billing Grace Period**: Enable (16 days)
- **Streamlined Purchasing**: ON

---

## 2) Subscription Product IDs (must match app)
These are the SKUs used by the backend and docs:
- Monthly: `beesmart.premium.monthly`
- Yearly: `beesmart.premium.yearly`
- (Optional) Family: `beesmart.premium.family.monthly`

---

## 3) Monthly Subscription (copy/paste)
- **Reference Name (internal)**: BeeSmart Premium Monthly
- **Product ID**: `beesmart.premium.monthly`
- **Duration**: 1 Month
- **Price (USD)**: $4.99

### App Store Localization (English - US)
- **Display Name**: Premium Monthly Membership
- **Description**:
```
Unlock unlimited spelling practice with Premium Monthly Membership!

WHAT YOU GET:
• Unlimited word lists and quizzes
• All premium bee avatars unlocked
• Ad-free experience
• Speed Round mode access
• Offline mode for practice anywhere
• Priority customer support

Cancel anytime in your Apple ID settings. Subscription automatically renews unless auto-renew is turned off at least 24 hours before the end of the current period.
```

### Review Information (common missing requirement)
- **Review Screenshot**: Upload an **opaque** PNG/JPG (no alpha). Use an in‑app screenshot showing the premium paywall/subscription screen.
- **Review Notes**:
```
Test subscription purchase in Sandbox.
In the app, open the Premium/Subscription screen and tap Subscribe.
Restore Purchases is available from the same Premium screen.
No login is required to view the subscription screen.
```

---

## 4) Yearly Subscription (copy/paste)
- **Reference Name (internal)**: BeeSmart Premium Yearly
- **Product ID**: `beesmart.premium.yearly`
- **Duration**: 1 Year
- **Price (USD)**: $39.99

### App Store Localization (English - US)
- **Display Name**: Premium Yearly Membership
- **Description**:
```
Best value! Unlock unlimited spelling practice for a full year.

WHAT YOU GET:
• Everything in Premium Monthly
• Save vs monthly billing
• All premium bee avatars unlocked
• Ad-free experience
• Speed Round mode access
• Offline mode for practice anywhere
• Priority customer support

Cancel anytime in your Apple ID settings. Subscription automatically renews unless auto-renew is turned off at least 24 hours before the end of the current period.
```

### Review Information
- **Review Screenshot**: Upload opaque PNG/JPG
- **Review Notes**: Same as Monthly

---

## 5) Required URLs (App Info + Subscription group)
These pages already exist in-app as public routes:
- **Privacy Policy URL**: `https://YOUR_DOMAIN/privacy`
- **Terms of Use URL**: `https://YOUR_DOMAIN/terms`

If you’re using the hosted static pages instead, use your actual public URLs.

---

## 6) First Submission Requirement (critical)
On the **new app version page** in App Store Connect:
- Go to **In-App Purchases and Subscriptions**
- Click **+** and select your subscription(s) from the list
- Save the version
- Submit the version to review

---

## 7) The usual causes of “Developer Action Needed”
Check these first:
- Missing **App Store Localization** (Display Name + Description)
- Missing **Review Screenshot** and/or **Review Notes**
- Not marked **Cleared for Sale**
- Subscription not attached to the **new app version** (first subscription only)
- Banking/tax agreements not completed (less common, but blocks selling)
