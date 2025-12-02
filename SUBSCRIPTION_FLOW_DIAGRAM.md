# App Store Subscription Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BeeSmart Subscription Flow                           │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   iOS App    │
│              │
│ User taps    │
│ "Subscribe"  │
└──────┬───────┘
       │
       │ 1. Trigger purchase with product ID
       │    'beesmart.premium.monthly'
       ▼
┌──────────────┐
│  StoreKit    │◄─────────────────────┐
│              │                      │
│ Shows Apple  │                      │
│ payment UI   │                      │
└──────┬───────┘                      │
       │                              │
       │ 2. User authorizes           │
       │    (Face ID / Touch ID)      │
       ▼                              │
┌──────────────────────┐              │
│  App Store Connect   │              │
│                      │              │
│ • Validates payment  │              │
│ • Charges iTunes     │              │
│ • Creates receipt    │              │
└──────┬───────────────┘              │
       │                              │
       │ 3. Receipt returned          │
       ▼                              │
┌──────────────┐                      │
│   iOS App    │                      │
│              │                      │
│ Receipt:     │                      │
│ {            │                      │
│   product_id │                      │
│   expires_ms │                      │
│   ...        │                      │
│ }            │                      │
└──────┬───────┘                      │
       │                              │
       │ 4. POST /api/validate-receipt│
       │    {receipt_data, user_id}   │
       ▼                              │
┌──────────────────────┐              │
│   Flask Backend      │              │
│   (Railway)          │              │
│                      │              │
│ /api/validate-receipt│              │
└──────┬───────────────┘              │
       │                              │
       │ 5. Forward receipt to Apple  │
       │    for verification          │
       ▼                              │
┌──────────────────────┐              │
│  Apple Verification  │              │
│  Servers             │              │
│                      │              │
│ buy.itunes.apple.com │              │
└──────┬───────────────┘              │
       │                              │
       │ 6. Verified receipt data     │
       │    {status: 0, receipt_info} │
       ▼                              │
┌──────────────────────┐              │
│   Flask Backend      │              │
│                      │              │
│ • Parse receipt      │              │
│ • Extract expiration │              │
│ • Update database:   │              │
│   - subscription_type│              │
│   - expires_at       │              │
│   - status='active'  │              │
└──────┬───────────────┘              │
       │                              │
       │ 7. Return success            │
       │    {subscription: {...}}     │
       ▼                              │
┌──────────────┐                      │
│   iOS App    │                      │
│              │                      │
│ • Unlock all │                      │
│   39 avatars │                      │
│ • Remove ads │                      │
│ • Speed Round│                      │
└──────────────┘                      │
                                      │
═══════════════════════════════════════╪═══════════════════════
    AUTOMATIC RENEWALS (Every Month/Year)                      
═══════════════════════════════════════╪═══════════════════════
                                      │
┌──────────────────────┐              │
│  App Store Connect   │              │
│                      │              │
│ (1 month later...)   │              │
│                      │              │
│ • Auto-charges user  │              │
│ • Creates new receipt│              │
└──────┬───────────────┘              │
       │                              │
       │ 8. Server-to-Server          │
       │    Notification              │
       │    POST /apple-webhook       │
       │    {notification_type:       │
       │     'DID_RENEW', ...}        │
       ▼                              │
┌──────────────────────┐              │
│   Flask Backend      │              │
│                      │              │
│ /apple-webhook       │              │
│                      │              │
│ • Detect DID_RENEW   │              │
│ • Extend expires_at  │              │
│ • Keep status=active │              │
│ • Update DB silently │              │
└──────────────────────┘              │
                                      │
       User keeps premium access!     │
                                      │
═══════════════════════════════════════╪═══════════════════════
    USER CANCELS SUBSCRIPTION         │
═══════════════════════════════════════╪═══════════════════════
                                      │
┌──────────────┐                      │
│ iPhone User  │                      │
│              │                      │
│ Settings →   │                      │
│ Apple ID →   │                      │
│ Subscriptions│                      │
│ → Cancel     │                      │
└──────┬───────┘                      │
       │                              │
       ▼                              │
┌──────────────────────┐              │
│  App Store Connect   │              │
│                      │              │
│ • Marks subscription │              │
│   for cancellation   │              │
│ • Still valid until  │              │
│   period ends        │              │
└──────┬───────────────┘              │
       │                              │
       │ 9. POST /apple-webhook       │
       │    {notification_type:       │
       │     'DID_CHANGE_RENEWAL_     │
       │      STATUS',                │
       │     auto_renew: '0'}         │
       ▼                              │
┌──────────────────────┐              │
│   Flask Backend      │              │
│                      │              │
│ • Detect cancelation │              │
│ • Set auto_renew=False│             │
│ • Set canceled_at    │              │
│ • Keep status=active │              │
│   until expires_at   │              │
└──────────────────────┘              │
                                      │
       User has access until          │
       subscription_expires_at!       │
                                      │
       (Then reverts to free tier)    │
                                      │
