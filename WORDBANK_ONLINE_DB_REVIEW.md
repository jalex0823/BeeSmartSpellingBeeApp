# 📚 BeeSmart Wordbank & Railway Database Documentation Review

## 🎯 Overview
Your application stores words/wordbanks in a **Railway PostgreSQL database** for persistence across container restarts. This document summarizes the key architecture and setup.

---

## 🏗️ Architecture: Three-Layer System

### Layer 1: Session (Ephemeral)
- **Location**: Browser cookie
- **Size**: ~36 bytes (UUID only)
- **Purpose**: Session pointer to wordbank
- **Key**: `session["wordbank_storage_id"]` = UUID string

### Layer 2: In-Memory (Fast Access)
- **Location**: Server RAM (WORD_STORAGE dict)
- **Purpose**: Quick access during active session
- **Lost on**: Server restart
- **Key**: `WORD_STORAGE[storage_id]` = list of word dicts

### Layer 3: Database (Persistent)
- **Location**: Railway PostgreSQL
- **Table**: `wordbank_storage`
- **Survives**: Container restarts, redeployments
- **Schema**:
  ```
  id              INTEGER PRIMARY KEY
  storage_id      VARCHAR(36) UNIQUE (UUID pointer from session)
  words_data      JSON (array of {word, sentence, hint})
  word_count      INTEGER (quick count)
  created_at      DATETIME
  updated_at      DATETIME
  last_accessed   DATETIME
  user_id         INTEGER FK to users table (optional)
  ```

---

## 🔄 Data Flow

### Upload Process
```
User uploads words via /api/upload
    ↓
Parse & validate words (filter kid-safety)
    ↓
Generate/get storage_id (UUID)
    ↓
Save to Database: WordBankStorage.save_wordbank(storage_id, words, user_id)
    ↓
Update Session: session["wordbank_storage_id"] = storage_id
    ↓
Load into WORD_STORAGE (in-memory)
    ↓
✅ Words ready for quiz
```

### Quiz Loading Process
```
User goes to quiz
    ↓
get_wordbank() called
    ↓
Check session for storage_id
    ↓
Load from WORD_STORAGE (if exists)
    ↓
OR load from Database: WordBankStorage.load_wordbank(storage_id)
    ↓
Populate WORD_STORAGE for current session
    ↓
✅ Quiz displays words
```

---

## 🗄️ Database Model (models.py)

```python
class WordBankStorage(db.Model):
    """Database-backed wordbank persistence for Railway deployment."""
    __tablename__ = 'wordbank_storage'
    
    id = db.Column(db.Integer, primary_key=True)
    storage_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUID
    words_data = db.Column(db.JSON, nullable=False)  # List of word dicts
    word_count = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    @classmethod
    def save_wordbank(cls, storage_id: str, words: list, user_id: int = None):
        """Save or update wordbank"""
        existing = cls.query.filter_by(storage_id=storage_id).first()
        if existing:
            existing.words_data = words
            existing.word_count = len(words)
            existing.updated_at = datetime.utcnow()
            existing.last_accessed = datetime.utcnow()
        else:
            new_storage = cls(
                storage_id=storage_id,
                words_data=words,
                word_count=len(words),
                user_id=user_id
            )
            db.session.add(new_storage)
        db.session.commit()
        return True
    
    @classmethod
    def load_wordbank(cls, storage_id: str):
        """Load wordbank and update last_accessed"""
        storage = cls.query.filter_by(storage_id=storage_id).first()
        if storage:
            storage.last_accessed = datetime.utcnow()
            db.session.commit()
            return storage.words_data
        return None
```

---

## 🔑 Key Functions in AjaSpellBApp.py

### `get_wordbank()` (Line 3201)
```python
def get_wordbank() -> List[Dict[str, str]]:
    """Read wordbank from Railway database."""
    storage_id = session.get("wordbank_storage_id")
    if not storage_id:
        return []
    
    # Try in-memory cache first
    if storage_id in WORD_STORAGE:
        return list(WORD_STORAGE[storage_id])
    
    # Load from database
    words = WordBankStorage.load_wordbank(storage_id)
    if words:
        WORD_STORAGE[storage_id] = words  # Cache it
        return list(words)
    
    return []
```

