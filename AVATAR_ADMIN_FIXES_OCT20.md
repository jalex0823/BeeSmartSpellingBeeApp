# Avatar System & Admin Dashboard Fixes

## Date: October 20, 2025

## Issues Resolved

### 1. Admin Dashboard 500 Error - `User.honey_points` Attribute Missing

**Problem:**
- Admin dashboard was querying `User.honey_points`, `User.total_battles_won`, and `User.total_battles_played`
- These fields don't exist in the User model
- Caused AttributeError and 500 Internal Server Error

**Solution:**
- Replaced all queries to use existing fields: `total_lifetime_points` and `total_quizzes_completed`
- Added safe fallbacks using `getattr()` for battle-related stats (placeholders until Battle models implemented)
- Updated `/admin/dashboard` and `/admin/battle-bees` routes

**Code Changes (AjaSpellBApp.py):**
```python
# OLD (BROKEN):
leaderboard = User.query.order_by(
    User.honey_points.desc(),
    User.total_battles_won.desc()
)

# NEW (FIXED):
leaderboard = User.query.order_by(
    User.total_lifetime_points.desc(),
    User.total_quizzes_completed.desc()
)

# Add safe fallbacks in loop:
for player in leaderboard:
    player.honey_points = getattr(player, 'honey_points', player.total_lifetime_points)
    player.total_battles_played = getattr(player, 'total_battles_played', 0)
    player.total_battles_won = getattr(player, 'total_battles_won', 0)
```

### 2. Avatar Texture Mismatch - System-Wide Issue

**Problem:**
- Files were named generically (`model.obj`, `model.mtl`, `texture.png`) in all avatar folders
- Lost identity tracking - couldn't tell which model belonged to which avatar
- Database stored `avatar_id='cool-bee'` but folder contained Professor Bee files
- All 18 avatars affected by generic naming

**Root Cause:**
- Original files had timestamps (e.g., `Professor_Bee_1019002841_texture.obj`)
- Someone renamed to generic names losing the connection to specific avatars
- Files got mixed up between folders

**User Solution:**
- Relabeled ALL source files to match folder names:
  - `ProfessorBee/ProfessorBee.obj`
  - `ProfessorBee/ProfessorBee.mtl`
  - `ProfessorBee/ProfessorBee.png`
  - (Removed `!` characters for consistency)

**System Solution:**

#### Updated `avatar_catalog.py`:
1. Scanned actual folder structure using `scan_avatar_folders.py`
2. Updated `AVATAR_CATALOG` from 16 to 18 avatars
3. Added new fields to each avatar entry:
   ```python
   {
       "id": "professor-bee",
       "name": "Professor Bee",
       "folder": "ProfessorBee",        # NEW - Source folder name
       "obj_file": "ProfessorBee.obj",   # NEW - Actual filename
       "mtl_file": "ProfessorBee.mtl",   # NEW - Actual filename
       "texture_file": "ProfessorBee.png", # NEW - Actual filename
       "description": "...",
       "variants": ["default"],
       "category": "profession"
   }
   ```

4. Updated `get_avatar_info()` function:
   ```python
   # OLD (HARDCODED):
   'model_obj_url': f"{base_path}/model.obj"
   
   # NEW (DYNAMIC):
   obj_file = avatar.get('obj_file', 'model.obj')
   'model_obj_url': f"{base_path}/{obj_file}"  # e.g., /static/assets/avatars/professor-bee/ProfessorBee.obj
   ```

#### Copied Files with Correct Names:
- Created `copy_simple.py` script
- Copied all 18 avatars from source to deployment:
  - Source: `C:/Users/jeff/Dropbox/BeeSmartSpellingBeeApp/Avatars/3D Avatar Files/[FolderName]/`
  - Target: `static/assets/avatars/[avatar-id]/`
- Successfully copied 18 avatars (89 files total):
  - Al Bee (al-bee)
  - Anxious Bee (anxious-bee)
  - Biker Bee (biker-bee)
  - Brother Bee (brother-bee)
  - Builder Bee (builder-bee)
  - Cool Bee (cool-bee) ✅
  - Diva Bee (diva-bee)
  - Doctor Bee (doctor-bee)
  - Explorer Bee (explorer-bee)
  - Knight Bee (knight-bee)
  - Mascot Bee (mascot-bee)
  - Monster Bee (monster-bee)
  - Professor Bee (professor-bee) ✅
  - Queen Bee (queen-bee) ⚠️ Missing .mtl file
  - Robo Bee (robo-bee)
  - Rocker Bee (rocker-bee)
  - Seabea (seabea)
  - Superbee (superbee)

