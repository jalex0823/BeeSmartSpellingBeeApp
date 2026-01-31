# App Store Avatar IAP — Apple Email vs App

Comparison of **Apple’s approved in-app purchases** (from the App Store verification email) with **what the app uses** for avatar purchases (`avatar_skus.py` → `APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG`).

---

## Summary

| Source | Avatar product IDs | Subscription |
|--------|--------------------|--------------|
| **Apple (email)** | 36 | `com.beesmart.premium.monthly` |
| **App** | 36 (in `APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG`) | Same (in `PRODUCT_MAP`) |
| **Delta** | **0** — 1:1 match | — |

---

## Apple email (avatar product IDs only)

From the verification email, in the order listed:

| # | Product ID (Apple) | Reference name |
|---|--------------------|----------------|
| 1 | beesmart.avatar.firefighter_bee | Firefighter Bee Avatar |
| 2 | beesmart.avatar.bk_bee | BKBee Avatar |
| 3 | beesmart.avatar.franken_bee.v2 | Franken Bee Avatar |
| 4 | beesmart.avatar.yeti_bee.v2 | Yeti Bee Avatar |
| 5 | beesmart.avatar.al_bee.v2 | Al Bee Avatar |
| 6 | beesmart.avatar.knight_bee.v2 | Knight Bee Avatar |
| 7 | beesmart.avatar.inventor_bee.v2 | Inventor Bee Avatar |
| 8 | beesmart.avatar.vamp_bee.v2 | Vamp Bee Avatar |
| 9 | beesmart.avatar.doc_bee.v2 | Doc Bee Avatar |
| 10 | beesmart.avatar.o_bee.v2 | O Bee Avatar |
| 11 | beesmart.avatar.xray_bee.v2 | Xray Bee Avatar |
| 12 | beesmart.avatar.fairy_bee | Fairy Bee Avatar |
| 13 | beesmart.avatar.buda_bee.v2 | Buda Bee Avatar |
| 14 | beesmart.avatar.j_rock_bee.v2 | J Rock Bee Avatar |
| 15 | beesmart.avatar.super_bee.v2 | Super Bee Avatar |
| 16 | beesmart.avatar.nurse_bee.v2 | Nurse Bee Avatar |
| 17 | beesmart.avatar.motor_bee.v2 | Motor Bee Avatar |
| 18 | beesmart.avatar.honey_comb.v2 | Honey Comb Avatar |
| 19 | beesmart.avatar.gamer_bee | Gamer Bee Avatar |
| 20 | beesmart.avatar.selfie_bee.v2 | Selfie Bee Avatar |
| 21 | beesmart.avatar.umpire_bee.v2 | Umpire Bee Avatar |
| 22 | beesmart.avatar.lumberjack_bee.v2 | Lumberjack Bee Avatar |
| 23 | beesmart.avatar.cutie_bee.v2 | Cutie Bee Avatar |
| 24 | beesmart.avatar.singer_bee.v2 | Singer Bee Avatar |
| 25 | beesmart.avatar.sea_bee.v2 | Sea Bee Avatar |
| 26 | beesmart.avatar.professor_bee.v2 | Professor Bee Avatar |
| 27 | beesmart.avatar.plumber_bee.v2 | Plumber Bee Avatar |
| 28 | beesmart.avatar.space_bee.v2 | Space Bee Avatar |
| 29 | beesmart.avatar.robo_bee.v2 | Robo Bee Avatar |
| 30 | beesmart.avatar.zom_bee.v2 | Zom Bee Avatar |
| 31 | beesmart.avatar.ware_bee.v2 | Ware Bee Avatar |
| 32 | beesmart.avatar.rocker_bee.v2 | Rocker Bee Avatar |
| 33 | beesmart.avatar.diva_bee.v2 | Diva Bee Avatar |
| 34 | beesmart.avatar.techno_bee.v2 | Techno Bee Avatar |
| 35 | beesmart.avatar.queen_bee.v2 | Queen Bee Avatar |
| 36 | beesmart.avatar.buzz_bee.v2 | Buzz Bee Avatar |

*(Subscription: com.beesmart.premium.monthly — Premium Monthly Membership; not an avatar.)*

---

## App (`avatar_skus.py` → `APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG`)

The app maps each **exact** Apple product ID to the **catalog slug** used in the picker and API:

| Product ID (app) | Catalog slug |
|------------------|--------------|
| beesmart.avatar.firefighter_bee | firefighter-bee |
| beesmart.avatar.bk_bee | bk-bee |
| beesmart.avatar.franken_bee.v2 | franken-bee |
| beesmart.avatar.yeti_bee.v2 | yeti-bee |
| beesmart.avatar.al_bee.v2 | al-bee |
| beesmart.avatar.knight_bee.v2 | knight-bee |
| beesmart.avatar.inventor_bee.v2 | inventor-bee |
| beesmart.avatar.vamp_bee.v2 | vamp-bee |
| beesmart.avatar.doc_bee.v2 | doc-bee |
| beesmart.avatar.o_bee.v2 | o-bee |
| beesmart.avatar.xray_bee.v2 | xray-bee |
| beesmart.avatar.fairy_bee | fairy-bee |
| beesmart.avatar.buda_bee.v2 | buda-bee |
| beesmart.avatar.j_rock_bee.v2 | j-rock-bee |
| beesmart.avatar.super_bee.v2 | super-bee |
| beesmart.avatar.nurse_bee.v2 | nurse-bee |
| beesmart.avatar.motor_bee.v2 | motor-bee |
| beesmart.avatar.honey_comb.v2 | honey-comb |
| beesmart.avatar.gamer_bee | gamer-bee |
| beesmart.avatar.selfie_bee.v2 | selfie-bee |
| beesmart.avatar.umpire_bee.v2 | umpire-bee |
| beesmart.avatar.lumberjack_bee.v2 | lumberjack-bee |
| beesmart.avatar.cutie_bee.v2 | cutie-bee |
| beesmart.avatar.singer_bee.v2 | singer-bee |
| beesmart.avatar.sea_bee.v2 | sea-bee |
| beesmart.avatar.professor_bee.v2 | professor-bee |
| beesmart.avatar.plumber_bee.v2 | plumber-bee |
| beesmart.avatar.space_bee.v2 | space-bee |
| beesmart.avatar.robo_bee.v2 | robo-bee |
| beesmart.avatar.zom_bee.v2 | zom-bee |
| beesmart.avatar.ware_bee.v2 | ware-bee |
| beesmart.avatar.rocker_bee.v2 | rocker-bee |
| beesmart.avatar.diva_bee.v2 | diva-bee |
| beesmart.avatar.techno_bee.v2 | techno-bee |
| beesmart.avatar.queen_bee.v2 | queen-bee |
| beesmart.avatar.buzz_bee.v2 | buzz-bee |

---

## Delta (Apple email vs app)

- **In Apple, in app:** All 36 avatar product IDs from the email are present in `APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG` with the **exact same** product ID strings.
- **In app, not in Apple:** None.
- **In Apple, not in app:** None.

So for avatar purchases, **Apple’s list and the app are 1:1**; there are no deltas.

The subscription `com.beesmart.premium.monthly` is handled in `AjaSpellBApp.py` (`PRODUCT_MAP` / subscription config), not in the avatar map.
