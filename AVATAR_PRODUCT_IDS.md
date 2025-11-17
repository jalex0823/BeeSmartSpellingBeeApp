# Avatar Product IDs for Apple App Store IAP

**Generated:** November 13, 2025 (Updated November 17, 2025)  
**Format:** `beesmart.avatar.{slug_with_underscores}`  
**Total Avatars:** 39

## Product ID Format
- **Prefix:** `beesmart.avatar.`
- **Slug:** Avatar ID with hyphens replaced by underscores
- **Example:** `explorer-bee` → `beesmart.avatar.explorer_bee`

---

## Complete Product ID List (By Tier)

### DEFAULT FREE (5 avatars)
| Display Name | Avatar ID | Product ID |
|-------------|-----------|------------|
| Brother Bee Avatar | brother-bee | `beesmart.avatar.brother_bee` |
| Builder Bee Avatar | builder-bee | `beesmart.avatar.builder_bee` |
| Cool Bee Avatar | cool-bee | `beesmart.avatar.cool_bee` |
| Detective Bee Avatar | detective-bee | `beesmart.avatar.detective_bee` |
| Explorer Bee Avatar | explorer-bee | `beesmart.avatar.explorer_bee` |

### EARN OR BUY (7 avatars)
| Display Name | Avatar ID | Product ID |
|-------------|-----------|------------|
| Buzz Bee Avatar | buzz-bee | `beesmart.avatar.buzz_bee` |
| Cutie Bee Avatar | cutie-bee | `beesmart.avatar.cutie_bee` |
| Knight Bee Avatar | knight-bee | `beesmart.avatar.knight_bee` |
| Professor Bee Avatar | professor-bee | `beesmart.avatar.professor_bee` |
| Rocker Bee Avatar | rocker-bee | `beesmart.avatar.rocker_bee` |
| Selfie Bee Avatar | selfie-bee | `beesmart.avatar.selfie_bee` |
| Vamp Bee Avatar | vamp-bee | `beesmart.avatar.vamp_bee` |

### MASCOT (1 avatar)
| Display Name | Avatar ID | Product ID |
|-------------|-----------|------------|
| Mascot Bee Avatar | mascot-bee | `beesmart.avatar.mascot_bee` |

### PREMIUM (26 avatars)
| Display Name | Avatar ID | Product ID |
|-------------|-----------|------------|
| Al Bee Avatar | al-bee | `beesmart.avatar.al_bee` |
| Buda Bee Avatar | buda-bee | `beesmart.avatar.buda_bee` |
| Diva Bee Avatar | diva-bee | `beesmart.avatar.diva_bee` |
| Doc Bee Avatar | doc-bee | `beesmart.avatar.doc_bee` |
| Franken Bee Avatar | franken-bee | `beesmart.avatar.franken_bee` |
| Gamer Bee Avatar | gamer-bee | `beesmart.avatar.gamer_bee` |
| Honey Comb Avatar | honey-comb | `beesmart.avatar.honey_comb` |
| Inventor Bee Avatar | inventor-bee | `beesmart.avatar.inventor_bee` |
| J Rock Bee Avatar | j-rock-bee | `beesmart.avatar.j_rock_bee` |
| Lumberjack Bee Avatar | lumberjack-bee | `beesmart.avatar.lumberjack_bee` |
| Motor Bee Avatar | motor-bee | `beesmart.avatar.motor_bee` |
| Nurse Bee Avatar | nurse-bee | `beesmart.avatar.nurse_bee` |
| O Bee Avatar | o-bee | `beesmart.avatar.o_bee` |
| Plumber Bee Avatar | plumber-bee | `beesmart.avatar.plumber_bee` |
| Queen Bee Avatar | queen-bee | `beesmart.avatar.queen_bee` |
| Robo Bee Avatar | robo-bee | `beesmart.avatar.robo_bee` |
| Sea Bee Avatar | sea-bee | `beesmart.avatar.sea_bee` |
| Singer Bee Avatar | singer-bee | `beesmart.avatar.singer_bee` |
| Space Bee Avatar | space-bee | `beesmart.avatar.space_bee` |
| Super Bee Avatar | super-bee | `beesmart.avatar.super_bee` |
| Techno Bee Avatar | techno-bee | `beesmart.avatar.techno_bee` |
| Umpire Bee Avatar | umpire-bee | `beesmart.avatar.umpire_bee` |
| Ware Bee Avatar | ware-bee | `beesmart.avatar.ware_bee` |
| Xray Bee Avatar | xray-bee | `beesmart.avatar.xray_bee` |
| Yeti Bee Avatar | yeti-bee | `beesmart.avatar.yeti_bee` |
| Zom Bee Avatar | zom-bee | `beesmart.avatar.zom_bee` |

