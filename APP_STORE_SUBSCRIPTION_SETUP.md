# BeeSmart Spelling Bee - App Store Subscription Setup Guide
**Date**: November 15, 2025

## Overview
Complete guide for setting up Auto-Renewable Subscriptions in App Store Connect for BeeSmart Spelling Bee App.

---

## Step 1: Create Subscription Group

### Subscription Group Details
- **Reference Name**: BeeSmart Premium Membership
- **App Name (Customer-Facing)**: Premium Membership

**Why**: All auto-renewable subscriptions must belong to a group. Users can only subscribe to one subscription within a group at a time.

---

## Step 2: Auto-Renewable Subscriptions

### Subscription 1: Monthly Premium
**Product ID**: `beesmart.premium.monthly`

**Reference Name**: BeeSmart Premium Monthly

**Subscription Duration**: 1 Month

**Subscription Prices**:
- **USD**: $4.99/month
- (Apple will auto-populate other currencies)

**Display Name**: Premium Monthly Membership

**Description**:
```
Unlock unlimited spelling practice with Premium Monthly Membership!

✨ WHAT YOU GET:
• Unlimited word lists and quizzes
• All 39 premium bee avatars unlocked
• Ad-free experience
• Speed Round mode access
• Offline mode for practice anywhere
• Priority customer support
• Monthly content updates

🎯 PERFECT FOR:
Kids who want full access to all spelling features and avatars without limits!

Cancel anytime from your iPhone settings. Subscription automatically renews unless auto-renew is turned off at least 24 hours before the end of the current period.
```

**Subscription Benefits**:
- Full avatar library access (39 avatars)
- Unlimited quiz attempts
- Ad-free experience
- Offline practice mode
- Speed Round challenges
- Premium customer support

**Promotional Image**: Use app icon or premium badge graphic (1024x1024px)

---

### Subscription 2: Yearly Premium (RECOMMENDED - Best Value)
**Product ID**: `beesmart.premium.yearly`

**Reference Name**: BeeSmart Premium Yearly

**Subscription Duration**: 1 Year

**Subscription Prices**:
- **USD**: $39.99/year (Save 33% - equivalent to $3.33/month)

**Display Name**: Premium Yearly Membership

**Description**:
```
Best Value! Unlock unlimited spelling practice for a full year!

✨ WHAT YOU GET:
• Everything in Monthly Premium
• Save 33% compared to monthly billing
• All 39 premium bee avatars unlocked forever
• Ad-free experience for the entire year
• Speed Round mode access
• Offline mode for practice anywhere
• Priority customer support
• All future content updates included

🎯 BEST VALUE:
Save $20/year compared to monthly subscription! Perfect for dedicated learners who want year-round spelling practice.

Cancel anytime from your iPhone settings. Subscription automatically renews unless auto-renew is turned off at least 24 hours before the end of the current period.
```

**Subscription Benefits**:
- All Monthly Premium features
- 33% cost savings
- Best value option
- Full year of uninterrupted learning

**Promotional Image**: Use "Best Value" badge graphic (1024x1024px)

---

### Subscription 3: Family Plan (Optional)
**Product ID**: `beesmart.premium.family.monthly`

**Reference Name**: BeeSmart Premium Family Monthly

**Subscription Duration**: 1 Month

**Family Sharing**: ✅ **ENABLED**

**Subscription Prices**:
- **USD**: $7.99/month (Up to 6 family members)

**Display Name**: Premium Family Membership

**Description**:
```
Perfect for families! Share Premium access with up to 6 family members!

✨ WHAT YOUR FAMILY GETS:
• Premium access for up to 6 family members
• Each member gets their own progress tracking
• All 39 premium bee avatars unlocked
• Ad-free experience for everyone
• Speed Round mode access
• Offline mode for practice anywhere
• Priority customer support
• Individual leaderboards and achievements

🎯 FAMILY FRIENDLY:
Best option for households with multiple children or siblings learning spelling together!

Shared through Apple Family Sharing. Cancel anytime from your iPhone settings. Subscription automatically renews unless auto-renew is turned off at least 24 hours before the end of the current period.
```

