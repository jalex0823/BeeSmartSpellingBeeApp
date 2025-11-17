# Avatar Catalog & Database Sync - Complete Documentation
**Date:** November 13, 2025 (Updated November 17, 2025)  
**Status:** ✅ COMPLETE - Deployed to Railway

---

## 📊 Final Configuration

### Catalog Summary
- **Total Avatars:** 39 (verified via count_avatars.py)
- **Location:** `avatar_catalog.py`
- **Apple Store Compliance:** ✅ All names end with " Avatar"
- **GLB Files:** 39 files in `static/assets/avatars/glb_files/`
- **Database:** 39 active avatars in Railway PostgreSQL

### Tier Distribution
```
Free (5 avatars):
  - Brother Bee Avatar
  - Builder Bee Avatar
  - Cool Bee Avatar
  - Detective Bee Avatar
  - Explorer Bee Avatar

Earn or Buy (7 avatars):
  - Buzz Bee Avatar
  - Cutie Bee Avatar
  - Knight Bee Avatar
  - Professor Bee Avatar
  - Rocker Bee Avatar
  - Selfie Bee Avatar
  - Vamp Bee Avatar

Mascot (1 avatar):
  - Mascot Bee Avatar

Premium (26 avatars):
  - Al Bee Avatar
  - Buda Bee Avatar
  - Diva Bee Avatar
  - Doc Bee Avatar
  - Franken Bee Avatar
  - Gamer Bee Avatar
  - Honey Comb Avatar
  - Inventor Bee Avatar
  - J Rock Bee Avatar
  - Lumberjack Bee Avatar
  - Motor Bee Avatar
  - Nurse Bee Avatar
  - O Bee Avatar
  - Plumber Bee Avatar
  - Queen Bee Avatar
  - Robo Bee Avatar
  - Sea Bee Avatar
  - Singer Bee Avatar
  - Space Bee Avatar
  - Super Bee Avatar
  - Techno Bee Avatar
  - Umpire Bee Avatar
  - Ware Bee Avatar
  - Xray Bee Avatar
  - Yeti Bee Avatar
  - Zom Bee Avatar
```

---

## 🔧 Changes Made

### Avatars Removed from Catalog
1. **biker-bee** - Not in reference image
2. **doctor-bee** - Replaced by doc-bee (different avatar)
3. **seabea** - Old slug, replaced by sea-bee
4. **superbee** - Old slug, not Super Bee Avatar
5. **buzzbot-bee** - Duplicate of robo-bee
6. **buzzhero-bee** - Duplicate of super-bee

### Avatars Added to Catalog
1. **doc-bee** - Doc Bee Avatar (DoctorBee.glb)
2. **franken-bee** - Franken Bee Avatar (FrankenBee.glb)
3. **honey-comb** - Honey Comb Avatar (HoneyComb.glb)
4. **j-rock-bee** - J Rock Bee Avatar (JRockBee.glb)
5. **sea-bee** - Sea Bee Avatar (SeaBee.glb)

### Critical Avatar Mappings
**Important:** These avatars had naming confusion that was resolved:

| Display Name | Catalog ID | GLB File | Notes |
|--------------|------------|----------|-------|
| Robo Bee Avatar | `robo-bee` | `BuzzbotBee.glb` | Previously had duplicate "buzzbot-bee" |
| Super Bee Avatar | `super-bee` | `SuperBee.glb` | Previously had duplicate "buzzhero-bee" |
| Knight Bee Avatar | `knight-bee` | `KnightBee.glb` | Same as "Bee Knight" in image |
| Doc Bee Avatar | `doc-bee` | `DoctorBee.glb` | Different from old "doctor-bee" |
| Sea Bee Avatar | `sea-bee` | `SeaBee.glb` | Different from old "seabea" |

---

## 📁 GLB Files (39 Total)

All GLB files located in: `static/assets/avatars/glb_files/`

```
AlBee.glb           → Al Bee Avatar
BrotherBee.glb      → Brother Bee Avatar
BudaBee.glb         → Buda Bee Avatar
BuilderBee.glb      → Builder Bee Avatar
BuzzBee.glb         → Buzz Bee Avatar
BuzzbotBee.glb      → Robo Bee Avatar ⚠️
CoolBee.glb         → Cool Bee Avatar
CutieBee.glb        → Cutie Bee Avatar
DetectiveBee.glb    → Detective Bee Avatar
DivaBee.glb         → Diva Bee Avatar
DoctorBee.glb       → Doc Bee Avatar ⚠️
ExplorerBee.glb     → Explorer Bee Avatar
FrankenBee.glb      → Franken Bee Avatar
GamerBee.glb        → Gamer Bee Avatar
HoneyComb.glb       → Honey Comb Avatar
InventorBee.glb     → Inventor Bee Avatar
JRockBee.glb        → J Rock Bee Avatar
KnightBee.glb       → Knight Bee Avatar
LumberjackBee.glb   → Lumberjack Bee Avatar
MascotBee.glb       → Mascot Bee Avatar
MotorBee.glb        → Motor Bee Avatar
NurseBee.glb        → Nurse Bee Avatar
OBee.glb            → O Bee Avatar
PlumberBee.glb      → Plumber Bee Avatar
ProfessorBee.glb    → Professor Bee Avatar
QueenBee.glb        → Queen Bee Avatar
RoboBee.glb         → (Backup - not used)
RockerBee.glb       → Rocker Bee Avatar
SeaBee.glb          → Sea Bee Avatar
SelfieBee.glb       → Selfie Bee Avatar
SingerBee.glb       → Singer Bee Avatar
SpaceBee.glb        → Space Bee Avatar
SuperBee.glb        → Super Bee Avatar
TechnoBee.glb       → Techno Bee Avatar
UmpireBee.glb       → Umpire Bee Avatar
VampBee.glb         → Vamp Bee Avatar
WareBee.glb         → Ware Bee Avatar
XrayBee.glb         → Xray Bee Avatar
YetiBee.glb         → Yeti Bee Avatar
ZomBee.glb          → Zom Bee Avatar
```