---

## Alphabetical Product ID List (All 39)

```
beesmart.avatar.al_bee
beesmart.avatar.brother_bee
beesmart.avatar.buda_bee
beesmart.avatar.builder_bee
beesmart.avatar.buzz_bee
beesmart.avatar.cool_bee
beesmart.avatar.cutie_bee
beesmart.avatar.detective_bee
beesmart.avatar.diva_bee
beesmart.avatar.doc_bee
beesmart.avatar.explorer_bee
beesmart.avatar.franken_bee
beesmart.avatar.gamer_bee
beesmart.avatar.honey_comb
beesmart.avatar.inventor_bee
beesmart.avatar.j_rock_bee
beesmart.avatar.knight_bee
beesmart.avatar.lumberjack_bee
beesmart.avatar.mascot_bee
beesmart.avatar.motor_bee
beesmart.avatar.nurse_bee
beesmart.avatar.o_bee
beesmart.avatar.plumber_bee
beesmart.avatar.professor_bee
beesmart.avatar.queen_bee
beesmart.avatar.robo_bee
beesmart.avatar.rocker_bee
beesmart.avatar.sea_bee
beesmart.avatar.selfie_bee
beesmart.avatar.singer_bee
beesmart.avatar.space_bee
beesmart.avatar.super_bee
beesmart.avatar.techno_bee
beesmart.avatar.umpire_bee
beesmart.avatar.vamp_bee
beesmart.avatar.ware_bee
beesmart.avatar.xray_bee
beesmart.avatar.yeti_bee
beesmart.avatar.zom_bee
```

---

## Apple App Store Connect Configuration

### Product Type
- **Consumable:** No
- **Non-Consumable:** Yes (for premium avatars)
- **Auto-Renewable Subscription:** No

### Pricing Tier
- Default Free: Not available for purchase (tier: free)
- Earn or Buy: Available through gameplay OR purchase
- Premium: Purchase only ($0.99 each)

### Localization
All product names must include " Avatar" suffix per Apple Store compliance:
- ✅ "Explorer Bee Avatar"
- ❌ "Explorer Bee" (will be rejected)

---

## Implementation Notes

1. **Catalog Integration:**
   - Product IDs are stored in `avatar_catalog.py`
   - Each avatar dictionary includes `"product_id"` field
   - API endpoint `/api/avatars` includes product_id in responses

2. **Database:**
   - Railway PostgreSQL already synced with 30 avatars
   - Product IDs available for IAP transaction linking

3. **Apple Store Setup:**
   - Use these exact product IDs in App Store Connect
   - Match pricing tiers with catalog pricing
   - Ensure all display names end with " Avatar"

4. **Testing:**
   - Use sandbox environment for IAP testing
   - Verify product_id matching between app and App Store Connect
   - Test purchase flow for each tier

---

## Verification

Run `count_avatars.py` to confirm all 30 avatars present:
```bash
python3 count_avatars.py
```

Expected output:
```
Total: 30
By tier:
  default_free: 5
  earn_or_buy: 7
  mascot: 1
  premium: 17
```

---

## Related Documentation
- **Full Avatar Sync:** `AVATAR_CATALOG_SYNC_COMPLETE_NOV13.md`
- **Apple IAP Setup:** `APP_STORE_IAP_SETUP.md`
- **Naming Standards:** `APPLE_IAP_NAMING_STANDARD.md`
- **Catalog Source:** `avatar_catalog.py`
