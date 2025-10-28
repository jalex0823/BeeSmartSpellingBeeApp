# Quick Start Guide - Avatar Cleanup

## Step 1: Backup (Optional but Recommended)
```powershell
# Create a backup of current state
git add .
git commit -m "Backup before avatar cleanup"
```

## Step 2: Run Database Cleanup
```powershell
# This removes broken avatars from database and resets affected users
python cleanup_broken_avatars.py
```
When prompted, type: `yes`

Expected output:
- Shows broken avatars found in database
- Shows users affected
- Resets users to 'al-bee'
- Removes broken avatars
- Confirms 9 working avatars remain

## Step 3: Delete Broken Avatar Folders
```powershell
# This removes the actual folder files
.\delete_broken_avatar_folders.ps1
```

This will delete:
- bee-diva/
- doctor-bee/

And keep only:
- al-bee/
- anxious-bee/
- mascot-bee/
- monster-bee/
- professor-bee/
- rocker-bee/
- vamp-bee/
- ware-bee/
- zom-bee/

## Step 4: Test the Application
```powershell
# Start the Flask app
python AjaSpellBApp.py
```

Visit: http://localhost:5000

Test:
1. ✅ Avatar picker shows only 9 avatars
2. ✅ Each avatar renders correctly (no white blobs)
3. ✅ Avatar selection persists
4. ✅ No console errors about missing files

## Step 5: Commit Changes
```powershell
git add .
git commit -m "Remove non-working avatars, keep 9 working OBJ-based avatars"
git push
```

## Troubleshooting

### If avatars still show white blobs:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Check browser console for 404 errors
3. Verify OBJ/MTL/texture files exist in avatar folders

### If database issues occur:
```powershell
# Re-run migration to repopulate
python migrate_avatars_to_db.py
```

### If users can't see their avatars:
- Check that default avatar is set to 'al-bee'
- Verify user.avatar_id matches one of the 9 working avatars
- Run cleanup script again to reset affected users

## Files Modified
- avatar_catalog.py ✅
- avatar_migration_tool.py ✅
- templates/unified_menu.html ✅ (partial)
- cleanup_broken_avatars.py ✅ (new)
- delete_broken_avatar_folders.ps1 ✅ (new)
- AVATAR_CLEANUP_SUMMARY.md ✅ (new)

## What This Does
✅ Removes 14+ broken avatars that rendered as white blobs
✅ Keeps 9 working OBJ-based avatars
✅ Resets affected users to default avatar
✅ Updates catalog and theme configuration
✅ Cleans up filesystem and database

## Success Criteria
- [ ] Database contains exactly 9 avatars
- [ ] No users have broken avatar IDs
- [ ] Filesystem has 9 avatar folders
- [ ] Avatar picker shows 9 options
- [ ] All avatars render correctly (no white blobs)
- [ ] No 404 errors in browser console