═══════════════════════════════════════╪═══════════════════════
    BILLING FAILURE (Grace Period)    │
═══════════════════════════════════════╪═══════════════════════
                                      │
┌──────────────────────┐              │
│  App Store Connect   │              │
│                      │              │
│ • Tries to charge    │              │
│ • Card declined! 💳❌ │              │
│ • Enters grace period│              │
│   (16 days)          │              │
└──────┬───────────────┘              │
       │                              │
       │ 10. POST /apple-webhook      │
       │     {notification_type:      │
       │      'DID_FAIL_TO_RENEW'}    │
       ▼                              │
┌──────────────────────┐              │
│   Flask Backend      │              │
│                      │              │
│ • Set status=        │              │
│   'grace_period'     │              │
│ • KEEP premium access│              │
│ • User has 16 days   │              │
│   to fix payment     │              │
└──────────────────────┘              │
                                      │
       If payment fixed:              │
       → status='active'              │
                                      │
       If 16 days pass:               │
       → status='expired'             │
       → premium_member=False         │
                                      │
═══════════════════════════════════════╪═══════════════════════
    FAMILY SHARING                    │
═══════════════════════════════════════╪═══════════════════════
                                      │
┌──────────────────────┐              │
│  Primary Subscriber  │              │
│                      │              │
│ original_transaction │              │
│ _id: 1000000001      │              │
└──────────────────────┘              │
         │                            │
         ├─────────┬──────────┐       │
         │         │          │       │
         ▼         ▼          ▼       │
┌────────────┐ ┌─────────┐ ┌─────────┐
│ Family     │ │ Family  │ │ Family  │
│ Member 1   │ │ Member 2│ │ Member 3│
│            │ │         │ │         │
│ family_    │ │ family_ │ │ family_ │
│ shared_from│ │ shared_ │ │ shared_ │
│ =100000001 │ │ from=.. │ │ from=.. │
└────────────┘ └─────────┘ └─────────┘
                                      │
       All 6 members get premium!     │
       is_premium_active() = True     │
                                      │
```

## Key Database States

```sql
-- Active Subscription
subscription_type = 'monthly'
subscription_status = 'active'
subscription_expires_at = '2026-01-15 10:00:00'
subscription_auto_renew = TRUE
premium_member = TRUE

-- Canceled (still has access)
subscription_status = 'canceled'
subscription_expires_at = '2025-12-31 23:59:59'  -- Future date
subscription_auto_renew = FALSE
subscription_canceled_at = '2025-11-15 14:30:00'
premium_member = TRUE  -- Until expires_at!

-- Grace Period (billing issue)
subscription_status = 'grace_period'
subscription_expires_at = '2025-11-30 10:00:00'
subscription_auto_renew = TRUE
premium_member = TRUE  -- Still has access

-- Expired
subscription_status = 'expired'
subscription_expires_at = '2025-10-15 10:00:00'  -- Past date
subscription_auto_renew = FALSE
premium_member = FALSE
```

## Premium Access Logic

```python
def is_premium_active(user):
    # Admin bypass
    if user.role == 'admin' or user.admin_all_access:
        return True
    
    # Legacy flag
    if user.premium_member:
        return True
    
    # Check subscription
    if user.subscription_status in ['active', 'grace_period']:
        if user.subscription_expires_at:
            return datetime.utcnow() < user.subscription_expires_at
        return True
    
    return False
```

## Error Handling

```
┌──────────────────────┐
│ Receipt Validation   │
│ Errors               │
└──────┬───────────────┘
       │
       ├─► 21007: Sandbox receipt → Retry with sandbox URL
       ├─► 21004: Wrong shared secret → Fix APPLE_SHARED_SECRET
       ├─► 21003: Invalid receipt → User tried to fake receipt
       ├─► 21006: Expired subscription → Normal (not an error)
       ├─► Timeout: Apple servers down → Retry with exponential backoff
       └─► Other: Log error, return 500
```

## Environment Setup

```bash
# Required in Railway
APPLE_SHARED_SECRET=a1b2c3d4e5f6...  # From App Store Connect
DATABASE_URL=postgresql://...         # Auto-set by Railway
SECRET_KEY=...                        # Existing

# Webhook URL (set in App Store Connect)
https://beesmart-production.up.railway.app/apple-webhook
```

## Testing Checklist

```
Sandbox Testing:
□ Create sandbox account in App Store Connect
□ Sign out of real App Store on test device
□ Launch app → tap "Subscribe"
□ Sign in with sandbox account
□ Verify purchase completes
□ Check Railway logs for webhook
□ Verify user.is_premium_active() = True
□ Verify all 39 avatars unlocked
□ Wait 5 minutes (sandbox auto-renewal)
□ Verify DID_RENEW webhook received
□ Test restore purchases
□ Test cancellation flow
```
