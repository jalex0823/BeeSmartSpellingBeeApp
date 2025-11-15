# App Store Subscription Integration - Quick Reference

**Date**: November 15, 2025  
**Status**: ✅ Backend Complete - Ready for iOS Integration

---

## 🎯 Overview

Your BeeSmart app now has **complete App Store subscription backend** with automatic receipt validation, webhook handling, and database sync.

---

## 📱 How It Works

```
[User buys subscription in iOS app]
         ↓
[iOS sends receipt to /api/validate-receipt]
         ↓
[Backend validates with Apple servers]
         ↓
[Database updated with subscription status]
         ↓
[Premium features unlocked]
         ↓
[Apple sends renewals/cancellations to /apple-webhook]
         ↓
[Backend auto-updates subscription]
```

---

## 🔑 Product IDs (Match in iOS & App Store Connect)

```python
# Monthly Subscription
'beesmart.premium.monthly' → $4.99/month

# Yearly Subscription (Best Value)
'beesmart.premium.yearly' → $39.99/year (Save 33%)

# Family Plan
'beesmart.premium.family.monthly' → $7.99/month (Up to 6 members)
```

---

## 🚀 Backend Endpoints

### 1. Validate Receipt
**URL**: `POST /api/validate-receipt`

**iOS sends**:
```json
{
  "receipt_data": "base64_encoded_receipt",
  "user_id": 123
}
```

**Backend responds**:
```json
{
  "status": "success",
  "message": "Subscription validated and updated",
  "subscription": {
    "is_premium": true,
    "subscription_type": "yearly",
    "status": "active",
    "expires_at": "2026-11-15T10:00:00",
    "days_remaining": 365
  }
}
```

### 2. Apple Webhook
**URL**: `POST /apple-webhook`

**Apple sends** (auto-renewal):
```json
{
  "notification_type": "DID_RENEW",
  "unified_receipt": {
    "latest_receipt_info": [...]
  }
}
```

**Backend auto-updates** database silently.

### 3. Subscription Info
**URL**: `GET /api/subscriptions`

Returns all 3 subscription tiers with pricing, benefits, descriptions.

### 4. Subscription Page
**URL**: `GET /subscription` or `/premium`

Visual landing page with 3-tier comparison cards.

---

## 🗄️ Database Fields (User Model)

```python
# Subscription tracking
subscription_type              # 'monthly', 'yearly', 'family'
subscription_product_id        # 'beesmart.premium.monthly'
subscription_status            # 'active', 'grace_period', 'expired', 'canceled'
subscription_expires_at        # When current period ends
subscription_auto_renew        # True if will renew
original_transaction_id        # Apple's unique ID (never changes)
latest_receipt_data            # Latest receipt (base64)
subscription_started_at        # First purchase date
subscription_canceled_at       # When user canceled (still has access until expires_at)
family_shared_from            # If using family sharing
```

---

## 🔍 Check Premium Status

### In Python (Backend):
```python
from models import User

user = User.query.get(user_id)

# Simple check
if user.is_premium_active():
    # Unlock premium features
    pass

# Detailed status
status = user.get_subscription_status()
print(status)
# {
#   'is_premium': True,
#   'subscription_type': 'yearly',
#   'status': 'active',
#   'expires_at': '2026-11-15T10:00:00',
#   'days_remaining': 365,
#   'auto_renew': True,
#   'family_shared': False
# }
```

### In Templates (Jinja2):
```jinja2
{% if current_user.is_premium_active() %}
  <p>Welcome Premium Member! 🌟</p>
  <!-- Show all 39 avatars -->
{% else %}
  <a href="/subscription">Upgrade to Premium</a>
{% endif %}
```

---

## ⚙️ Environment Variables Required

### Railway Production:
```bash
# Get from App Store Connect → App Information
APPLE_SHARED_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# Already set (existing)
DATABASE_URL=postgresql://...
SECRET_KEY=...
```

---

## 📋 Setup Checklist

### Backend (Complete ✅):
- [x] User model with subscription fields
- [x] Receipt validation endpoint
- [x] Apple webhook handler
- [x] Subscription page UI
- [x] Database migration script
- [x] Setup guide documentation

### Database (Run Once):
```bash
# SSH into Railway or run with production DATABASE_URL
python scripts/migrate_subscription_fields.py

# Expected output:
# ✅ Columns added: 10
# ✅ Added index: idx_users_subscription_type
# ✨ Migration completed successfully!
```

