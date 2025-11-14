# 🐝 Avatar Pricing - Complete Reference
**Date Locked Down**: November 13, 2025  
**Source of Truth**: `avatar_catalog.py` lines 665-697

---

## ✅ VERIFIED APP PRICING (via Python execution)

```
🐝 BEESMART SPELLING - OFFICIAL AVATAR PRICING
================================================================================

FREE AVATARS (6 total)
--------------------------------------------------------------------------------
  • Brother Bee          | default_free    |      0 points
  • Builder Bee          | default_free    |      0 points
  • Cool Bee             | default_free    |      0 points
  • Detective Bee        | default_free    |      0 points
  • Explorer Bee         | default_free    |      0 points
  • Mascot Bee           | mascot          |      0 points

$0.99 AVATARS (11 total)
--------------------------------------------------------------------------------
  • Doctor Bee           |   2,000 points | earn_or_buy
  • Buzz Bee             |   3,000 points | earn_or_buy
  • Knight Bee           |   4,000 points | earn_or_buy
  • Anxious Bee          |   5,000 points | special
  • Selfie Bee           |   5,000 points | earn_or_buy
  • Monster Bee          |   6,000 points | earn_or_buy
  • Rocker Bee           |   8,000 points | earn_or_buy
  • Seabea               |  10,000 points | earn_or_buy
  • Professor Bee        |  22,000 points | premium
  • Vamp Bee             |  24,000 points | premium
  • Franken Bee          |  25,000 points | premium

$1.99 AVATARS (9 total)
--------------------------------------------------------------------------------
  • Diva Bee             |  12,000 points | premium
  • Biker Bee            |  15,000 points | premium
  • Astro Bee            |  18,000 points | premium
  • Al Bee               |  20,000 points | premium
  • Zom Bee              |  25,000 points | premium
  • Superbee             |  26,000 points | premium
  • Ware Bee             |  27,000 points | premium
  • Queen Bee            |  28,000 points | premium
  • Robo Bee             |  30,000 points | premium

TOTAL: 26 avatars
  • FREE: 6
  • $0.99: 11
  • $1.99: 9
```

---

## 📱 App Store Connect Product IDs

### $0.99 Tier (11 products)
```
com.beesmart.avatar.doctor_bee      → Doctor Bee (2,000 pts)
com.beesmart.avatar.buzz_bee        → Buzz Bee (3,000 pts)
com.beesmart.avatar.knight_bee      → Knight Bee (4,000 pts)
com.beesmart.avatar.anxious_bee     → Anxious Bee (5,000 pts)
com.beesmart.avatar.selfie_bee      → Selfie Bee (5,000 pts)
com.beesmart.avatar.monster_bee     → Monster Bee (6,000 pts)
com.beesmart.avatar.rocker_bee      → Rocker Bee (8,000 pts)
com.beesmart.avatar.seabea          → Seabea (10,000 pts)
com.beesmart.avatar.professor_bee   → Professor Bee (22,000 pts)
com.beesmart.avatar.vamp_bee        → Vamp Bee (24,000 pts)
com.beesmart.avatar.franken_bee     → Franken Bee (25,000 pts)
```

### $1.99 Tier (9 products)
```
com.beesmart.avatar.diva_bee        → Diva Bee (12,000 pts)
com.beesmart.avatar.biker_bee       → Biker Bee (15,000 pts)
com.beesmart.avatar.astro_bee       → Astro Bee (18,000 pts)
com.beesmart.avatar.al_bee          → Al Bee (20,000 pts)
com.beesmart.avatar.zom_bee         → Zom Bee (25,000 pts)
com.beesmart.avatar.superbee        → Superbee (26,000 pts)
com.beesmart.avatar.ware_bee        → Ware Bee (27,000 pts)
com.beesmart.avatar.queen_bee       → Queen Bee (28,000 pts)
com.beesmart.avatar.robo_bee        → Robo Bee (30,000 pts)
```

**Total IAPs to create**: 20 products

---

## 🖼️ Screenshot Specifications

