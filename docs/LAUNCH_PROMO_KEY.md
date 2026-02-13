# Launch promo key (90 days, one per account)

One shared code for social distribution. Valid 90 days; each account can redeem once (idempotent).

## Single source of truth for the code

**To change the promo code in one place:**

1. **Config:** Set `REDEEM_CODE_PLACEHOLDER` in `config.py` (default: blank - leave empty to not reveal the code), or set the env var `REDEEM_CODE_PLACEHOLDER` in `.env` to show a hint (e.g. `BEESPECIAL2026`).
2. **UI:** The avatar picker “Redeem code” input placeholder uses this value automatically.
3. **Admin key:** When creating the bundle key (below), use the same value for `key_raw`.
4. **Social copy:** Use that same code in posts and bios.

No need to edit the template or doc each time — only config (and creating a new key when you change the code).

---

## Bundle: Launch Pack

**Bundle ID:** `launch_pack_2025`  
**Avatars (5):** BK Bee, Gamer Bee, Super Bee, Techno Bee, Knight Bee  

Defined in `avatar_bundles.py` under `BUNDLE_CATALOG["launch_pack_2025"]`.

**Not included (so promo stays valuable):**
- **Brother Bee (BroBee)** — already free at registration (`default_free`). Including it would give nothing extra.

---

## Create the key (admin, once at launch)

1. Ensure `ALLOW_KEY_REDEMPTION=1` (and `APP_STORE_BUILD` not `1`) so the admin endpoint is available.
2. As an admin, POST to create a key with **custom code** and 90-day expiry. Use the same value as `REDEEM_CODE_PLACEHOLDER` (see above) for `key_raw`:

```json
POST /api/admin/bundle-keys
Content-Type: application/json

{
  "bundle_id": "launch_pack_2025",
  "key_raw": "<same as REDEEM_CODE_PLACEHOLDER, e.g. BEESPECIAL2026>",
  "max_uses": 5000,
  "expires_days": 90
}
```

3. Response will include the same `key_raw` — that’s the code to share.

**Notes:**
- `key_raw` is optional; if omitted, the server generates a random code.
- `max_uses` = total redemptions allowed (different users). Each user still only gets the pack once if they redeem again.
- `expires_days`: 90 → key stops working 90 days after creation.

---

## Where users enter the code

**Avatar picker only** (to avoid confusion): From the main menu, tap **Avatars** (or **Change Avatar** on the dashboard). At the top of the avatar picker, tap **Redeem code**, enter the code (the placeholder in the field shows the current one), and tap **Redeem**. The grid refreshes so new avatars appear unlocked.

---

## Social copy (example)

Use the code from `REDEEM_CODE_PLACEHOLDER` when you change it.

- **Post:** “To celebrate our launch, unlock the Launch Pack free. In the app, open Redeem code and enter: **BEESPECIAL2026**. One per account, valid for 90 days.”
- **Bio / link:** “Free Launch Pack — use code **BEESPECIAL2026** in the app (one per account, 90 days).”

---

## Changing the pack or code

- **Different avatars:** Edit `avatar_bundles.py` → `BUNDLE_CATALOG["launch_pack_2025"]["avatars"]`, then redeploy.
- **Different code:** Update `REDEEM_CODE_PLACEHOLDER` in config (or `.env`), then create a new key with that value as `key_raw`. Old code keeps working until it expires or is revoked.
- **Revoke early:** `POST /api/admin/bundle-keys/<key_id>/revoke`.

---

## Free-at-registration avatars (do not put in promo pack)

These are already unlocked for new users; including them in the pack adds no value:

- Brother Bee (`brother-bee`)
- Builder Bee (`builder-bee`)
- Cool Bee (`cool-bee`)
- Detective Bee (`detective-bee`)
- Explorer Bee (`explorer-bee`)
- Mascot Bee (`mascot-bee`)

Source: `avatar_catalog.py` entries with `is_default_free: True`.
