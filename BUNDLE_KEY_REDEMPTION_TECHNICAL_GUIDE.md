# Bundle Key Redemption System — Technical Guide

## Overview

The **Bundle Key Redemption System** is a comprehensive mechanism for distributing avatar bundles to users via time-limited, usage-limited redemption keys. The system uses database-managed keys that supersede legacy in-memory keys, supports both static predefined bundles and dynamic admin-created packs, tracks all redemption events for compliance/auditing, and ensures idempotent behavior to prevent duplicate unlocks.

---

## System Architecture

### Key Components

1. **BundleKey Model** (`models.py:1300–1372`)
   - Stores individual redemption keys with usage and expiry tracking
   - Supports single-use and multi-use (classroom/group) keys
   - Tracks creation, redemption, and status transitions

2. **DynamicBundle Model** (`models.py:1375–1395`)
   - Admin-created avatar bundles with custom avatar lists
   - Assigned a unique `bundle_id` (e.g., `beekey_abc12345`)
   - Can be shared via BundleKey codes

3. **BundleKeyRedemption Model** (`models.py:1398–1422`)
   - Audit trail table recording each redemption event
   - Captures user ID, bundle ID, IP address, user agent
   - Indexed by timestamp for analytics

4. **Redemption Endpoints**
   - `/api/bundles/redeem` — User redeems a bundle key
   - `/api/admin/bundle-keys` (GET/POST) — Admin manages keys
   - `/api/admin/bee-keys/generate` — Admin creates dynamic BeeKey packs
   - `/api/admin/bundle-keys/<key_id>/redemptions` — View redemption history
   - `/api/beekey/redeem-for-linked` — Admin redeems for linked students

---

## Data Model & Database Schema

### `bundle_keys` Table

| Column       | Type     | Nullable | Indexed | Notes |
|--------------|----------|----------|---------|-------|
| `id`         | Integer  | N        | Y       | Primary key |
| `key_raw`    | String80 | N        | N       | Human-readable form (e.g., `BEE-BUNDLE-2024-ABC123`) |
| `key_norm`   | String80 | N        | Y (U)   | Normalized (uppercase, no spaces); unique |
| `bundle_id`  | String100| N        | Y       | Reference to static or dynamic bundle |
| `max_uses`   | Integer  | N        | N       | 1 = single-use; >1 = multi-use |
| `uses_count` | Integer  | N        | N       | Current usage count |
| `expires_at` | DateTime | Y        | Y       | Expiry cutoff (UTC) |
| `status`     | String20 | N        | Y       | `active` \| `revoked` \| `expired` \| `exhausted` |
| `issued_by`  | FK(users)| Y        | Y       | Admin who created the key |
| `redeemed_by`| FK(users)| Y        | N       | Last user to redeem (single-use only) |
| `redeemed_at`| DateTime | Y        | N       | Timestamp of last redemption |
| `created_at` | DateTime | N        | Y       | Key creation time |
| `updated_at` | DateTime | N        | N       | Last modification time |

### `dynamic_bundles` Table

| Column       | Type     | Nullable | Indexed | Notes |
|--------------|----------|----------|---------|-------|
| `id`         | Integer  | N        | Y       | Primary key |
| `bundle_id`  | String120| N        | Y (U)   | Unique ID (e.g., `beekey_abc12345`) |
| `name`       | String200| N        | N       | Display name (e.g., "Zoo Adventure Pack") |
| `avatars`    | JSON     | N        | N       | Array of avatar slugs: `["avatar_slug1", "avatar_slug2", ...]` |
| `created_at` | DateTime | N        | Y       | Bundle creation time |
| `created_by` | FK(users)| Y        | Y       | Admin who created bundle |

### `bundle_key_redemptions` Table

| Column         | Type      | Nullable | Indexed | Notes |
|----------------|-----------|----------|---------|-------|
| `id`           | Integer   | N        | Y       | Primary key |
| `bundle_key_id`| FK(bundle_keys) | Y  | Y       | Reference to redeemed key |
| `user_id`      | FK(users) | Y        | Y       | User who redeemed |
| `bundle_id`    | String120 | N        | Y       | Bundle ID (denormalized for quick lookup) |
| `ip_address`   | String45  | Y        | N       | Client IP (IPv4/IPv6 safe) |
| `user_agent`   | String300 | Y        | N       | Browser/app user agent (truncated) |
| `redeemed_at`  | DateTime  | N        | Y       | Redemption timestamp |

---

## Key Methods

### BundleKey.normalize(raw: str) → str

