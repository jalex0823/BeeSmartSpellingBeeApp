# 9 New Avatars - Naming Reference

## ✅ Complete Naming Consistency Check

This document confirms all naming is consistent across the entire codebase.

---

## 1. GAMER BEE (Letter G)

**Database/Catalog ID:** `gamer-bee`  
**Product ID:** `beesmart.avatar.gamer_bee`  
**Display Name:** `Gamer Bee Avatar`  
**GLB File:** `GamerBee.glb`  
**PNG Thumbnail:** `GamerBee!.png`  
**App Store Key:** `GamerBee`

---

## 2. INVENTOR BEE (Letter I)

**Database/Catalog ID:** `inventor-bee`  
**Product ID:** `beesmart.avatar.inventor_bee`  
**Display Name:** `Inventor Bee Avatar`  
**GLB File:** `InventorBee.glb`  
**PNG Thumbnail:** `InventorBee!.png`  
**App Store Key:** `InventorBee`

---

## 3. LUMBERJACK BEE (Letter L)

**Database/Catalog ID:** `lumberjack-bee`  
**Product ID:** `beesmart.avatar.lumberjack_bee`  
**Display Name:** `Lumberjack Bee Avatar`  
**GLB File:** `LumberjackBee.glb`  
**PNG Thumbnail:** `LumberjackBee!.png`  
**App Store Key:** `LumberjackBee`

---

## 4. NURSE BEE (Letter N)

**Database/Catalog ID:** `nurse-bee`  
**Product ID:** `beesmart.avatar.nurse_bee`  
**Display Name:** `Nurse Bee Avatar`  
**GLB File:** `NurseBee.glb`  
**PNG Thumbnail:** `NurseBee!.png`  
**App Store Key:** `NurseBee`

---

## 5. PLUMBER BEE (Letter P)

**Database/Catalog ID:** `plumber-bee`  
**Product ID:** `beesmart.avatar.plumber_bee`  
**Display Name:** `Plumber Bee Avatar`  
**GLB File:** `PlumberBee.glb`  
**PNG Thumbnail:** `PlumberBee!.png`  
**App Store Key:** `PlumberBee`

---

## 6. TECHNO BEE (Letter T)

**Database/Catalog ID:** `techno-bee`  
**Product ID:** `beesmart.avatar.techno_bee`  
**Display Name:** `Techno Bee Avatar`  
**GLB File:** `TechnoBee.glb`  
**PNG Thumbnail:** `TechnoBee!.png`  
**App Store Key:** `TechnoBee`

---

## 7. UMPIRE BEE (Letter U)

**Database/Catalog ID:** `umpire-bee`  
**Product ID:** `beesmart.avatar.umpire_bee`  
**Display Name:** `Umpire Bee Avatar`  
**GLB File:** `UmpireBee.glb`  
**PNG Thumbnail:** `UmpireBee!.png`  
**App Store Key:** `UmpireBee`

---

## 8. XRAY BEE (Letter X)

**Database/Catalog ID:** `xray-bee`  
**Product ID:** `beesmart.avatar.xray_bee`  
**Display Name:** `Xray Bee Avatar`  
**GLB File:** `XrayBee.glb`  
**PNG Thumbnail:** `XrayBee!.png`  
**App Store Key:** `XrayBee`

---

## 9. YETI BEE (Letter Y)

**Database/Catalog ID:** `yeti-bee`  
**Product ID:** `beesmart.avatar.yeti_bee`  
**Display Name:** `Yeti Bee Avatar`  
**GLB File:** `YetiBee.glb`  
**PNG Thumbnail:** `YetiBee!.png`  
**App Store Key:** `YetiBee`

---

## File Naming Pattern

All files follow the **PascalCase** pattern:

### GLB Files (3D Models)
```
GamerBee.glb
InventorBee.glb
LumberjackBee.glb
NurseBee.glb
PlumberBee.glb
TechnoBee.glb
UmpireBee.glb
XrayBee.glb
YetiBee.glb
```

### PNG Thumbnails (Note the `!` before `.png`)
```
GamerBee!.png
InventorBee!.png
LumberjackBee!.png
NurseBee!.png
PlumberBee!.png
TechnoBee!.png
UmpireBee!.png
XrayBee!.png
YetiBee!.png
```

---

## Files Already Updated

✅ **avatar_catalog.py** - Lines 543-695
- All 9 avatars added with correct IDs, product_ids, obj_files, and names
- Thumbnail mappings added (lines 999-1021)

✅ **generate_avatar_cards_simple.py**
- App Store metadata keys: GamerBee, InventorBee, LumberjackBee, NurseBee, PlumberBee, TechnoBee, UmpireBee, XrayBee, YetiBee

✅ **Verified by verify_alphabet_order.py**
- All 39 avatars display in correct alphabetical order
- All 26 letters A-Z covered

---

## Quick Checklist

When adding the GLB files, verify:

- [ ] File is named **exactly** as shown above (case-sensitive)
- [ ] File is placed in `/static/assets/avatars/glb_files/`
- [ ] Corresponding PNG thumbnail exists in `/static/assets/avatars/glb_files/AvatarThumbnails/`
- [ ] PNG filename has `!` before `.png` extension

---

## No Further Changes Needed

All naming is consistent across:
- ✅ Database catalog entries
- ✅ Product IDs for Apple IAP
- ✅ Display names (with "Avatar" suffix for Apple compliance)
- ✅ GLB filenames
- ✅ PNG thumbnail mappings
- ✅ App Store card generator keys

Just add the 9 GLB files and you're ready to test! 🎉