## Files Modified

1. **AjaSpellBApp.py** (Lines 5810-5870)
   - Fixed `/admin/dashboard` route
   - Fixed `/admin/battle-bees` route
   - Replaced `User.honey_points` with `User.total_lifetime_points`
   - Added safe `getattr()` fallbacks

2. **avatar_catalog.py**
   - Updated AVATAR_CATALOG from 16 to 18 entries
   - Added `folder`, `obj_file`, `mtl_file`, `texture_file` fields
   - Updated `get_avatar_info()` to use specific filenames
   - Removed duplicate entries

3. **static/assets/avatars/** (18 folders)
   - Copied all avatar files with proper names
   - Each folder now contains:
     - `{FolderName}.obj` (3D model geometry)
     - `{FolderName}.mtl` (material definition)
     - `{FolderName}.png` (texture image)
     - `thumbnail.png` (preview thumbnail)
     - `preview.png` (higher quality preview)

## Scripts Created

1. **scan_avatar_folders.py** - Scans source directory and generates catalog mappings
2. **copy_avatar_files.py** - Full-featured copy script (had emoji encoding issues)
3. **copy_simple.py** - Simplified copy script (SUCCESSFUL)
4. **copy_avatars.ps1** - PowerShell version (had syntax issues)

## Testing Required

### Admin Dashboard:
1. Navigate to `/admin/dashboard`
2. Verify page loads without 500 error
3. Check leaderboard displays correctly
4. Verify stats show total_lifetime_points as honey_points

### Avatar Loading:
1. Login as BigDaddy2 (currently has avatar_id='cool-bee')
2. Check browser console for avatar loading logs (🎨🔍 emojis)
3. Verify URLs show: `/static/assets/avatars/cool-bee/CoolBee.obj`
4. Confirm Cool Bee texture loads correctly (not Professor Bee)
5. Test avatar selection UI - all 18 avatars should be available
6. Select different avatars and verify correct models/textures load

## Known Issues

1. **Queen Bee Missing MTL File:**
   - QueenBee.mtl not found in source directory
   - May cause material rendering issues
   - Need to investigate source files

2. **Battle Models Not Implemented:**
   - `honey_points`, `total_battles_won`, `total_battles_played` are placeholders
   - Will need proper Battle model implementation
   - Consider adding these fields to User model OR creating separate HoneyTransaction/Battle models

## Future Enhancements

### Option A: Add Battle Fields to User Model
```python
# migrations/versions/add_battle_fields.py
def upgrade():
    op.add_column('users', sa.Column('honey_points', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('total_battles_played', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('total_battles_won', sa.Integer(), nullable=False, server_default='0'))
```

### Option B: Create Transaction-Based System
```python
class HoneyTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    delta = db.Column(db.Integer)  # +/- honey points
    source = db.Column(db.String(50))  # 'quiz', 'battle', 'achievement'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Query with computed totals:
leaders = db.session.query(
    User,
    func.coalesce(func.sum(HoneyTransaction.delta), 0).label('honey_points')
).outerjoin(HoneyTransaction).group_by(User.id).order_by(...)
```

## Deployment Checklist

- [x] Update avatar_catalog.py
- [x] Copy avatar files to static/assets/avatars/
- [ ] Test admin dashboard (no 500 error)
- [ ] Test avatar loading (correct textures)
- [ ] Deploy to Railway
- [ ] Clear browser cache
- [ ] Verify on production

## Git Commit

```bash
git add avatar_catalog.py AjaSpellBApp.py static/assets/avatars/
git commit -m "Fix admin dashboard 500 error & avatar texture system

- Replace User.honey_points queries with total_lifetime_points
- Add safe fallbacks for battle stats (placeholders)
- Update avatar catalog with 18 avatars and specific filenames
- Copy all avatar files with proper naming (AlBee.obj, CoolBee.obj, etc.)
- Fix avatar URL generation to use actual filenames vs hardcoded model.obj
- Resolves texture mismatch issue affecting all 18 avatars"
```