Converts user input to canonical form for lookup:
- Removes all whitespace
- Uppercases all characters
- Used as unique index key for fast lookup

**Example:**
```python
BundleKey.normalize("BEE-BUNDLE-2024-ABC123")
# → "BEEBUNDLE2024ABC123"

BundleKey.normalize("bee bundle 2024 abc 123")
# → "BEEBUNDLE2024ABC123"
```

### BundleKey.generate(bundle_id: str, prefix: str = 'BEE') → tuple[str, str]

Admin utility to auto-generate a human-readable key:

**Returns:** `(key_raw, key_norm)`

**Example:**
```python
BundleKey.generate("standard_bundle_2024", prefix="BEE")
# → ("BEE-STANDA-2024-XYZ789", "BEESTANDA2024XYZ789")

BundleKey.generate("beekey_abc12345", prefix="BEEKEY")
# → ("BEEKEY-BEEKEY-2024-ABC456", "BEEKEY-BEEKEY-2024-ABC456")
```

### BundleKey.can_redeem() → tuple[bool, str]

Validates whether key is eligible for redemption:

| Status           | Reason          | Can Redeem? | Notes |
|------------------|-----------------|-------------|-------|
| `active`         | `ok`            | ✓           | Eligible |
| `revoked`        | `status_not_active` | ✗       | Admin revoked |
| `expired`        | `expired`       | ✗           | Past `expires_at` |
| `active` (exhausted) | `key_exhausted` | ✗      | Uses ≥ max_uses |
| `active` (valid) | `ok`            | ✓           | Can proceed |

**Example:**
```python
key = BundleKey.query.get(1)
can_redeem, reason = key.can_redeem()
if not can_redeem:
    # Handle rejection: reason ∈ {status_not_active, expired, key_exhausted}
```

### BundleKey.apply_use(user_id: int)

Increments usage counter; transitions status to `exhausted` if single-use limit reached.

**Side effects:**
- `uses_count` incremented
- `redeemed_by` set to `user_id`
- `redeemed_at` updated to current UTC time
- `status` changed to `exhausted` if `uses_count >= max_uses`

---

## Redemption Flow

### User Redeems Bundle Key via `/api/bundles/redeem`

**Request:**
```json
{
  "key": "BEE-BUNDLE-2024-ABC123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "bundle_id": "standard_bundle_2024",
  "bundle_name": "Standard 4-Avatar Bundle",
  "source": "db",
  "unlocked_count": 4,
  "entitlements": {
    "user_owned_avatars": ["avatar_slug1", "avatar_slug2", "avatar_slug3", "avatar_slug4"],
    "...": "..."
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid key" | "expired" | "key_exhausted" | "status_not_active"
}
```

### Processing Steps (AjaSpellBApp.py:7827–7920)

1. **Extract & Normalize Input**
   - Parse JSON: `data.get('key')`
   - Strip whitespace: `raw_key.strip()`
   - Normalize: `re.sub(r"\s+", "", raw_key).upper()`

2. **Lookup in Priority Order**
   - **Tier 1 (Preferred):** Check `BundleKey.query.filter_by(key_norm=norm_key).first()`
     - If found, call `bundle_key_row.can_redeem()` to validate
     - On rejection, return error with specific reason
   - **Tier 2 (Legacy):** Check `REDEEMABLE_KEYS[norm_key]` in-memory map
     - Fallback for pre-existing static keys

3. **Resolve Bundle Configuration**
   - Load `bundle_cfg` from `BUNDLE_CATALOG[bundle_id]` (static bundles)
   - Or query `DynamicBundle.query.filter_by(bundle_id=bundle_id).first()`
   - Extract `avatars` list and `name`

4. **Apply Entitlement**
   - Create product ID: `f"bundle:{bundle_id}"`
   - Call `_apply_entitlement(current_user, product_id)`
   - This grants avatar unlocks to user

5. **Record Redemption (DB Key Only)**
   - Increment `bundle_key_row.uses_count`
   - Call `bundle_key_row.apply_use(current_user.id)`
   - Create `BundleKeyRedemption` record with IP + user agent
   - Commit to database

6. **Log Purchase Record**
   - Create `PurchaseRecord` with `status='verified'`
   - Store redemption metadata in `raw_payload`
   - Commit

7. **Return Success Response**
   - Include `bundle_id`, `bundle_name`, `source`, unlock count
   - Include `_entitlements_summary()` showing all user avatars

---

## Admin Bundle Key Creation

### `/api/admin/bundle-keys` (GET)

Lists all bundle keys with filtering.

