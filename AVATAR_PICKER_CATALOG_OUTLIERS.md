# 🐝 Avatar Picker vs Sales Catalog - Name Consistency Report

**Date:** November 13, 2025  
**Status:** ⚠️ **13 Outliers Found**

---

## Summary

- **Total avatars in catalog:** 26
- **Total GLB files found:** 23
- **GLB files in catalog:** 10
- **GLB files missing from catalog:** 13
- **OBJ avatars in catalog:** 22

---

## ⚠️ **Outliers: GLB Avatars Missing from Catalog**

The following 13 avatars are present as GLB files and **show up in the picker**, but are **NOT in the sales catalog**. This means:
- ❌ They have no pricing configuration
- ❌ They have no tier assignment (free/earn_or_buy/premium)
- ❌ They have no unlock requirements
- ❌ Their names are auto-generated from filenames (not standardized with "Avatar" suffix)

### Missing GLB Avatars

| # | Slug | GLB Filename | Picker Display Name | Recommended Catalog Name |
|---|------|--------------|---------------------|--------------------------|
| 1 | `bee-knight` | `BeeKnight.glb` | Bee Knight | **Bee Knight Avatar** |
| 2 | `buda-bee` | `BudaBee.glb` | Buda Bee | **Buda Bee Avatar** |
| 3 | `cutie-bee` | `CutieBee.glb` | Cutie Bee | **Cutie Bee Avatar** |
| 4 | `doc-bee` | `DocBee.glb` | Doc Bee | **Doc Bee Avatar** |
| 5 | `frankenbee` | `Frankenbee.glb` | Frankenbee | **Frankenbee Avatar** |
| 6 | `honey-comb` | `HoneyComb.glb` | Honey Comb | **Honey Comb Avatar** |
| 7 | `j-rock-bee` | `JRockBee.glb` | J Rock Bee | **J Rock Bee Avatar** |
| 8 | `motor-bee` | `MotorBee.glb` | Motor Bee | **Motor Bee Avatar** |
| 9 | `o-bee` | `OBee.glb` | O Bee | **O Bee Avatar** |
| 10 | `sea-bee` | `SeaBee.glb` | Sea Bee | **Sea Bee Avatar** |
| 11 | `singer-bee` | `SingerBee.glb` | Singer Bee | **Singer Bee Avatar** |
| 12 | `space-bee` | `SpaceBee.glb` | Space Bee | **Space Bee Avatar** |
| 13 | `super-bee` | `SuperBee.glb` | Super Bee | **Super Bee Avatar** |

---

## ✅ **Properly Configured GLB Avatars**

These 10 GLB avatars are correctly listed in both the picker and catalog:

| # | Slug | Catalog Name | Status |
|---|------|--------------|--------|
| 1 | `brother-bee` | Brother Bee Avatar | ✅ Match |
| 2 | `builder-bee` | Builder Bee Avatar | ✅ Match |
| 3 | `buzz-bee` | Buzz Bee Avatar | ✅ Match |
| 4 | `cool-bee` | Cool Bee Avatar | ✅ Match |
| 5 | `detective-bee` | Detective Bee Avatar | ✅ Match |
| 6 | `diva-bee` | Diva Bee Avatar | ✅ Match |
| 7 | `explorer-bee` | Explorer Bee Avatar | ✅ Match |
| 8 | `queen-bee` | Queen Bee Avatar | ✅ Match |
| 9 | `robo-bee` | Robo Bee Avatar | ✅ Match |
| 10 | `selfie-bee` | Selfie Bee Avatar | ✅ Match |

---

## 📋 **Special Cases & Notes**

### Duplicate/Overlapping Avatars

Some catalog entries may be duplicates of GLB files:

1. **Knight Bee**
   - Catalog has: `knight-bee` → `Knight Bee Avatar` (folder: `glb_files`, file: `BeeKnight.glb`)
   - GLB file: `BeeKnight.glb` → generates slug `bee-knight`
   - **Issue:** Slug mismatch (`knight-bee` vs `bee-knight`)

2. **Astro/Space Bee**
   - Catalog has: `astro-bee` → `Astro Bee Avatar` (folder: `glb_files`, file: `SpaceBee.glb`)
   - GLB file: `SpaceBee.glb` → generates slug `space-bee`
   - **Issue:** Slug mismatch (`astro-bee` vs `space-bee`)

3. **Seabea vs SeaBee**
   - Catalog has: `seabea` → `Seabea Avatar` (folder: `seabea`, OBJ files)
   - GLB file: `SeaBee.glb` → generates slug `sea-bee`
   - **Issue:** Different formats (OBJ vs GLB)

4. **Superbee vs SuperBee**
   - Catalog has: `superbee` → `Superbee Avatar` (folder: `superbeehero`, OBJ files)
   - GLB file: `SuperBee.glb` → generates slug `super-bee`
   - **Issue:** Different formats (OBJ vs GLB)

---

## 🔧 **Recommendations**

### Option 1: Add Missing Avatars to Catalog (Recommended)

Add the 13 missing GLB avatars to `avatar_catalog.py` with proper:
- ID (slug)
- Name (with "Avatar" suffix for Apple compliance)
- Description
- Category
- Tier (default_free, earn_or_buy, or premium)
- Pricing
- Unlock requirements

### Option 2: Remove Unused GLB Files

If these avatars are not meant to be used, remove the GLB files from:
```
/static/assets/avatars/glb_files/
```

### Option 3: Resolve Slug Conflicts

For avatars with slug mismatches:
- **Knight Bee:** Update catalog `id` from `knight-bee` to `bee-knight` OR rename file
- **Astro/Space Bee:** Decide on one name and update catalog accordingly
- **SeaBee:** Choose GLB or OBJ version, remove the other
- **SuperBee:** Choose GLB or OBJ version, remove the other

---

## 🎯 **Next Steps**

1. **Review the 13 missing avatars** and decide which should be:
   - Added to catalog (for sale/unlock)
   - Kept as free avatars
   - Removed entirely

2. **Fix slug conflicts** for Knight Bee, Astro/Space Bee, SeaBee, SuperBee

3. **Ensure all catalog names** end with " Avatar" for Apple App Store compliance

4. **Re-run the comparison** after updates to verify consistency

---

## 📊 **Current State**

```
✅ OBJ Avatars: 22/22 properly configured in catalog
⚠️ GLB Avatars: 10/23 properly configured in catalog
❌ Missing: 13 GLB avatars not in catalog
```

---

**Generated by:** `compare_picker_catalog_names.py`