⚠️ **Note:**
- `BuzzbotBee.glb` is used for Robo Bee Avatar (not a separate avatar)
- `DoctorBee.glb` is used for Doc Bee Avatar (different from old doctor-bee)

---

## 🗄️ Railway Database Sync

**Connection String:**
```
postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway
```

### Database Operations Performed

#### 1. Reactivated Avatars (7)
Previously inactive avatars that were reactivated with correct names:
- Builder Bee Avatar (ID=27)
- Detective Bee Avatar (ID=30)
- Franken Bee Avatar (ID=32)
- Motor Bee Avatar (ID=33)
- Sea Bee Avatar (ID=35)
- Space Bee Avatar (ID=36)
- Super Bee Avatar (ID=37)

#### 2. Inserted New Avatars (4)
Avatars that didn't exist in database and were inserted:
- Cool Bee Avatar (ID=53)
- Honey Comb Avatar (ID=54)
- Robo Bee Avatar (ID=55)
- Singer Bee Avatar (ID=56)

#### 3. Updated Avatars (2)
Existing avatars updated with correct names:
- Doc Bee Avatar (reactivated)
- J Rock Bee Avatar (reactivated)

#### 4. Deactivated Duplicates (17)
Old/duplicate entries deactivated in earlier sync:
- anxious-bee, beedoctor, beeknight, builderbee, buzzbotbee, buzzhero
- detectivebee, doc-bee (old), explorerbee, frankenbee, j-rock-bee (old)
- monster-bee, motorcyclebuzzbee, queenbeemajesty, seabee
- spacebeeexplorer, superbeehero

