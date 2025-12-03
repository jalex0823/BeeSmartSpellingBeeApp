# 🔧 Wordbank Single Source of Truth Fix

## Problem Identified
The app has **THREE** storage locations for words, causing confusion and bugs:

1. **WORD_STORAGE** (in-memory dict) - ephemeral, lost on restart
2. **Disk files** (WORDBANK_DIR/*.json) - ephemeral on Railway (filesystem resets)
3. **Railway PostgreSQL** (`wordbank_storage` table) - persistent, but **NEVER QUERIED**

## Root Cause
- `get_wordbank()` reads from WORD_STORAGE → disk → legacy session
- **NEVER queries the Railway database**
- `wordbank_storage` table has 5 wordbanks with 22 words but code ignores it
- No database model (class WordBankStorage) exists in AjaSpellBApp.py
- Session `wordbank_storage_id` is a UUID pointer that points to nothing

## Solution: Railway Database as ONLY Storage
Make `wordbank_storage` table the single source of truth for ALL word operations:

### Step 1: Create Database Model
```python
class WordBankStorage(db.Model):
    __tablename__ = 'wordbank_storage'
    
    storage_id = db.Column(db.String(36), primary_key=True)  # UUID
    words_data = db.Column(db.JSON, nullable=False)  # List of {word, sentence, hint}
    word_count = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='wordbanks')
```

### Step 2: Rewrite get_wordbank()
```python
def get_wordbank() -> List[Dict[str, str]]:
    """Read wordbank from Railway database (ONLY source of truth)."""
    storage_id = session.get("wordbank_storage_id")
    
    if not storage_id:
        print("DEBUG get_wordbank: No storage_id in session")
        return []
    
    # Query Railway database
    wb_storage = WordBankStorage.query.filter_by(storage_id=storage_id).first()
    
    if not wb_storage:
        print(f"⚠️ WARNING: storage_id={storage_id} not found in database")
        return []
    
    words = wb_storage.words_data or []
    print(f"✅ Loaded {len(words)} words from Railway database")
    return list(words)  # Return copy to prevent modification
```

### Step 3: Rewrite set_wordbank()
```python
def set_wordbank(rows: List[Dict[str, str]], is_user_upload: bool = False):
    """Save wordbank to Railway database (ONLY storage location)."""
    storage_id = session.get("wordbank_storage_id")
    
    if not storage_id:
        storage_id = str(uuid.uuid4())
        session["wordbank_storage_id"] = storage_id
        session.modified = True
    
    # Save to Railway database
    wb_storage = WordBankStorage.query.filter_by(storage_id=storage_id).first()
    
    if wb_storage:
        # Update existing
        wb_storage.words_data = rows
        wb_storage.word_count = len(rows)
        wb_storage.updated_at = datetime.utcnow()
    else:
        # Create new
        wb_storage = WordBankStorage(
            storage_id=storage_id,
            words_data=rows,
            word_count=len(rows),
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(wb_storage)
    
    db.session.commit()
    print(f"✅ Saved {len(rows)} words to Railway database")
    
    # Update session count
    session["wordbank_count"] = len(rows)
```

### Step 4: Delete Wordbank
```python
def delete_wordbank(storage_id: str):
    """Delete wordbank from Railway database."""
    wb_storage = WordBankStorage.query.filter_by(storage_id=storage_id).first()
    if wb_storage:
        db.session.delete(wb_storage)
        db.session.commit()
        print(f"✅ Deleted wordbank {storage_id} from Railway database")
```

### Step 5: Remove All References To
- `WORD_STORAGE` dictionary
- `WORD_STORAGE_LOCK` threading lock
- `save_wordbank_atomic()` disk function
- `load_wordbank_safe()` disk function
- `_wordbank_path()` disk path function
- `_load_wordbank_from_disk()` disk loader
- `_delete_wordbank_from_disk()` disk deleter
- `WORDBANK_DIR` directory

## Benefits
✅ **Single source of truth** - Railway database only
✅ **Survives restarts** - database persists across deployments
✅ **No sync issues** - memory/disk/database always consistent
✅ **Simpler code** - one storage mechanism instead of three
✅ **Accurate diagnostics** - `getCount()` shows actual database count
✅ **Guest users** - user_id NULL for unauthenticated sessions
✅ **User wordbanks** - user_id links wordbanks to accounts

## Implementation Order
1. Add WordBankStorage model to AjaSpellBApp.py
2. Rewrite get_wordbank() to query database
3. Rewrite set_wordbank() to save to database
4. Update all endpoints that delete wordbanks
5. Remove WORD_STORAGE, disk functions, and WORDBANK_DIR
6. Test upload → quiz → save → load flow
7. Verify diagnostics show correct counts

## Migration
Existing sessions with `wordbank_storage_id` will work automatically:
- If storage_id exists in database → load words
- If storage_id missing → return empty (user uploads new words)
- No data loss for users with saved wordbanks