**Response Example:**
```json
{
  "success": true,
  "bundle_keys": [
    {
      "id": 1,
      "key_raw": "BEE-STANDARD-2024-XYZ789",
      "bundle_id": "standard_bundle_2024",
      "max_uses": 1,
      "uses_count": 0,
      "expires_at": "2025-12-31T23:59:59",
      "status": "active",
      "redeemed_by": null,
      "redeemed_at": null
    }
  ]
}
```

### `/api/admin/bundle-keys` (POST)

Creates a new redemption key for an existing static bundle.

**Request:**
```json
{
  "bundle_id": "standard_bundle_2024",
  "max_uses": 1,
  "expires_days": 365
}
```

**Response (Success):**
```json
{
  "success": true,
  "bundle_key": {
    "id": 2,
    "key_raw": "BEE-STANDARD-2024-ABC123",
    "key_norm": "BEESTANDARDD2024ABC123",
    "bundle_id": "standard_bundle_2024",
    "max_uses": 1,
    "uses_count": 0,
    "expires_at": "2025-12-31T23:59:59",
    "status": "active",
    "redeemed_by": null,
    "redeemed_at": null
  }
}
```

### `/api/admin/bee-keys/generate` (POST)

Creates a **dynamic** bundle (DynamicBundle) + associated key in one operation.

**Request:**
```json
{
  "avatar_ids": ["avatar_slug1", "avatar_slug2", "avatar_slug3", "avatar_slug4"],
  "max_uses": 10,
  "expires_days": 180,
  "name": "Zoo Adventure Pack"
}
```

**Or (auto-select 4 random avatars):**
```json
{
  "max_uses": 5,
  "expires_days": 90
}
```

**Response (Success):**
```json
{
  "success": true,
  "bundle": {
    "bundle_id": "beekey_abc12345",
    "name": "Zoo Adventure Pack",
    "avatars": ["avatar_slug1", "avatar_slug2", "avatar_slug3", "avatar_slug4"],
    "created_at": "2024-11-17T10:30:00"
  },
  "bundle_key": {
    "id": 3,
    "key_raw": "BEEKEY-BEEKEY-2024-XYZ789",
    "key_norm": "BEEKEY-BEEKEY-2024-XYZ789",
    "bundle_id": "beekey_abc12345",
    "max_uses": 5,
    "uses_count": 0,
    "expires_at": "2025-02-15T23:59:59",
    "status": "active",
    "redeemed_by": null,
    "redeemed_at": null
  }
}
```

---

## Admin Redemption for Linked Users

### `/api/beekey/redeem-for-linked` (POST)

Allows Admin/Parent/Teacher to redeem a BeeKey code and unlock avatars for **all** their linked students/children.

**Request:**
```json
{
  "beekey": "BEEKEY-BEEKEY-2024-XYZ789"
}
```

**Response (Success):**
```json
{
  "success": true,
  "bundle_id": "beekey_abc12345",
  "avatars_count": 4,
  "users_unlocked": ["student1_id", "student2_id", "student3_id"],
  "message": "Successfully unlocked avatars for 3 students"
}
```

**Key Behaviors:**
- Requires user to have `admin_key` or `teacher_key` relationship data
- Looks up all users linked via `admin_key_for` or `teacher_linked_students` relationships
- Applies entitlements to **each** linked student independently
- Single DB key usage is recorded once (not per student)
- If any student unlock fails, the operation still logs partial success

---

## Admin Key Management Endpoints

### `/api/admin/bundle-keys/<key_id>/redemptions` (GET)

View all redemption history for a specific key.

**Response:**
```json
{
  "success": true,
  "redemptions": [
    {
      "id": 1,
      "bundle_key_id": 1,
      "user_id": 42,
      "bundle_id": "standard_bundle_2024",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
      "redeemed_at": "2024-11-10T14:32:00"
    }
  ]
}
```

### `/api/admin/bundle-keys/<key_id>/revoke` (POST)

Immediately revoke a key (prevent further redemptions).

**Request:** (empty body)

**Response:**
```json
{
  "success": true,
  "message": "Key revoked",
  "bundle_key": {
    "id": 1,
    "status": "revoked",
    "...": "..."
  }
}
```

---

## Legacy Static Bundles (BUNDLE_CATALOG)

### In-Memory Configuration

Static bundles are defined in code (e.g., `avatar_bundles.py` or hardcoded in `AjaSpellBApp.py`):