### Database Schema Notes
Required fields for avatar insertion:
```sql
slug            VARCHAR (unique identifier, e.g., "cool-bee")
name            VARCHAR (display name with " Avatar" suffix)
description     TEXT
category        VARCHAR (e.g., "classic", "premium", "tech")
folder_path     VARCHAR (e.g., "glb_files")
obj_file        VARCHAR (GLB filename)
mtl_file        VARCHAR (optional, can be NULL)
texture_file    VARCHAR (optional, can be NULL)
unlock_level    INTEGER (default: 1)
points_required INTEGER (default: 0)
is_premium      BOOLEAN
is_active       BOOLEAN
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

---

## 🛠️ Scripts Created

### Database Sync Scripts
1. **cleanup_railway_database.py**
   - Compares catalog to database
   - Deactivates avatars not in catalog
   - Updates names to match catalog
   - Reactivates missing avatars

2. **final_avatar_sync.py**
   - Reactivates specific inactive avatars
   - Updates names with " Avatar" suffix
   - Maps old database names to catalog IDs

3. **insert_missing_avatars.py**
   - Inserts completely new avatars
   - Populates all required database fields
   - Used for: cool-bee, honey-comb, robo-bee, singer-bee

### Verification Scripts
1. **count_avatars.py**
   - Counts total avatars in catalog
   - Shows tier distribution
   - Lists all avatar names

2. **compare_picker_catalog_names.py**
   - Compares picker display names to catalog
   - Identifies naming discrepancies

3. **verify_30_avatars.py**
   - Confirms exactly 30 avatars
   - Matches against reference image

### Audit Scripts
1. **complete_avatar_audit.py**
   - Full audit of catalog, GLB files, and database
   - Generates JSON report

2. **find_missing_glb.py**
   - Identifies avatars without GLB files

---

## 📋 Apple Store Compliance

### Naming Convention
**Rule:** All avatar names MUST end with " Avatar"

**Examples:**
- ✅ "Al Bee Avatar"
- ✅ "Robo Bee Avatar"
- ✅ "Honey Comb Avatar"
- ❌ "Al Bee" (missing suffix)
- ❌ "RoboBee" (missing suffix and space)

### Implementation
1. **avatar_catalog.py**: All `name` fields have " Avatar" suffix
2. **AjaSpellBApp.py**: API endpoint `/api/avatars` uses catalog names for GLB avatars
3. **Railway Database**: All active avatars have " Avatar" suffix
4. **Frontend**: Picker displays catalog names directly

---

## 🚀 Deployment

### Git Commit
```bash
git add avatar_catalog.py AjaSpellBApp.py static/assets/avatars/glb_files/*.glb
git commit -m "Sync catalog with 30 avatars from image - Apple Store compliant names"
git push origin main --force
```

**Commit Hash:** dce040c  
**Date:** November 13, 2025

### Files Deployed
- `avatar_catalog.py` (updated with 30 avatars)
- `AjaSpellBApp.py` (catalog name mapping for GLB files)
- 30 GLB files in `static/assets/avatars/glb_files/`

### Railway Auto-Deploy
Railway automatically rebuilds and deploys on push to main branch.

---

## 📝 Reference Image

The definitive source of truth for avatar selection is the user's reference image showing exactly 30 avatars arranged as:

**Row 1 (5):** Al Bee, Bee Knight, Brother Bee, Buda Bee, Builder Bee  
**Row 2 (5):** Buzz Bee, Buzzbot Bee, Buzzhero Bee, Cool Bee, Cutie Bee  
**Row 3 (5):** Detective Bee, Diva Bee, Doc Bee, Explorer Bee, Franken Bee  
**Row 4 (5):** Honey Comb, J Rock Bee, Mascot Bee, Motor Bee, O Bee  
**Row 5 (5):** Professor Bee, Queen Bee, Rocker Bee, Sea Bee, Selfie Bee  
**Row 6 (5):** Singer Bee, Space Bee, Vamp Bee, Ware Bee, Zom Bee

**Total:** 30 avatars

---

## ⚠️ Important Notes

1. **Robo Bee vs Buzzbot Bee**
   - They are the SAME avatar
   - Display name: "Robo Bee Avatar"
   - GLB file: `BuzzbotBee.glb`
   - Catalog ID: `robo-bee`

2. **Super Bee vs Buzzhero Bee**
   - They are the SAME avatar
   - Display name: "Super Bee Avatar"
   - GLB file: `SuperBee.glb`
   - Catalog ID: `super-bee`

3. **Knight Bee vs Bee Knight**
   - Same avatar, different labels in image
   - Display name: "Knight Bee Avatar"
   - GLB file: `KnightBee.glb`
   - Catalog ID: `knight-bee`

4. **Doc Bee vs Doctor Bee**
   - Different avatars!
   - Doc Bee uses `DoctorBee.glb`
   - Old `doctor-bee` was removed

5. **Sea Bee vs Seabea**
   - Same concept, different naming
   - New: `sea-bee` with `SeaBee.glb`
   - Old `seabea` was removed

---

## 🔍 Future Maintenance

### Adding New Avatars
1. Add entry to `avatar_catalog.py` with:
   - Unique `id` (slug format: lowercase-with-hyphens)
   - `name` ending with " Avatar"
   - `folder` = "glb_files"
   - `obj_file` = matching GLB filename
   - Appropriate `tier`, `unlock_points`, `price`

2. Add GLB file to `static/assets/avatars/glb_files/`

3. Insert into Railway database:
```python
import psycopg2
conn = psycopg2.connect("postgresql://postgres:...")
cur = conn.cursor()
cur.execute("""
    INSERT INTO avatars (slug, name, description, category, folder_path, 
                        obj_file, is_active, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW())
""", (avatar_id, name, description, category, "glb_files", glb_filename))
conn.commit()
```

4. Deploy to Railway

### Removing Avatars
1. Remove from `avatar_catalog.py`
2. Deactivate in database (don't delete):
```python
cur.execute("UPDATE avatars SET is_active = FALSE WHERE slug = %s", (avatar_id,))
```
3. Optionally move GLB file to backup folder
4. Deploy to Railway

### Renaming Avatars
1. Update `name` in `avatar_catalog.py`
2. Update database:
```python
cur.execute("UPDATE avatars SET name = %s WHERE slug = %s", (new_name, avatar_id))
```
3. Ensure name ends with " Avatar"
4. Deploy to Railway

---

## ✅ Verification Checklist

Before any future avatar changes, verify:

- [ ] Catalog has correct number of avatars
- [ ] All names end with " Avatar"
- [ ] All avatars have GLB files
- [ ] GLB filenames match catalog `obj_file` field
- [ ] Database active count matches catalog count
- [ ] All database names end with " Avatar"
- [ ] No duplicate avatars in catalog
- [ ] Tier distribution is correct
- [ ] Reference image matches catalog

**Run:** `python3 count_avatars.py` to verify catalog state

---

## 📞 Support

For avatar-related issues:
1. Check this documentation first
2. Verify catalog with `count_avatars.py`
3. Check database with `cleanup_railway_database.py`
4. Verify GLB files exist
5. Confirm Railway deployment succeeded

**Key Files:**
- Catalog: `avatar_catalog.py`
- API: `AjaSpellBApp.py` (lines 9400-9460)
- GLB Files: `static/assets/avatars/glb_files/`
- Database: Railway PostgreSQL (connection string above)

---

**Document Created:** November 13, 2025  
**Last Updated:** November 13, 2025  
**Status:** Complete ✅