### App Store Connect:
- [ ] Create Subscription Group "BeeSmart Premium Membership"
- [ ] Add Monthly ($4.99), Yearly ($39.99), Family ($7.99) subscriptions
- [ ] Set level rankings (Yearly > Family > Monthly)
- [ ] Enable 16-day billing grace period
- [ ] Generate App-Specific Shared Secret
- [ ] Configure webhook URL:
  ```
  https://your-railway-domain.up.railway.app/apple-webhook
  ```

### iOS App:
- [ ] Implement StoreKit purchase flow
- [ ] Send receipt to `/api/validate-receipt` after purchase
- [ ] Handle subscription status responses
- [ ] Implement restore purchases
- [ ] Test in sandbox environment

---

## 🧪 Testing

### Sandbox Environment:
1. Create sandbox tester in App Store Connect
2. Sign out of real App Store on device
3. Launch app → attempt purchase
4. Sign in with sandbox account
5. **Subscriptions renew every 5 minutes** (not monthly!)

### Verify Backend:
```bash
# Check Railway logs for webhook events
railway logs -f

# Look for:
# 📱 Apple webhook: DID_RENEW for user 123
# ✅ Subscription renewed for user 123
```

### Test Receipt Validation:
```bash
curl -X POST https://your-domain.up.railway.app/api/validate-receipt \
  -H "Content-Type: application/json" \
  -d '{
    "receipt_data": "base64_receipt",
    "user_id": 123
  }'
```

---

## 🎓 Webhook Event Types

| Event | When | Backend Action |
|-------|------|----------------|
| `INITIAL_BUY` | First subscription | Set status='active' |
| `DID_RENEW` | Auto-renewal success | Extend expires_at |
| `DID_FAIL_TO_RENEW` | Billing failed | Set status='grace_period' (16 days) |
| `DID_CHANGE_RENEWAL_STATUS` | User canceled | Set canceled_at, keep access until expires |
| `DID_RECOVER` | Billing recovered | Set status='active' |
| `REFUND` | User refunded | Revoke access immediately |
| `CANCEL` | Apple support canceled | Revoke access |

---

## 🚨 Troubleshooting

### "Receipt validation failed (21004)":
- **Cause**: APPLE_SHARED_SECRET mismatch
- **Fix**: Get correct secret from App Store Connect → App Information

### "No user found for transaction":
- **Cause**: First-time purchase, user doesn't exist yet
- **Fix**: iOS app should create user BEFORE sending receipt

### "Subscription status still 'none'":
- **Cause**: Receipt not validated yet
- **Fix**: iOS app must call `/api/validate-receipt` after purchase

### "Webhook not receiving events":
- **Cause**: Incorrect webhook URL in App Store Connect
- **Fix**: Verify URL is `https://your-domain.up.railway.app/apple-webhook`

---

## 📚 Documentation

- **Setup Guide**: `APP_STORE_SUBSCRIPTION_SETUP.md`
- **Migration Script**: `scripts/migrate_subscription_fields.py`
- **User Model**: `models.py` (lines 48-75 + subscription methods)
- **API Routes**: `AjaSpellBApp.py` (lines 9814-10070)
- **Subscription Page**: `templates/subscription.html`

---

## 🎉 Success Criteria

**Backend is ready when**:
- ✅ Database migration successful
- ✅ APPLE_SHARED_SECRET set in Railway
- ✅ Webhook URL configured in App Store Connect
- ✅ `/api/validate-receipt` returns 200 status
- ✅ Railway logs show webhook events

**iOS integration complete when**:
- [ ] Sandbox purchase succeeds
- [ ] Backend validates receipt → status='active'
- [ ] Premium features unlock immediately
- [ ] Restore purchases works
- [ ] Webhooks auto-renew subscription

---

## 💡 Next Steps

1. **Run migration**: `python scripts/migrate_subscription_fields.py`
2. **Set env variable**: Add APPLE_SHARED_SECRET to Railway
3. **Configure webhook**: Add URL to App Store Connect
4. **Test sandbox**: Purchase with test account
5. **Monitor logs**: `railway logs -f` to see webhook events
6. **Deploy iOS**: Submit with StoreKit integration

---

**Status**: ✅ Backend infrastructure complete and deployed  
**Blocking**: iOS StoreKit implementation + App Store Connect setup  
**ETA to Production**: 3-5 days after iOS integration complete