**App Store Connect Requirements:**
- **Dimensions**: 640×920 pixels (iPhone 6.5" Display)
- **Format**: PNG or JPG
- **Transparency**: MUST be opaque (no alpha channel)
- **File Size**: Maximum 500KB per image
- **Quantity**: 3-10 screenshots recommended

**How to capture:**
1. Open iOS Simulator (iPhone 15 Pro)
2. Run app in Xcode
3. Navigate to desired screen
4. Press **Cmd+S** → screenshot auto-saves to Desktop
5. Screenshots are automatically opaque ✅

---

## 🧑‍💻 Code Reference

### avatar_catalog.py (Lines 665-697)
```python
# Business rule (2025-11-13):
# All locked avatars default to $0.99 unless explicitly listed otherwise
# Premium set priced at $0.99 each (12 avatars): doctor-bee, knight-bee,
# monster-bee, rocker-bee, seabea, buzz-bee, selfie-bee, anxious-bee,
# professor-bee, vamp-bee, franken-bee, obee
# Ultra Premium set priced at $1.99 each (9 avatars or via bundle): al-bee,
# astro-bee, biker-bee, diva-bee, superbee, queen-bee, robo-bee, ware-bee, zom-bee

DEFAULT_LOCKED_PRICE = 0.99

PREMIUM_199_IDS = {
    "al-bee", "astro-bee", "biker-bee", "diva-bee",
    "superbee", "queen-bee", "robo-bee", "ware-bee", "zom-bee"
}

EARN_OR_BUY_POINTS = {
    "doctor-bee": 2000,
    "knight-bee": 4000,
    "monster-bee": 6000,
    "rocker-bee": 8000,
    "seabea": 10000
}

# Programmatic override — applies prices at module load time
for a in AVATAR_CATALOG:
    if not a.get("is_default_free", False):
        a["price"] = DEFAULT_LOCKED_PRICE  # Sets $0.99 for all locked avatars
    if a.get("id") in PREMIUM_199_IDS:
        a["price"] = 1.99  # Overrides to $1.99 for ultra premium set
    if a.get("id") in EARN_OR_BUY_POINTS:
        a["unlock_points"] = EARN_OR_BUY_POINTS[a["id"]]  # Enforces specific thresholds
```

**Verification command:**
```bash
cd /Users/jalex0823/Dropbox/GitBackUpAppFolder && python3 -c "
from avatar_catalog import AVATAR_CATALOG
import json
all_avatars = sorted([{
    'id': a['id'],
    'name': a['name'],
    'price': a.get('price', 0),
    'points': a.get('unlock_points', 0)
} for a in AVATAR_CATALOG], key=lambda x: x['points'])
print(json.dumps(all_avatars, indent=2))
"
```

---

## 📄 Documentation Files Created

1. **APP_STORE_IAP_SETUP.md**
   - Complete IAP creation guide
   - Product ID table with all 20 avatars
   - Step-by-step App Store Connect workflow
   - Screenshot requirements
   - Pre-submission checklist

2. **WEBSITE_AVATAR_PRICING_TABLE.html**
   - HTML table for website integration
   - Styled with BeeSmart theme colors
   - Shows all 26 avatars with pricing
   - Matches app code exactly

3. **AVATAR_PRICING_LOCKED_NOV13.md** (this file)
   - Central reference document
   - Verified pricing from app code
   - Product ID list
   - Code snippets for maintenance

---

## ✅ Consistency Verification

**App Code** (`avatar_catalog.py`): ✅ VERIFIED  
**Website Table** (`WEBSITE_AVATAR_PRICING_TABLE.html`): ✅ CREATED  
**App Store Connect**: ⏳ PENDING (20 IAPs to create)

**Status**: Pricing locked down and documented. Ready for IAP creation.

---

## 🚀 Next Actions

1. ✅ **Pricing Audit Complete** (verified via Python execution)
2. ✅ **Documentation Created** (3 new files)
3. ⏳ **Create 20 IAP products** in App Store Connect (see APP_STORE_IAP_SETUP.md)
4. ⏳ **Upload opaque screenshots** (640×920px from iOS Simulator)
5. ⏳ **Complete submission checklist** (privacy policy, age rating, etc.)
6. ⏳ **Submit for App Store review**

**Estimated time to complete IAPs**: 100-200 minutes (5-10 min per avatar × 20)

---

## 📞 Support

If pricing needs to change in the future:

1. Update `PREMIUM_199_IDS` set in `avatar_catalog.py` (lines 674-677)
2. Re-run verification command to confirm changes
3. Update App Store Connect IAP prices (can take 24-48 hours to propagate)
4. Update website table HTML
5. Deploy updated `avatar_catalog.py` to Railway

**Last Verified**: November 13, 2025 @ 11:30 PM PST  
**Verification Method**: Direct Python execution of `avatar_catalog.py`  
**Status**: ✅ LOCKED AND VERIFIED