```python
BUNDLE_CATALOG = {
    "standard_bundle_2024": {
        "name": "Standard 4-Avatar Bundle",
        "avatars": ["avatar_slug1", "avatar_slug2", "avatar_slug3", "avatar_slug4"]
    },
    "premium_bundle_2024": {
        "name": "Premium Bundle (6 avatars)",
        "avatars": ["avatar_slug5", "avatar_slug6", "avatar_slug7", "avatar_slug8", "avatar_slug9", "avatar_slug10"]
    }
}
```

### Legacy REDEEMABLE_KEYS Map

Old in-memory key registry (superseded by `BundleKey` table):

```python
REDEEMABLE_KEYS = {
    "BEESTANDARDD2024ABC123": "standard_bundle_2024",
    "BEEPREMIUM2024XYZ789": "premium_bundle_2024"
}
```

**Lookup Priority:**
1. Check `BundleKey` table (database, preferred)
2. Fall back to `REDEEMABLE_KEYS` (in-memory, legacy)

---

## Idempotency & Duplicate Prevention

### Why Idempotent?

A user **can** redeem the **same key multiple times** (if `max_uses > 1`), but the system ensures:

1. **No duplicate avatar unlocks** → Each avatar unlock is tracked in user's entitlements
2. **Usage counter increments** → Each redemption increments `uses_count`
3. **Status transitions** → Single-use key moves to `exhausted` after first redeem
4. **Audit trail preserved** → Each redemption creates a new `BundleKeyRedemption` record

### Example: Single-Use Key

```
User A redeems key (max_uses=1):
  → uses_count: 0 → 1
  → status: active → exhausted
  → redeemed_by: User A
  → redeemed_at: 2024-11-17T10:30:00
  → Unlock avatars

User B tries same key:
  → can_redeem() returns (False, 'key_exhausted')
  → Redemption fails with error
```

### Example: Multi-Use Key (Classroom)

```
Teacher creates key (max_uses=30):
  → Initial state: uses_count=0, status=active

Student 1 redeems:
  → uses_count: 0 → 1
  → status: active (unchanged, not exhausted yet)
  → Avatars unlocked

Student 2 redeems:
  → uses_count: 1 → 2
  → status: active (unchanged)
  → Avatars unlocked

... repeat for 28 more students ...

Student 30 redeems:
  → uses_count: 29 → 30
  → status: active → exhausted (now equal to max_uses)
  → Avatars unlocked

Student 31 tries:
  → can_redeem() returns (False, 'key_exhausted')
  → Redemption fails
```

---

## Error Handling & Validation

### Validation Checks

| Check | Location | Condition | Error |
|-------|----------|-----------|-------|
| Key present | User input | `raw_key.strip()` empty | `"Missing key"` (400) |
| Catalog available | System config | `REDEEMABLE_KEYS` missing | `"Redemption unavailable"` (503) |
| Key exists | Database lookup | No row found, no legacy key | `"Invalid key"` (400) |
| Key status | `can_redeem()` | `status != 'active'` | `"status_not_active"` (400) |
| Key expired | `can_redeem()` | `datetime.utcnow() > expires_at` | `"expired"` (400) |
| Key exhausted | `can_redeem()` | `uses_count >= max_uses` | `"key_exhausted"` (400) |
| Bundle config | Resolution | Bundle not in catalog/DB | `"Bundle not found"` (500) |
| DB commit | Transaction | Commit failed | `"db_commit_failed: {e}"` (500) |

---

## Compliance & Auditing

### PurchaseRecord

Each redemption creates a `PurchaseRecord` entry:

| Field | Value |
|-------|-------|
| `user_id` | Current user ID |
| `platform` | `'web'` |
| `product_id` | `f"bundle:{bundle_id}"` |
| `status` | `'verified'` |
| `transaction_id` | `None` |
| `purchase_token` | `None` |
| `raw_payload` | `{'redeemed_key': norm_key, 'bundle_id': bundle_id, 'apply_result': ...}` |

### BundleKeyRedemption

Captures full audit trail:
- **User ID** — Who redeemed
- **Bundle ID** — What bundle was unlocked
- **IP Address** — Geographic/network origin (compliance)
- **User Agent** — Browser/app context
- **Timestamp** — When redemption occurred

**Queries:**
```sql
-- All redemptions for a key
SELECT * FROM bundle_key_redemptions
WHERE bundle_key_id = ?
ORDER BY redeemed_at DESC;

-- All redemptions by a user
SELECT * FROM bundle_key_redemptions
WHERE user_id = ?
ORDER BY redeemed_at DESC;

-- Recent redemptions (last 24 hours)
SELECT * FROM bundle_key_redemptions
WHERE redeemed_at > NOW() - INTERVAL '1 day'
ORDER BY redeemed_at DESC;
```

