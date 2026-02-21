# BeeSmart Avatar Product IDs

Single reference for avatar IAP product IDs. Use this to verify **App Store Connect (Apple)** and **Google Play** are configured correctly.

**Note:** App Store Connect shows 36 approved IAPs; most use **`.v2`** (e.g. `beesmart.avatar.al_bee.v2`). A few have no suffix (e.g. `beesmart.avatar.bk_bee`, `beesmart.avatar.fairy_bee`, `beesmart.avatar.firefighter_bee`, `beesmart.avatar.gamer_bee`). The catalog stores `.v3`; the API converts to `.v2` for Apple.

---

## Convention

| Platform | Product ID format | Example |
|----------|-------------------|---------|
| **Apple (App Store Connect)** | `beesmart.avatar.<slug>.v2` (most); some no suffix | `beesmart.avatar.al_bee.v2` |
| **Google Play** | `beesmart.avatar.<slug>.v3` | `beesmart.avatar.al_bee.v3` |

- **Source of truth:** `data/avatars.catalog.json` (stores `iapProductId`; most entries use `.v3`).
- **Backend:** Avatars API replaces `.v3` with `.v2` when returning product IDs for Apple, so the picker sends the ID StoreKit expects. Catalog entries with no `.v3` (e.g. YardStick) are returned as-is.
- **PRODUCT_MAP** (verify/restore) already includes `.v2` and no-suffix keys via `avatar_skus.build_product_entitlements`.

---

## Apple App Store Connect — product IDs (.v2)

Verify each of these exists in App Store Connect. Most use **`.v2`**; a few (e.g. bk_bee, fairy_bee, firefighter_bee, gamer_bee) may have no suffix in App Store Connect.

| # | Avatar (slug) | Display name | Apple product ID |
|---|----------------|--------------|-------------------|
| 1 | firefighter-bee | Firefighter Bee | `beesmart.avatar.firefighter_bee` or `.v2` |
| 2 | bk-bee | BK Bee | `beesmart.avatar.bk_bee` |
| 3 | franken-bee | Franken Bee | `beesmart.avatar.franken_bee.v2` |
| 4 | yeti-bee | Yeti Bee | `beesmart.avatar.yeti_bee.v2` |
| 5 | al-bee | Al Bee | `beesmart.avatar.al_bee.v2` |
| 6 | knight-bee | Knight Bee | `beesmart.avatar.knight_bee.v2` |
| 7 | inventor-bee | Inventor Bee | `beesmart.avatar.inventor_bee.v2` |
| 8 | vamp-bee | Vamp Bee | `beesmart.avatar.vamp_bee.v2` |
| 9 | doc-bee | Doc Bee | `beesmart.avatar.doc_bee.v2` |
| 10 | o-bee | O Bee | `beesmart.avatar.o_bee.v2` |
| 11 | xray-bee | Xray Bee | `beesmart.avatar.xray_bee.v2` |
| 12 | fairy-bee | Fairy Bee | `beesmart.avatar.fairy_bee` |
| 13 | buda-bee | Buda Bee | `beesmart.avatar.buda_bee.v2` |
| 14 | j-rock-bee | J Rock Bee | `beesmart.avatar.j_rock_bee.v2` |
| 15 | super-bee | Super Bee | `beesmart.avatar.super_bee.v2` |
| 16 | nurse-bee | Nurse Bee | `beesmart.avatar.nurse_bee.v2` |
| 17 | motor-bee | Motor Bee | `beesmart.avatar.motor_bee.v2` |
| 18 | honey-comb | Honey Comb | `beesmart.avatar.honey_comb.v2` |
| 19 | gamer-bee | Gamer Bee | `beesmart.avatar.gamer_bee` |
| 20 | selfie-bee | Selfie Bee | `beesmart.avatar.selfie_bee.v2` |
| 21 | umpire-bee | Umpire Bee | `beesmart.avatar.umpire_bee.v2` |
| 22 | lumberjack-bee | Lumberjack Bee | `beesmart.avatar.lumberjack_bee.v2` |
| 23 | cutie-bee | Cutie Bee | `beesmart.avatar.cutie_bee.v2` |
| 24 | singer-bee | Singer Bee | `beesmart.avatar.singer_bee.v2` |
| 25 | sea-bee | Sea Bee | `beesmart.avatar.sea_bee.v2` |
| 26 | professor-bee | Professor Bee | `beesmart.avatar.professor_bee.v2` |
| 27 | plumber-bee | Plumber Bee | `beesmart.avatar.plumber_bee.v2` |
| 28 | space-bee | Space Bee | `beesmart.avatar.space_bee.v2` |
| 29 | robo-bee | Robo Bee | `beesmart.avatar.robo_bee.v2` |
| 30 | zom-bee | Zom Bee | `beesmart.avatar.zom_bee.v2` |
| 31 | ware-bee | Ware Bee | `beesmart.avatar.ware_bee.v2` |
| 32 | rocker-bee | Rocker Bee | `beesmart.avatar.rocker_bee.v2` |
| 33 | diva-bee | Diva Bee | `beesmart.avatar.diva_bee.v2` |
| 34 | techno-bee | Techno Bee | `beesmart.avatar.techno_bee.v2` |
| 35 | queen-bee | Queen Bee | `beesmart.avatar.queen_bee.v2` |
| 36 | buzz-bee | Buzz Bee | `beesmart.avatar.buzz_bee.v2` |
| 37 | yardstick-bee | YardStick Bee | `beesmart.avatar.yardstick_bee` (or `.v2` if in App Store) |

---

## Google Play

Google uses the same base IDs with a **`.v3`** suffix. See **store/GOOGLE_PLAY_PRODUCT_IDS.md** for the full table and Purchase option ID (hyphenated) format.

---

## Related files

- **`data/avatars.catalog.json`** — Source of truth; `iapProductId` per avatar (catalog uses `.v3` for most; backend strips for Apple).
- **`avatar_skus.py`** — Loads catalog, exposes `app_store_product_id_for_avatar()` / `AVATAR_SLUG_TO_APP_STORE_PRODUCT_ID`; fallback map uses `.v3` keys.
- **`AjaSpellBApp.py`** — Avatars API strips `.v3` from `product_id` when `use_google_play_ids` is False (Apple).
