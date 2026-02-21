# BeeSmart Avatar Product IDs

Single reference for avatar IAP product IDs. Use this to verify **App Store Connect (Apple)** and **Google Play** are configured correctly.

**Note:** These Apple IDs were verified at app approval. The only catalog exception is **YardStick Bee**, which uses `beesmart.avatar.yardstick_bee` (no `.v3`) in `data/avatars.catalog.json`; all other avatars use `.v3` in the catalog and the API strips it for Apple. No other product IDs were changed by the YardStick update.

---

## Convention

| Platform | Product ID format | Example |
|----------|-------------------|---------|
| **Apple (App Store Connect)** | `beesmart.avatar.<slug>` — **no** `.v3` suffix | `beesmart.avatar.al_bee` |
| **Google Play** | `beesmart.avatar.<slug>.v3` | `beesmart.avatar.al_bee.v3` |

- **Source of truth:** `data/avatars.catalog.json` (stores `iapProductId`; most entries use `.v3`).
- **Backend:** Avatars API strips trailing `.v3` when returning product IDs for Apple, so the picker sends the correct ID to StoreKit.
- **YardStick Bee** is the only avatar in the catalog with no `.v3` in `iapProductId`; it is correct for Apple as-is.

---

## Apple App Store Connect — product IDs (no .v3)

Verify each of these exists in App Store Connect with **exactly** this Product ID.

| # | Avatar (slug) | Display name | Apple product ID |
|---|----------------|--------------|-------------------|
| 1 | firefighter-bee | Firefighter Bee | `beesmart.avatar.firefighter_bee` |
| 2 | bk-bee | BK Bee | `beesmart.avatar.bk_bee` |
| 3 | franken-bee | Franken Bee | `beesmart.avatar.franken_bee` |
| 4 | yeti-bee | Yeti Bee | `beesmart.avatar.yeti_bee` |
| 5 | al-bee | Al Bee | `beesmart.avatar.al_bee` |
| 6 | knight-bee | Knight Bee | `beesmart.avatar.knight_bee` |
| 7 | inventor-bee | Inventor Bee | `beesmart.avatar.inventor_bee` |
| 8 | vamp-bee | Vamp Bee | `beesmart.avatar.vamp_bee` |
| 9 | doc-bee | Doc Bee | `beesmart.avatar.doc_bee` |
| 10 | o-bee | O Bee | `beesmart.avatar.o_bee` |
| 11 | xray-bee | Xray Bee | `beesmart.avatar.xray_bee` |
| 12 | fairy-bee | Fairy Bee | `beesmart.avatar.fairy_bee` |
| 13 | buda-bee | Buda Bee | `beesmart.avatar.buda_bee` |
| 14 | j-rock-bee | J Rock Bee | `beesmart.avatar.j_rock_bee` |
| 15 | super-bee | Super Bee | `beesmart.avatar.super_bee` |
| 16 | nurse-bee | Nurse Bee | `beesmart.avatar.nurse_bee` |
| 17 | motor-bee | Motor Bee | `beesmart.avatar.motor_bee` |
| 18 | honey-comb | Honey Comb | `beesmart.avatar.honey_comb` |
| 19 | gamer-bee | Gamer Bee | `beesmart.avatar.gamer_bee` |
| 20 | selfie-bee | Selfie Bee | `beesmart.avatar.selfie_bee` |
| 21 | umpire-bee | Umpire Bee | `beesmart.avatar.umpire_bee` |
| 22 | lumberjack-bee | Lumberjack Bee | `beesmart.avatar.lumberjack_bee` |
| 23 | cutie-bee | Cutie Bee | `beesmart.avatar.cutie_bee` |
| 24 | singer-bee | Singer Bee | `beesmart.avatar.singer_bee` |
| 25 | sea-bee | Sea Bee | `beesmart.avatar.sea_bee` |
| 26 | professor-bee | Professor Bee | `beesmart.avatar.professor_bee` |
| 27 | plumber-bee | Plumber Bee | `beesmart.avatar.plumber_bee` |
| 28 | space-bee | Space Bee | `beesmart.avatar.space_bee` |
| 29 | robo-bee | Robo Bee | `beesmart.avatar.robo_bee` |
| 30 | zom-bee | Zom Bee | `beesmart.avatar.zom_bee` |
| 31 | ware-bee | Ware Bee | `beesmart.avatar.ware_bee` |
| 32 | rocker-bee | Rocker Bee | `beesmart.avatar.rocker_bee` |
| 33 | diva-bee | Diva Bee | `beesmart.avatar.diva_bee` |
| 34 | techno-bee | Techno Bee | `beesmart.avatar.techno_bee` |
| 35 | queen-bee | Queen Bee | `beesmart.avatar.queen_bee` |
| 36 | buzz-bee | Buzz Bee | `beesmart.avatar.buzz_bee` |
| 37 | yardstick-bee | YardStick Bee | `beesmart.avatar.yardstick_bee` |

---

## Google Play

Google uses the same base IDs with a **`.v3`** suffix. See **store/GOOGLE_PLAY_PRODUCT_IDS.md** for the full table and Purchase option ID (hyphenated) format.

---

## Related files

- **`data/avatars.catalog.json`** — Source of truth; `iapProductId` per avatar (catalog uses `.v3` for most; backend strips for Apple).
- **`avatar_skus.py`** — Loads catalog, exposes `app_store_product_id_for_avatar()` / `AVATAR_SLUG_TO_APP_STORE_PRODUCT_ID`; fallback map uses `.v3` keys.
- **`AjaSpellBApp.py`** — Avatars API strips `.v3` from `product_id` when `use_google_play_ids` is False (Apple).
