# Avatar Picker Apple Store Compliance - Complete

## Summary
Fixed avatar names to comply with Apple App Store naming requirements (all must end with " Avatar" suffix).

## What Was Done

### 1. Cleaned Up Catalog (avatar_catalog.py)
- **Removed 9 duplicate/prototype avatars** from catalog
  - Duplicates: bee-knight, doc-bee, sea-bee, astro-bee, honey-comb, cutie-bee, buda-bee, frankenbee, j-rock-bee
- **Fixed tier assignments** to match official spec:
  - default_free: 5 avatars
  - mascot: 1 avatar
  - earn_or_buy: 11 avatars
  - premium: 13 avatars
  - **Total: 30 avatars**
- **All names now have " Avatar" suffix** (Apple compliance)

### 2. Cleaned Up Filesystem (static/assets/avatars/glb_files/)
- **Removed 11 GLB files** that weren't in the catalog:
  - BudaBee.glb, CutieBee.glb, Frankenbee.glb, HoneyComb.glb, JRockBee.glb
  - BuzzBee.glb, DivaBee.glb, DocBee.glb, ExplorerBee.glb, SeaBee.glb, SelfieBee.glb
- **Kept 12 official GLB files** (backed up removed ones to `glb_files_backup/`)

### 3. Updated API (/api/avatars)
- Modified `AjaSpellBApp.py` to use **catalog names for GLB avatars**
- Instead of auto-generating names from filenames, API now uses catalog entry names
- Ensures Apple Store compliant names with " Avatar" suffix

### 4. Created Admin Sync Endpoint
- **New endpoint**: `POST /admin/sync-avatar-names`
- Updates Railway database avatar names to match catalog
- Admin-only access required

## Deployment Steps

### After Deploying to Railway:

1. **Update Railway URL** in `sync_railway_avatars.py`:
   ```python
   BASE_URL = "https://beesmart-spelling-app.railway.app"  # Your Railway URL
   ```

2. **Run the sync script**:
   ```bash
   python3 sync_railway_avatars.py bigdaddy your_password
   ```
   
   This will:
   - Login as admin
   - Update all DB avatar names to match catalog (add " Avatar" suffix)
   - Show which avatars were updated

3. **Verify** by visiting your app and checking the avatar picker shows all 30 avatars with correct names

## File Structure

```
avatar_catalog.py              # 30 official avatars with Apple-compliant names
AjaSpellBApp.py                # API updated to use catalog names
sync_railway_avatars.py        # Script to sync Railway DB (run after deploy)
cleanup_glb_files.py           # One-time cleanup (already run)
static/assets/avatars/
  ├── glb_files/              # 12 GLB avatars (cleaned)
  └── glb_files_backup/       # 11 removed GLBs (backup)
```

## Expected Result

After deployment and sync:
- ✅ **30 total avatars** in picker
- ✅ **All names end with " Avatar"** (Apple Store compliant)
- ✅ **Correct tier distribution**: 6 free, 11 standard, 13 premium
- ✅ **No duplicates**

## Technical Details

### Avatar Sources
1. **Database** (Railway): 9 OBJ avatars (will be updated by sync script)
2. **Filesystem**: 12 GLB avatars (already cleaned up)
3. **Catalog** (avatar_catalog.py): 30 entries total (mix of DB and GLB avatars, plus future ones)

### Why Two Steps?
- **Catalog cleanup** (done): Defines the official 30 avatars
- **Database sync** (after deploy): Updates Railway DB to match catalog names
  
### Notes
- The sync endpoint is idempotent - safe to run multiple times
- Removed GLB files are backed up in `glb_files_backup/` (not deployed)
- Local database doesn't matter - Railway DB is the source of truth