### `set_wordbank()` (Line 3250)
```python
def set_wordbank(rows: List[Dict[str, str]], is_user_upload: bool = False):
    """Save wordbank to Railway database."""
    import uuid
    
    storage_id = session.get("wordbank_storage_id")
    if not storage_id:
        storage_id = str(uuid.uuid4())
        session["wordbank_storage_id"] = storage_id
    
    # Delete old if exists (clean slate)
    existing = WordBankStorage.query.filter_by(storage_id=storage_id).first()
    if existing:
        db.session.delete(existing)
        db.session.flush()
    
    # Save to database
    user_id = current_user.id if current_user.is_authenticated else None
    WordBankStorage.save_wordbank(storage_id, rows, user_id)
    
    # Update session
    session["wordbank_storage_id"] = storage_id
    session["wordbank_count"] = len(rows)
    session.permanent = True
    session.modified = True
```

### `delete_wordbank()` (Line 3300)
```python
def delete_wordbank(storage_id: str):
    """Delete wordbank from database."""
    WordBankStorage.delete_wordbank(storage_id)
```

---

## 📋 Current Status (Local Development)

### Database Configuration
- **URI**: `sqlite:///beesmart.db` → creates `instance/beesmart.db`
- **Location**: `c:\Temp\BeeSmartSpellingBeeApp\instance\beesmart.db` (979 MB)
- **Tables**: All tables created and working
- **WordBankStorage Rows**: 66+ (confirmed working)
- **Upload Test**: ✅ Words persist correctly

### Verified Operations
✅ Upload words via `/api/upload` → saves to database  
✅ Query `WordBankStorage` → returns stored words  
✅ Session persistence → storage_id preserved  
✅ Database commit → words survive server restart  

---

## 🚀 Deployment to Railway

### Prerequisites
1. Railway account and project created
2. PostgreSQL database provisioned in Railway
3. `DATABASE_URL` environment variable set in Railway

### Environment Variables Needed
```
DATABASE_URL=postgresql://user:pass@host:port/dbname
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

### Initial Setup on Railway
1. Deploy code to Railway
2. Run database migration (create wordbank_storage table)
3. Test word upload in production
4. Verify persistence across restarts

### Verify on Railway
```bash
# Check logs for:
# "✅ Saved X words to Railway database"
# "✅ Loaded X words from Railway database"

# Test upload → restart app → verify words still there
```

---

## ⚠️ Known Issues & Fixes

### Issue 1: Session Loss
**Problem**: Cookie cleared → storage_id lost → words appear gone  
**Fix**: Implement user authentication → wordbanks tied to user_id

### Issue 2: Ephemeral Filesystem
**Problem**: Railway container restarts delete `/data/wordbanks/` files  
**Fix**: ✅ All data now in PostgreSQL (not filesystem)

### Issue 3: Multiple Storage Locations
**Problem**: WORD_STORAGE (memory), disk files, and database conflicting  
**Fix**: ✅ Database is single source of truth with in-memory cache

---

## 📝 Testing Checklist

### Local Development
- ✅ Upload words → database persists
- ✅ Server restart → words still load
- ✅ Multiple users → separate storage_ids
- ✅ Database queries work
- ✅ Session management correct

### Before Railway Deploy
- ✅ All code committed to GitHub
- ✅ Database migration script tested
- ✅ Environment variables configured
- ✅ SECRET_KEY set securely
- ✅ DATABASE_URL points to Railway PostgreSQL

### Post-Deploy on Railway
- ✅ Upload words on Railway
- ✅ Check logs for "Saved to database"
- ✅ Restart app → verify words persist
- ✅ Test quiz with saved words
- ✅ Monitor for database errors

---

## 🔗 Related Documentation
- `RAILWAY_WORDBANK_FIX.md` - Deployment guide
- `WORDBANK_SINGLE_SOURCE_FIX.md` - Architecture explanation
- `WORDBANK_PERSISTENCE_FIX.md` - Complete solution details
- `AIS_RAILWAY_SUMMARY.md` - Railway integration overview

---

## 💡 Key Takeaways

1. **Single Source of Truth**: Railway PostgreSQL database
2. **Session Lightweight**: Only stores UUID (36 bytes)
3. **In-Memory Cache**: Fast access for active session
4. **Survives Restarts**: Unlike filesystem or in-memory storage
5. **User-Linked**: Optional user_id for persistence across logins
6. **Automatic Migration**: Old disk wordbanks auto-migrate to database

