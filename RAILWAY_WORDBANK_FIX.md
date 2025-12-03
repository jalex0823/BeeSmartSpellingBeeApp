# Railway Wordbank Persistence Fix - Deployment Guide

## Problem Fixed ✅
- **Issue**: Words upload successfully locally but disappear on Railway
- **Root Cause**: Railway uses ephemeral filesystem - files in `data/wordbanks/` get deleted on container restart
- **Impact**: Users lose their wordbanks after Railway restarts/redeploys

## Solution Implemented
Moved wordbank storage from filesystem to PostgreSQL database for Railway persistence.

## How It Works

### Old System (Broken on Railway)
```
Upload → Session (storage_id) → WORD_STORAGE (in-memory) → data/wordbanks/*.json (disk)
                                        ↓
                                    DELETED on restart
```

### New System (Railway-Safe)
```
Upload → Session (storage_id) → WORD_STORAGE (in-memory) → PostgreSQL wordbank_storage table
                                        ↓
                                    Survives restarts!
```

## Deployment Steps

### 1. Deploy Code (Already Done)
The code has been pushed to GitHub and will auto-deploy to Railway.

### 2. Create Database Table in Railway PostgreSQL
**IMPORTANT:** Run this in **RAILWAY**, not locally!

1. Go to Railway Dashboard → Your Project → Click on your service
2. Click "Shell" or "Terminal" tab
3. Run this command:

```bash
python railway_add_wordbank_table.py
```

**What this does:**
- Connects to Railway's PostgreSQL database (uses DATABASE_URL automatically)
- Creates the `wordbank_storage` table
- Shows you the schema and confirms creation
- Verifies the table exists

This creates the `wordbank_storage` table with these columns:
- `id` (primary key)
- `storage_id` (UUID, indexed)
- `words_data` (JSON array of word objects)
- `word_count` (integer)
- `created_at`, `updated_at`, `last_accessed` (timestamps)
- `user_id` (optional FK to users table)

### 3. Verify
After running the migration:
1. Upload a word list
2. Check Railway logs for: `✅ Saved X words to database for storage_id=...`
3. Restart the Railway app
4. Verify words are still there (they'll load from database)

## Migration
- **Automatic**: Old disk-based wordbanks will automatically migrate to database on first load
- **Backward Compatible**: Local development still uses disk storage as fallback
- **Zero Downtime**: Works with existing sessions

## Technical Details

### Database Model
```python
class WordBankStorage(db.Model):
    storage_id = UUID (unique index)
    words_data = JSON array
    word_count = int
    user_id = optional FK
```

### Updated Functions
- `_save_wordbank_to_disk()` → Saves to PostgreSQL + disk fallback
- `_load_wordbank_from_disk()` → Loads from PostgreSQL, migrates legacy disk files
- `_delete_wordbank_from_disk()` → Deletes from both PostgreSQL and disk

### Persistence Chain
1. **Session**: Stores `storage_id` (UUID pointer) + lightweight metadata
2. **WORD_STORAGE**: In-memory dict for fast access during active session
3. **PostgreSQL**: Permanent storage survives restarts/redeploys
4. **Disk** (legacy): Local dev fallback only

## Why This Fixes Railway
- ✅ PostgreSQL data persists across container restarts
- ✅ Works with Railway's multi-instance deployments
- ✅ No reliance on ephemeral filesystem
- ✅ Automatic migration from old system
- ✅ Works for both authenticated and guest users

## Testing
1. Upload words on Railway
2. Check logs: Should see database save messages
3. Restart Railway service
4. Navigate to quiz - words should still be there!
