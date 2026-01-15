# 9 New Bee Avatars - File Requirements

## Add-on: FireFighterBee + BKBee (2 new avatars)

These two avatars are now supported by the app catalog and avatar picker.

### Required Files

- **GLB models** → `/static/assets/avatars/glb_files/`
  - `FireFighterBee.glb`
  - `BKBee.glb`
- **PNG thumbnails** (must include `!`) → `/static/assets/avatars/glb_files/AvatarThumbnails/`
  - `FireFighterBee!.png`
  - `BKBee!.png`

### Catalog IDs / Product IDs

- **Firefighter Bee**
  - **ID:** `firefighter-bee`
  - **Product ID:** `beesmart.avatar.firefighter_bee`
- **BK Bee**
  - **ID:** `bk-bee`
  - **Product ID:** `beesmart.avatar.bk_bee`

## Overview
These 9 new premium avatars complete the alphabet coverage (A-Z) for BeeSmart Spelling Bee App.
All avatars are configured at **$1.99 premium tier** with 30,000 unlock points.

## Required Files

### GLB Files (3D Models)
Place in: `/static/assets/avatars/glb_files/`

1. `GamerBee.glb` - Gaming headset, controller
2. `InventorBee.glb` - Steampunk inventor with goggles, wrench
3. `LumberjackBee.glb` - Plaid shirt, axe, blue beanie
4. `NurseBee.glb` - Medical outfit with clipboard
5. `PlumberBee.glb` - Red hard hat, overalls, wrench
6. `TechnoBee.glb` - Black tech suit with glowing blue lines
7. `UmpireBee.glb` - Referee striped shirt, baseball
8. `XrayBee.glb` - Glowing skeleton/x-ray effect
9. `YetiBee.glb` - White furry ice costume

### PNG Thumbnails (2048x2048 recommended)
Place in: `/static/assets/avatars/glb_files/AvatarThumbnails/`

1. `GamerBee!.png`
2. `InventorBee!.png`
3. `LumberjackBee!.png`
4. `NurseBee!.png`
5. `PlumberBee!.png`
6. `TechnoBee!.png`
7. `UmpireBee!.png`
8. `XrayBee!.png`
9. `YetiBee!.png`

**Note:** PNG filenames MUST end with `!` before the extension (e.g., `GamerBee!.png`)

## Alphabet Coverage

After adding these 9 avatars, the app will have **41 total avatars** (including BK Bee + Firefighter Bee) covering all 26 letters:

- **A** = Al Bee
- **B** = Brother Bee, Buda Bee, Builder Bee, Buzz Bee
- **C** = Cool Bee, Cutie Bee
- **D** = Detective Bee, Diva Bee, Doc Bee
- **E** = Explorer Bee
- **F** = Franken Bee
- **G** = Gamer Bee ✨ NEW
- **H** = Honey Comb Bee
- **I** = Inventor Bee ✨ NEW
- **J** = J Rock Bee
- **K** = Knight Bee
- **L** = Lumberjack Bee ✨ NEW
- **M** = Mascot Bee, Motor Bee
- **N** = Nurse Bee ✨ NEW
- **O** = O Bee
- **P** = Professor Bee, Plumber Bee ✨ NEW
- **Q** = Queen Bee
- **R** = Robo Bee, Rocker Bee
- **S** = Seabea, Selfie Bee, Singer Bee, Space Bee, Super Bee
- **T** = Techno Bee ✨ NEW
- **U** = Umpire Bee ✨ NEW
- **V** = Vamp Bee
- **W** = Ware Bee
- **X** = Xray Bee ✨ NEW
- **Y** = Yeti Bee ✨ NEW
- **Z** = Zom Bee

## Avatar Details

### Gamer Bee
- **ID:** gamer-bee
- **Product ID:** beesmart.avatar.gamer_bee
- **Description:** Elite gamer bee with headset and controller! Levels up spelling skills!
- **Category:** classic
- **Tier:** premium
- **Price:** $1.99

### Inventor Bee
- **ID:** inventor-bee
- **Product ID:** beesmart.avatar.inventor_bee
- **Description:** Brilliant inventor bee with goggles and gadgets! Creates amazing spelling inventions!
- **Category:** adventure
- **Tier:** premium
- **Price:** $1.99

