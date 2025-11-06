# BeeKey System and Pack Assignments

This document summarizes how BeeKeys work in the BeeSmart Spelling Bee App and lists the current pack assignments. It covers static bundles (catalog-based) and dynamic 4-avatar BeeKey packs, how to create and redeem keys, and what’s returned.

## Overview

- A BeeKey is a short, human-friendly code that unlocks a pack of avatars for a user account.
- Two sources of packs exist:
  - Static bundles from the catalog (predefined packs).
  - Dynamic BeeKey packs generated on-demand (4 avatars per pack by default).
- Keys are validated server-side and applied idempotently (re-redeeming a key won’t duplicate unlocks).
- For compatibility, legacy dev keys are still accepted. DB-managed keys are preferred when present.

## Static Bundle Catalog (current assignments)

These packs live in `avatar_bundles.py` as `BUNDLE_CATALOG`. Slugs refer to avatar IDs used across the app.

- classroom_starter_pack — “Classroom Starter Pack”
  - Avatars: queen-bee, superbee, knight-bee, rocker-bee, doctor-bee
- family_fun_pack — “Family Fun Pack”
  - Avatars: cutie-bee, explorer-bee, singer-bee, astro-bee, biker-bee
  - Notes: astro-bee is an alias of space-bee; biker-bee is an alias of motor-bee

Legacy development keys map to these bundles (case-insensitive, spaces ignored):
- BEE-CLASS-STARTER-1 → classroom_starter_pack
- BEE-FAMILY-FUN-1 → family_fun_pack

You can also supply overrides via an environment JSON, for example:
- `BUNDLE_KEYS_JSON='{"SCHOOL-ABC-2025":"classroom_starter_pack"}'`

## Dynamic BeeKey Packs (on-demand 4-packs)

Admins can generate unique BeeKeys that unlock a custom 4-avatar pack. If no avatars are specified, the server picks 4 distinct active avatars automatically.

- Each dynamic pack is stored as a `DynamicBundle` with its own bundle_id (e.g., `beekey_12ab34cd`).
- A `BundleKey` record is created and associated with that bundle; usage and expiry can be configured.
- Redemptions are traced with IP and user-agent for auditing.

## Key Normalization & Behavior

- Normalization: whitespace removed and uppercased before lookup.
  - Example: `"  bee-key  abc 123  "` → `"BEE-KEYABC123"`
- Redemption is idempotent per user and pack; repeat redemption won’t grant duplicates.

### Error Conditions (non-exhaustive)
| Condition | HTTP | Error Field |
|-----------|------|-------------|
| Missing key | 400 | Missing key |
| Invalid key | 400 | Invalid key |
| Expired DB key | 400 | (reason from `can_redeem()`) |
| Usage exhausted | 400 | (reason from `can_redeem()`) |
| Key revoked | 400 | (reason from `can_redeem()`) |
| Redemption unavailable (no legacy map) | 503 | Redemption unavailable |
| DB commit failure | 500 | db_commit_failed:* |

## Admin Endpoints

All endpoints require an authenticated admin session.

- List bundle keys (DB-managed)
  - `GET /api/admin/bundle-keys`
  - Response: `{ success, bundle_keys: [ ...rows ] }`
- Create a bundle key for a static catalog pack
  - `POST /api/admin/bundle-keys`
  - Body: `{ bundle_id: string, max_uses?: int, expires_days?: int }`
  - Response: `{ success, bundle_key }`
- Generate a dynamic 4-avatar BeeKey pack
  - `POST /api/admin/bee-keys/generate`
  - Body: `{ avatar_ids?: [string,...], max_uses?: int, expires_days?: int, name?: string }`
  - Behavior: If `avatar_ids` omitted, server selects 4 random active avatars
  - Response: `{ success, bundle, bundle_key }`
- Revoke an existing key
  - `POST /api/admin/bundle-keys/{key_id}/revoke`
  - Response: `{ success, bundle_key }`
- List redemptions for a key
  - `GET /api/admin/bundle-keys/{key_id}/redemptions`
  - Response: `{ success, redemptions: [ ...rows ] }`

Notes:
- Static key creation only accepts bundle_ids from the current catalog.
- Dynamic packs are stored as `DynamicBundle` entries; redemptions recorded in `BundleKeyRedemption`.

## User Redemption Endpoint

- `POST /api/bundles/redeem`
- Body: `{ key: string }`
- Response: `{ success, bundle_id, bundle_name, source, unlocked_count, entitlements }`
  - `source`: `"db"` for DB-managed key; `"legacy"` for legacy in-memory key
  - `unlocked_count`: number of avatars newly granted during this call
  - `entitlements`: summary of the user’s avatar/bundle entitlements after redemption

## Key Lifecycle
1. Generate (static or dynamic)
2. Distribute (email, classroom handout, dashboard display)
3. Redeem (user enters key; server normalizes & validates)
4. Apply (entitlements updated; idempotent)
5. Trace (redemption audit row + purchase record)
6. Revoke / Expire (future attempts blocked)
7. Report (admin views redemption history)

## Pack Assignment Guidelines

For dynamic packs:
- Include variety (e.g., 1 exploratory, 1 themed, 1 fun/casual, 1 aspirational avatar).
- Avoid duplicates; server already enforces distinct selection.
- Use thematic names: “Science Night Pack”, “Reading Rally Pack”, etc.
- Keep total avatars ≤ 4 for clarity and balanced perceived value.

## Data Models (simplified)

- `BundleKey`: `{ key_raw, key_norm, bundle_id, max_uses, uses_count, expires_at, status, issued_by, redeemed_by?, redeemed_at?, created_at, updated_at }`
- `DynamicBundle`: `{ bundle_id, name, avatars: [string], created_at, created_by }`
- `BundleKeyRedemption`: `{ bundle_key_id, user_id, bundle_id, ip_address, user_agent, redeemed_at }`

## JSON Examples

- Create static key:
```json
{ "bundle_id": "classroom_starter_pack", "max_uses": 1, "expires_days": 30 }
```
- Generate dynamic BeeKey pack (explicit avatars):
```json
{ "avatar_ids": ["explorer-bee", "queen-bee", "rocker-bee", "astro-bee"], "max_uses": 10, "name": "Science Night Pack" }
```
- Redeem a key:
```json
{ "key": "BEE-CLASS-STARTER-1" }
```

## Operations & Testing

- Schema: `scripts/ensure_db_schema.py` creates BeeKey tables.
- Smoke test: `scripts/smoke_bundle_db_keys.py` (login → create key → redeem → second redemption).
- Auditing: DB key redemption writes to `BundleKeyRedemption` + `PurchaseRecord`.

## Security & Guardrails

- Server authoritative; no client-side entitlement logic.
- Implement rate limiting on creation & redemption in production.
- Avoid logging raw key content; prefer normalized or hashed forms.
- Revocation stops future redemptions; rollback of granted avatars is not automatic.

## Future Enhancements

- Pagination for key and redemption listings
- Rate limiting & anomaly detection (e.g., multiple failed attempts)
- Bulk generation & CSV export
- Thumbnail previews of avatars in admin key list
- Automated pytest coverage for expiry/exhaustion/revoke flows

## Change History (High Level)

- Added DB-managed `BundleKey`, `DynamicBundle`, `BundleKeyRedemption` models
- Enhanced redemption for dynamic bundles + audit logging
- Implemented admin endpoints for list/create/revoke/generate packs & view redemptions
- Integrated admin dashboard management panel

---
For updates to static packs, edit `avatar_bundles.py`. For new dynamic packs, use the Admin Dashboard BeeKey generator.