**Subscription Benefits**:
- Share with up to 6 family members
- Individual progress tracking
- Cost-effective for families
- All premium features for everyone

---

## Step 3: Subscription Group Settings

### Level Ranking (Upsell Priority)
1. **Yearly Premium** (Level 1 - Highest Value)
2. **Family Plan** (Level 2)
3. **Monthly Premium** (Level 3)

**Why this order**: Apple will suggest upgrades from lower to higher tiers. We want users to see Yearly as the upgrade path from Monthly.

---

## Step 4: Billing Grace Period

**Recommendation**: ✅ **Enable 16-day grace period**

**Settings**:
- Grace Period Duration: 16 days
- Retain Access During Grace Period: Yes

**Why**: Helps retain subscribers who have billing issues (expired cards, insufficient funds). You maintain revenue continuity, and users maintain access while Apple attempts to recover payment.

---

## Step 5: Streamlined Purchasing

**Setting**: ✅ **Keep TURNED ON**

**Why**: Allows users to subscribe from:
- App Store product page
- Marketing emails
- Website links
- Other promotional channels

**Exception**: Only turn OFF if you have:
- Contingent pricing (we don't)
- Win-back offers (not applicable for new submission)

---

## Step 6: Promotional Offers (After Initial Approval)

### Introductory Offer - Free Trial
**Type**: Free Trial
**Duration**: 7 days
**Product**: All subscriptions (Monthly, Yearly, Family)

**Customer-Facing Text**:
```
Start your 7-day free trial! Cancel anytime.
```

**Why**: Industry standard. Significantly increases conversion rates. Users can experience full premium features before committing.

### Introductory Offer - Discounted First Period
**Type**: Pay Up Front
**Duration**: First month
**Price**: $0.99 (for Monthly Premium)

**Customer-Facing Text**:
```
Get your first month for just $0.99! Then $4.99/month.
```

**Why**: Alternative to free trial. Gets users invested with small initial payment, then converts to full price.

---

## Step 7: Subscription Terms & Policies

### Privacy Policy URL
`https://beesmartspelling.com/privacy` (or your actual URL)

### Terms of Service URL
`https://beesmartspelling.com/terms` (or your actual URL)

### Subscription Terms (Required Text for App Description)
Add to your App Store description:

```
SUBSCRIPTION INFORMATION:

• Premium Monthly: $4.99/month
• Premium Yearly: $39.99/year (Save 33%)
• Premium Family: $7.99/month (Up to 6 family members)

• Payment will be charged to iTunes Account at confirmation of purchase
• Subscription automatically renews unless auto-renew is turned off at least 24 hours before the end of the current period
• Account will be charged for renewal within 24 hours prior to the end of the current period
• Subscriptions may be managed by the user and auto-renewal may be turned off by going to the user's Account Settings after purchase
• Any unused portion of a free trial period, if offered, will be forfeited when the user purchases a subscription to that publication

Privacy Policy: [YOUR_URL]
Terms of Use: [YOUR_URL]
```

---

## Step 8: Implementation Checklist

### Before Submitting First Version:
- [ ] Create Subscription Group "BeeSmart Premium Membership"
- [ ] Add Monthly Premium subscription ($4.99)
- [ ] Add Yearly Premium subscription ($39.99)
- [ ] (Optional) Add Family Premium subscription ($7.99)
- [ ] Set subscription level rankings (Yearly > Family > Monthly)
- [ ] Enable 16-day billing grace period
- [ ] Keep Streamlined Purchasing ON
- [ ] Upload promotional images for each tier
- [ ] Add subscription terms to app description
- [ ] Ensure Privacy Policy and Terms of Service URLs are live
- [ ] Select subscriptions in app version's "In-App Purchases and Subscriptions" section
- [ ] Submit app binary with first subscription

### After Initial Approval:
- [ ] Add 7-day free trial introductory offer
- [ ] (Optional) Add $0.99 first month offer
- [ ] Monitor subscription analytics
- [ ] Set up promotional offers for win-back campaigns

---

## Step 9: In-App Implementation Reference

Your app already has subscription handling in `AjaSpellBApp.py`. Verify these product IDs match:

```python
SUBSCRIPTION_PRODUCTS = {
    'beesmart.premium.monthly': {
        'name': 'Premium Monthly Membership',
        'duration': '1 month',
        'price': 4.99
    },
    'beesmart.premium.yearly': {
        'name': 'Premium Yearly Membership', 
        'duration': '1 year',
        'price': 39.99
    },
    'beesmart.premium.family.monthly': {
        'name': 'Premium Family Membership',
        'duration': '1 month',
        'price': 7.99,
        'family_sharing': True
    }
}
```

---

## Step 10: App Store Connect Navigation

### To Create Subscriptions:
1. Log in to App Store Connect
2. Go to "My Apps" → Select "BeeSmart Spelling Bee"
3. Click "Features" tab
4. Click "In-App Purchases" in left sidebar
5. Click "Subscriptions" 
6. Click "Create" under Subscription Groups
7. Create group "BeeSmart Premium Membership"
8. Click "+" to add subscriptions
9. Fill in details from this guide
10. Save each subscription

### To Link to App Version:
1. Go to "App Store" tab
2. Click on your version (e.g., "1.0 Prepare for Submission")
3. Scroll to "In-App Purchases and Subscriptions" section
4. Click "Add" next to Subscriptions
5. Select all your subscriptions
6. Save

### Important: 
⚠️ **First subscription MUST be submitted with your app binary**. You cannot add subscriptions without an uploaded build.

---

## Recommended Pricing Strategy

### Why These Prices:

**Monthly $4.99**:
- Industry standard for educational apps
- Lower than competitors ($5.99-$7.99)
- Affordable for parents
- Monthly commitment flexibility

**Yearly $39.99**:
- 33% discount (equivalent to $3.33/month)
- Strong incentive to commit long-term
- Better lifetime value
- Common pricing in education category

**Family $7.99**:
- Only $3 more than individual
- Huge value for families with 2+ kids
- Encourages family sharing adoption
- Increases customer lifetime value

---

## Marketing Copy for App Store

### In App Purchases Section Preview Text:
```
Premium Membership - $4.99/month
Unlock all 39 avatars, unlimited quizzes, and ad-free spelling practice!

Premium Yearly - $39.99/year
Best Value! Save 33% with annual billing. Full year of unlimited learning!

Premium Family - $7.99/month
Share premium access with up to 6 family members!
```

---

## Success Metrics to Track

After launch, monitor in App Store Connect:
- Subscription conversion rate (target: 2-5%)
- Free trial to paid conversion (target: 30-40%)
- Monthly to yearly upgrade rate
- Churn rate (target: <10% monthly)
- Family plan adoption rate

---

## Common Mistakes to Avoid

❌ **DON'T**:
- Submit app without selecting subscriptions in version
- Forget to upload binary before creating subscriptions
- Use vague subscription descriptions
- Skip promotional images
- Forget to add subscription terms to app description
- Turn off Streamlined Purchasing unnecessarily

✅ **DO**:
- Create clear, benefit-focused descriptions
- Set up billing grace period (helps retention)
- Order subscription levels strategically
- Add free trial after initial approval
- Monitor and optimize pricing based on data
- Test subscription flow thoroughly before submission

---

## Next Steps

1. **Create Privacy Policy & Terms** (if not done)
2. **Upload App Binary** to App Store Connect
3. **Create Subscription Group** following this guide
4. **Add All 3 Subscriptions** (Monthly, Yearly, Family)
5. **Link Subscriptions to App Version**
6. **Submit for Review** with binary and subscriptions together
7. **Add Free Trial Offer** after approval
8. **Monitor Performance** and optimize

---

## Support Resources

- [Apple Subscription Documentation](https://developer.apple.com/app-store/subscriptions/)
- [Pricing Best Practices](https://developer.apple.com/app-store/subscriptions/pricing/)
- [Subscription Group Setup](https://help.apple.com/app-store-connect/#/dev4f019af23)
- [Testing Subscriptions](https://developer.apple.com/documentation/storekit/in-app_purchase/testing_in-app_purchases_with_sandbox)

---

**Document Version**: 1.0  
**Last Updated**: November 15, 2025  
**Status**: Ready for App Store Connect Setup