### Lumberjack Bee
- **ID:** lumberjack-bee
- **Product ID:** beesmart.avatar.lumberjack_bee
- **Description:** Rugged lumberjack bee with axe and plaid! Chops through tough words!
- **Category:** adventure
- **Tier:** premium
- **Price:** $1.99

### Nurse Bee
- **ID:** nurse-bee
- **Product ID:** beesmart.avatar.nurse_bee
- **Description:** Caring nurse bee with clipboard! Heals spelling mistakes with kindness!
- **Category:** classic
- **Tier:** premium
- **Price:** $1.99

### Plumber Bee
- **ID:** plumber-bee
- **Product ID:** beesmart.avatar.plumber_bee
- **Description:** Handy plumber bee with tools and overalls! Fixes spelling pipes and unclogs word jams!
- **Category:** classic
- **Tier:** premium
- **Price:** $1.99

### Techno Bee
- **ID:** techno-bee
- **Product ID:** beesmart.avatar.techno_bee
- **Description:** Futuristic techno bee with glowing circuits! High-tech spelling from the future!
- **Category:** fantasy
- **Tier:** premium
- **Price:** $1.99

### Umpire Bee
- **ID:** umpire-bee
- **Product ID:** beesmart.avatar.umpire_bee
- **Description:** Fair umpire bee with striped jersey! Calls spelling strikes and home runs!
- **Category:** adventure
- **Tier:** premium
- **Price:** $1.99

### Xray Bee
- **ID:** xray-bee
- **Product ID:** beesmart.avatar.xray_bee
- **Description:** Mysterious X-ray bee with glowing skeleton! Sees through tricky words with X-ray vision!
- **Category:** fantasy
- **Tier:** premium
- **Price:** $1.99

### Yeti Bee
- **ID:** yeti-bee
- **Product ID:** beesmart.avatar.yeti_bee
- **Description:** Fluffy yeti bee from snowy mountains! Cool, calm, and cuddly spelling expert!
- **Category:** fantasy
- **Tier:** premium
- **Price:** $1.99

## After Adding Files

1. **Generate App Store Cards:**
   ```bash
   python3 generate_avatar_cards_simple.py
   ```
   This will create 2048x2048 preview cards in `app_store_cards/`

2. **Verify Alphabetical Order:**
   ```bash
   python3 verify_alphabet_order.py
   ```
   Should show all 39 avatars in perfect A-Z order

3. **Test Locally:**
   - Start the app: `python3 AjaSpellBApp.py`
   - Go to avatar picker
   - Verify all 9 new avatars appear
   - Check they're in alphabetical order
   - Confirm pricing shows $1.99

4. **Deploy to Railway:**
   ```bash
   git add .
   git commit -m "Add 9 new premium avatars: Gamer, Inventor, Lumberjack, Nurse, Plumber, Techno, Umpire, Xray, Yeti - Complete A-Z alphabet coverage"
   git push
   ```

5. **Run Database Migration on Railway:**
   - Open Railway console
   - Run: `python3 add_avatar_indexes.py`
   - Verify indexes created successfully

## Database Updates

The catalog has been pre-configured with:
- ✅ Avatar metadata (names, descriptions, pricing)
- ✅ Thumbnail path mappings
- ✅ App Store card metadata
- ✅ Alphabetical ordering (automatic via sort_order)

No manual database updates needed - the catalog changes will sync automatically when the app loads.

## Apple App Store IAP Setup

Each avatar needs an In-App Purchase (IAP) configured in App Store Connect:

1. **GamerBee**: beesmart.avatar.gamer_bee - $1.99
2. **InventorBee**: beesmart.avatar.inventor_bee - $1.99
3. **LumberjackBee**: beesmart.avatar.lumberjack_bee - $1.99
4. **NurseBee**: beesmart.avatar.nurse_bee - $1.99
5. **PlumberBee**: beesmart.avatar.plumber_bee - $1.99
6. **TechnoBee**: beesmart.avatar.techno_bee - $1.99
7. **UmpireBee**: beesmart.avatar.umpire_bee - $1.99
8. **XrayBee**: beesmart.avatar.xray_bee - $1.99
9. **YetiBee**: beesmart.avatar.yeti_bee - $1.99

All avatar IAP names must end with " Avatar" suffix for Apple compliance.