---

## Best Practices

### For Admins

1. **Use Dynamic Bundles for One-Off Packs**
   - Call `/api/admin/bee-keys/generate` to auto-create custom pack + key

2. **Set Appropriate Expiry**
   - `expires_days=0` → No expiry
   - `expires_days=365` → Valid for 1 year
   - `expires_days=7` → Limited-time promotion

3. **Use Multi-Use Keys for Classrooms**
   - `max_uses=30` → Allows 30 students to redeem same key
   - Prevents needing 30 individual keys

4. **Monitor Redemption History**
   - Regularly check `/api/admin/bundle-keys/<key_id>/redemptions`
   - Verify no fraudulent activity (IP patterns, timing)

5. **Revoke Compromised Keys**
   - If key leaked, call `/api/admin/bundle-keys/<key_id>/revoke`
   - Prevents further unauthorized redemptions

### For Frontend/Client

1. **Normalize User Input**
   - Strip whitespace before submission
   - Accept case-insensitive input

2. **Handle Error Responses**
   ```javascript
   POST /api/bundles/redeem with { key: "..." }
   
   if (response.success) {
     // Show unlock message
     showSuccess(`Unlocked ${response.unlocked_count} avatars!`);
     refreshAvatarList(response.entitlements);
   } else {
     // Show error message
     switch (response.error) {
       case 'expired':
         showError('This key has expired.');
         break;
       case 'key_exhausted':
         showError('This key has been fully redeemed.');
         break;
       case 'Invalid key':
         showError('Invalid or unknown key.');
         break;
       default:
         showError(response.error || 'Redemption failed.');
     }
   }
   ```

3. **Prevent Double-Submit**
   - Disable button during submission
   - Clear input field on success

---

## Integration with IAP (In-App Purchase)

### Product Map

The system integrates with IAP by registering bundles in `PRODUCT_MAP`:

```python
product_id = f"bundle:{bundle_id}"
if product_id not in PRODUCT_MAP:
    PRODUCT_MAP[product_id] = {
        'type': 'bundle',
        'bundle_id': bundle_id,
        'avatars': avatars
    }
```

### Flow

1. User redeems key → `_apply_entitlement()` called
2. `_apply_entitlement()` grants avatars to user (adds to entitlements)
3. User sees avatars in avatar selector immediately
4. Frontend/app refreshes avatar list via `/api/avatars` or similar

---

## Troubleshooting

### Key Redemption Fails

**Symptom:** User sees error: `"Invalid key"`

**Diagnostics:**
1. Check `BundleKey` table: `SELECT * FROM bundle_keys WHERE key_norm = ?;`
2. Check legacy map: Does `REDEEMABLE_KEYS[norm_key]` exist?
3. Verify normalization: `BundleKey.normalize(raw_key)` matches stored `key_norm`

**Solution:**
- If DB key missing, create via `/api/admin/bundle-keys` or `/api/admin/bee-keys/generate`
- If legacy key, add to `REDEEMABLE_KEYS` map in code

### Key Marked "Expired" But Should Be Active

**Symptom:** `can_redeem()` returns `(False, 'expired')`

**Diagnostics:**
```python
key = BundleKey.query.get(key_id)
print(f"expires_at: {key.expires_at}")
print(f"now: {datetime.utcnow()}")
print(f"is_expired: {key.is_expired()}")
```

**Solution:**
- If `expires_at` is None → Not set, shouldn't be expired
- If `expires_at` is past → Extend via admin query or recreate key
- Check server timezone (should use UTC)

### Key Shows "Exhausted" But max_uses > uses_count

**Symptom:** `status='exhausted'` but `uses_count (5) < max_uses (10)`

**Root Cause:** Possible race condition or manual database edit

**Solution:**
- Review `BundleKeyRedemption` records to verify actual usage
- If erroneous, admin can manually update `status='active'` and `uses_count`
- Recommend using admin dashboard for all key management

---

## Summary

The Bundle Key Redemption System provides:

✓ **Flexible Distribution** — Static bundles + dynamic admin-created packs
✓ **Usage Control** — Single-use and multi-use keys
✓ **Time Limits** — Expiry dates for promotional campaigns
✓ **Audit Trail** — Full compliance tracking of all redemptions
✓ **Idempotency** — No duplicate avatar unlocks
✓ **Backward Compatibility** — Legacy in-memory keys still work
✓ **Admin Oversight** — Complete redemption history and key management

This enables businesses to run campaigns, distribute classroom keys, and grant promotional bundles while maintaining full visibility into usage and preventing fraud.
