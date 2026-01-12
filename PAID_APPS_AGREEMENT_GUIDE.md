# Paid Apps Agreement - Signing Guide

## Issue
Apple Developer account has 2 agreements. The Paid Apps Agreement needs to be signed to enable in-app purchases.

## Why This is Required

- **In-App Purchases**: Cannot function without an active Paid Apps Agreement
- **App Store Review**: IAP products will not work in sandbox testing without this agreement
- **Revenue**: Required to receive payments from App Store sales

## Solution: Sign Paid Apps Agreement

### Step-by-Step Instructions

1. **Log in to App Store Connect**
   - Go to: https://appstoreconnect.apple.com
   - Sign in with your Apple Developer account

2. **Navigate to Agreements**
   - Click on your account/profile icon (top right)
   - Select **"Agreements, Tax, and Banking"** from the dropdown
   - OR go directly to: https://appstoreconnect.apple.com/agreements

3. **View Agreement Status**
   - You'll see a list of agreements:
     - **Paid Applications Agreement** (this is what you need)
     - **Free Applications Agreement** (you may already have this)

4. **Check Agreement Status**
   - Look for **"Paid Applications Agreement"**
   - Status will show one of:
     - ✅ **"Active"** - Already signed (no action needed)
     - ⚠️ **"Pending"** - Needs to be completed
     - ❌ **"Expired"** - Needs to be renewed
     - ⚠️ **"Action Required"** - Needs attention

5. **Complete the Agreement**
   - If status is "Pending" or "Action Required":
     - Click on **"Paid Applications Agreement"**
     - Review the agreement terms
     - Click **"Agree"** or **"Accept"**

6. **Complete Tax and Banking Information**
   - After accepting the agreement, you'll need to:
     - **Tax Information**: Complete W-9 (US) or tax forms for your country
     - **Banking Information**: Add your bank account for payments
     - **Contact Information**: Verify your contact details

7. **Wait for Activation**
   - After completing all steps, the agreement status will change to **"Processing"**
   - This can take 24-48 hours to become **"Active"**
   - You'll receive an email when it's active

### Visual Guide

```
App Store Connect → Account → Agreements, Tax, and Banking
↓
Find "Paid Applications Agreement"
↓
Check Status:
  - If "Active" → ✅ Done!
  - If "Pending" → Click to complete
↓
Accept Agreement → Complete Tax & Banking
↓
Wait for "Active" status (24-48 hours)
```

### Required Information

Before starting, gather:
- **Tax ID** (SSN for individuals, EIN for businesses)
- **Bank Account Details**:
  - Account number
  - Routing number (US) or SWIFT code (international)
  - Bank name and address
- **Business Information** (if applicable):
  - Legal business name
  - Business address
  - Business type

### Common Issues

**Issue**: "Agreement not available"
- **Fix**: Ensure your Apple Developer account is fully set up
- **Fix**: Complete any pending account verification steps

**Issue**: "Tax information incomplete"
- **Fix**: Complete all required tax forms
- **Fix**: For US developers, complete W-9 form
- **Fix**: For international developers, complete appropriate tax forms for your country

**Issue**: "Banking information invalid"
- **Fix**: Verify account number and routing number are correct
- **Fix**: Ensure bank account is in your name (or business name)
- **Fix**: Some banks require additional verification

**Issue**: "Agreement stuck in Processing"
- **Fix**: Wait 24-48 hours (normal processing time)
- **Fix**: Check email for any requests for additional information
- **Fix**: Contact Apple Developer Support if stuck longer than 48 hours

### Verification

After completing the agreement:

1. **Check Status**
   - Go back to Agreements page
   - Verify "Paid Applications Agreement" shows **"Active"**

2. **Test IAP in Sandbox**
   - Create a sandbox test account
   - Test in-app purchase flow
   - Purchases should now work in sandbox environment

3. **Check IAP Products**
   - Go to: App Store Connect → Your App → Features → In-App Purchases
   - Products should be available for testing
   - Status should show "Ready to Submit" or "Cleared for Sale"

### Timeline

- **Agreement Acceptance**: Immediate
- **Tax Information**: 1-2 business days (if already prepared)
- **Banking Information**: 1-2 business days (if already prepared)
- **Agreement Activation**: 24-48 hours after all information is complete

### Support

If you need help:
- **Apple Developer Support**: https://developer.apple.com/contact/
- **App Store Connect Help**: https://help.apple.com/app-store-connect/
- **Agreement Questions**: Contact Apple Developer Support directly

---

## Current Status Checklist

- [ ] Logged into App Store Connect
- [ ] Navigated to Agreements, Tax, and Banking
- [ ] Checked Paid Applications Agreement status
- [ ] Accepted/Completed Paid Applications Agreement
- [ ] Completed Tax Information
- [ ] Completed Banking Information
- [ ] Verified Agreement is "Active"
- [ ] Tested IAP in sandbox environment

---

## Important Notes

- **Account Holder**: Only the Account Holder can sign agreements
- **Team Admin**: Team Admins cannot sign agreements (only Account Holder)
- **Multiple Agreements**: You can have both Free and Paid agreements active
- **No Cost**: Signing the agreement is free (no fees to activate)
- **Revenue Share**: Apple takes 30% (15% after first year for subscriptions) - this is standard

---

## Next Steps After Agreement is Active

1. ✅ Verify IAP products are "Ready to Submit"
2. ✅ Test purchases in sandbox environment
3. ✅ Submit app for review
4. ✅ IAP will work in production after app approval
