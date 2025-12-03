# Quiz & Word List Management - Complete Reference

**Last Updated:** December 3, 2025  
**Purpose:** Comprehensive guide to all quiz routes, word list APIs, and management scripts

---

## 📋 Table of Contents
1. [Quiz Routes (External & Internal)](#quiz-routes)
2. [Word List Management APIs](#word-list-apis)
3. [Session WordBank APIs](#session-wordbank-apis)
4. [Management Scripts](#management-scripts)
5. [Database Tables](#database-tables)
6. [Quick Reference](#quick-reference)

---

## 🎮 Quiz Routes

### Regular Quiz Routes
| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/quiz` | GET | Main quiz interface | No (guest/user) |
| `/api/next` | POST | Get next word in quiz | No |
| `/api/answer` | POST | Submit answer for current word | No |
| `/api/hint` | POST | Get hint for current word | No |
| `/api/skip` | POST | Skip current word | No |
| `/api/quiz-state` | GET | Get current quiz state/progress | No |

### Speed Round Quiz Routes
| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/speed-round-quiz` | GET | Speed round quiz interface | No (guest/user) |
| `/api/speed-round/next` | POST | Get next speed round word | No |
| `/api/speed-round/answer` | POST | Submit speed round answer | No |
| `/api/speed-round/complete` | POST | Complete speed round session | No |

### Practice Quiz Routes
| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/practice-quiz` | GET | Practice mode interface | Yes |
| `/api/practice/next` | POST | Get next practice word | Yes |
| `/api/practice/answer` | POST | Submit practice answer | Yes |

---

## 📝 Word List Management APIs

### Save to Word Lists
| Route | Method | Purpose | Auth Required | Storage |
|-------|--------|---------|---------------|---------|
| `/api/save-to-list` | POST | Save current wordbank to permanent list | Yes | `word_lists` + `word_list_items` tables |

**Request Body:**
```json
{
  "list_name": "My Spelling Words"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Saved 20 words to list 'My Spelling Words'",
  "list_id": 42
}
```

**Database Impact:**
- Creates entry in `word_lists` table (list_name, user_id, word_count, created_at)
- Creates entries in `word_list_items` table (word, sentence, hint, list_id)

### List User's Saved Lists
| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/api/my-lists` | GET | Get all saved word lists for current user | Yes |

**Response:**
```json
{
  "lists": [
    {
      "id": 42,
      "name": "My Spelling Words",
      "word_count": 20,
      "created_at": "2025-12-03T10:30:00",
      "preview": ["apple", "banana", "cherry"]
    }
  ]
}
```

### Load Saved List
| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/api/load-list/<list_id>` | POST | Load saved list into current session | Yes |

**Response:**
```json
{
  "success": true,
  "message": "Loaded 20 words from 'My Spelling Words'",
  "word_count": 20
}
```

**Session Impact:**
- Creates new wordbank in `wordbank_storage` table (or disk fallback)
- Updates session with new `wordbank_storage_id`
- Initializes quiz state with shuffled word indices

### Delete Saved List
| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/api/delete-list/<list_id>` | DELETE | Permanently delete a saved word list | Yes |

**Response:**
```json
{
  "success": true,
  "message": "Deleted list 'My Spelling Words'"
}
```

**Database Impact:**
- Deletes from `word_lists` table (CASCADE deletes `word_list_items`)

---

## 💾 Session WordBank APIs

### Upload/Create WordBank
| Route | Method | Purpose | Auth Required | Storage |
|-------|--------|---------|---------------|---------|
| `/api/upload` | POST | Upload words via text/file/URL | No | `wordbank_storage` table (Railway) |

**Supported Formats:**
- Plain text (one word per line)
- CSV (word, sentence, hint)
- URL scraping
- Image OCR (if Tesseract available)

**Storage Mechanism:**
1. **Railway (Production):** Saves to `wordbank_storage` table (PostgreSQL JSONB)
2. **Local (Development):** Saves to `data/wordbanks/{storage_id}.json` file
3. **Session:** Stores `storage_id` (UUID) in session cookie

### Get Current WordBank
| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/api/wordbank` | GET | Get all words in current session wordbank | No |

**Response:**
```json
{
  "words": [
    {"word": "apple", "sentence": "I ate an apple.", "hint": "red fruit"},
    {"word": "banana", "sentence": "Yellow banana.", "hint": "yellow fruit"}
  ],
  "count": 2
}
```

### Clear Current WordBank
| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/api/clear` | POST | Clear current session wordbank | No |

**Response:**
```json
{
  "success": true,
  "message": "WordBank cleared"
}
```

**Database/File Impact:**
- Deletes from `wordbank_storage` table (if exists)
- Deletes from `data/wordbanks/{storage_id}.json` (if exists)
- Clears session variables: `wordbank_storage_id`, `quiz_state_v1`

### Add Words to WordBank
| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/api/add-words` | POST | Add words to existing wordbank | No |

**Request Body:**
```json
{
  "words": [
    {"word": "dog", "sentence": "The dog barked.", "hint": "animal"}
  ]
}
```

---

## 🛠️ Management Scripts

### Database Management Scripts

#### `scripts/ensure_db_schema.py`
**Purpose:** Ensure all database tables exist with correct schema  
**Usage:**
```powershell
python scripts/ensure_db_schema.py
```
**Tables Created:**
- `users`
- `word_lists`
- `word_list_items`
- `wordbank_storage`
- `password_reset_tokens`
- `avatars`
- `user_avatar_purchases`
- `user_avatar_favorites`

---

#### `create_railway_wordbank_table.py`
**Purpose:** Create `wordbank_storage` table in Railway PostgreSQL  
**Usage:**
```powershell
python create_railway_wordbank_table.py
```
**Output:**
- Creates `wordbank_storage` table with JSONB column
- Creates indexes: `storage_id`, `user_id`, `created_at`, `last_accessed`
- Shows current row count

---

#### `add_wordbank_columns.py`
**Purpose:** Add missing columns to existing wordbank tables  
**Usage:**
```powershell
python add_wordbank_columns.py
```
**Columns Added:**
- `last_accessed` (TIMESTAMP)
- `word_count` (INTEGER)

---

### Word List Cleanup Scripts

#### `scripts/clean_word_lists.py`
**Purpose:** Remove duplicate or invalid word lists  
**Usage:**
```powershell
python scripts/clean_word_lists.py
```
**Actions:**
- Removes duplicate list names for same user
- Removes lists with 0 words
- Removes orphaned `word_list_items` (no parent list)

---

#### `scripts/delete_word_list.py`
**Purpose:** Delete specific word list by ID  
**Usage:**
```powershell
python scripts/delete_word_list.py --list-id 42
```
**Actions:**
- Deletes from `word_lists` table
- Cascade deletes from `word_list_items` table

---

#### `scripts/clear_all_word_lists.py`
**Purpose:** Clear all word lists for a specific user  
**Usage:**
```powershell
python scripts/clear_all_word_lists.py --user-id 5
# OR
python scripts/clear_all_word_lists.py --username "john@example.com"
```
**Actions:**
- Deletes all `word_lists` entries for user
- Cascade deletes all `word_list_items` entries

---

### Word List Statistics Scripts

#### `scripts/count_word_lists.py`
**Purpose:** Show word list statistics for all users  
**Usage:**
```powershell
python scripts/count_word_lists.py
```
**Output:**
```
User: john@example.com
  - Total Lists: 5
  - Total Words: 120
  - Lists:
    * Math Terms (25 words)
    * Science Words (30 words)
    * History Vocabulary (20 words)
```

---

#### `scripts/count_wordbank_storage.py`
**Purpose:** Show wordbank_storage table statistics  
**Usage:**
```powershell
python scripts/count_wordbank_storage.py
```
**Output:**
```
📊 WordBank Storage Statistics
==============================
Total Entries: 15
Guest Wordbanks: 8
User Wordbanks: 7
Average Word Count: 18.5
Oldest Entry: 2025-11-15 (18 days old)
Newest Entry: 2025-12-03 (0 days old)
```

---

#### `scripts/read_word_list.py`
**Purpose:** Display contents of a specific word list  
**Usage:**
```powershell
python scripts/read_word_list.py --list-id 42
```
**Output:**
```
📝 Word List: "My Spelling Words"
Owner: john@example.com
Created: 2025-12-03 10:30:00
Word Count: 20

Words:
1. apple - "I ate an apple." (Hint: red fruit)
2. banana - "Yellow banana." (Hint: yellow fruit)
...
```

---

### WordBank Cleanup Scripts

#### `scripts/clean_old_wordbanks.py`
**Purpose:** Delete wordbank_storage entries older than X days  
**Usage:**
```powershell
# Delete wordbanks older than 30 days
python scripts/clean_old_wordbanks.py --days 30

# Dry run (show what would be deleted)
python scripts/clean_old_wordbanks.py --days 30 --dry-run
```
**Actions:**
- Deletes old entries from `wordbank_storage` table
- Deletes corresponding files from `data/wordbanks/` (if exist)

---

#### `scripts/clear_wordbank_storage.py`
**Purpose:** Clear all wordbank_storage entries  
**Usage:**
```powershell
# Clear all wordbanks
python scripts/clear_wordbank_storage.py --confirm

# Clear only guest wordbanks
python scripts/clear_wordbank_storage.py --guest-only --confirm
```
**Actions:**
- Deletes entries from `wordbank_storage` table
- Optionally deletes files from `data/wordbanks/`

---

## 🗄️ Database Tables

### `word_lists` Table
**Purpose:** Store permanent saved word lists  
**Schema:**
```sql
CREATE TABLE word_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    list_name VARCHAR(255) NOT NULL,
    word_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### `word_list_items` Table
**Purpose:** Store individual words for saved lists  
**Schema:**
```sql
CREATE TABLE word_list_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    word VARCHAR(255) NOT NULL,
    sentence TEXT,
    hint TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES word_lists(id) ON DELETE CASCADE
);
```

### `wordbank_storage` Table
**Purpose:** Store temporary session wordbanks (Railway-safe)  
**Schema (PostgreSQL):**
```sql
CREATE TABLE wordbank_storage (
    id SERIAL PRIMARY KEY,
    storage_id VARCHAR(36) UNIQUE NOT NULL,
    words_data JSONB NOT NULL,
    word_count INTEGER DEFAULT 0,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_wordbank_storage_id ON wordbank_storage(storage_id);
CREATE INDEX idx_wordbank_user_id ON wordbank_storage(user_id);
CREATE INDEX idx_wordbank_created_at ON wordbank_storage(created_at);
CREATE INDEX idx_wordbank_last_accessed ON wordbank_storage(last_accessed);
```

**Schema (SQLite):**
```sql
CREATE TABLE wordbank_storage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_id VARCHAR(36) UNIQUE NOT NULL,
    words_data JSON NOT NULL,
    word_count INTEGER DEFAULT 0,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
```

---

## 🔍 Quick Reference

### Common User Workflows

#### **Guest User - Upload and Quiz**
1. `POST /api/upload` → Upload words (stores in `wordbank_storage`)
2. `GET /quiz` → Start quiz
3. `POST /api/next` → Get next word
4. `POST /api/answer` → Submit answer
5. Repeat steps 3-4 until done

#### **Registered User - Save List for Later**
1. `POST /api/upload` → Upload words (stores in `wordbank_storage`)
2. `POST /api/save-to-list` → Save to permanent list (stores in `word_lists`)
3. Later: `POST /api/load-list/42` → Load list back into session

#### **Admin - View User's Lists**
1. `python scripts/count_word_lists.py` → See all users' lists
2. `python scripts/read_word_list.py --list-id 42` → View specific list
3. `python scripts/delete_word_list.py --list-id 42` → Delete if needed

#### **Maintenance - Clean Old Data**
1. `python scripts/clean_old_wordbanks.py --days 30` → Remove old session data
2. `python scripts/clean_word_lists.py` → Remove duplicates/orphans
3. `python scripts/count_wordbank_storage.py` → Verify cleanup

---

## 📊 Data Flow Diagrams

### Upload → Quiz → Save Flow
```
User Action          API Route              Database               Session
───────────────────────────────────────────────────────────────────────────
Upload words    →    POST /api/upload   →   wordbank_storage   →   storage_id
                                             (temp session)          (UUID)

Start quiz      →    GET /quiz          →   (read from DB)     →   quiz_state_v1
                                                                     (indices, progress)

Take quiz       →    POST /api/next     →   (read from DB)     →   (update progress)
                     POST /api/answer

Save to list    →    POST /api/save     →   word_lists         →   (no session change)
                     -to-list                word_list_items
                                             (permanent storage)

Load list       →    POST /api/load     →   word_lists         →   new storage_id
                     -list/42                → wordbank_storage     (fresh session)
```

### Storage Locations
```
Guest User:
  - Upload → wordbank_storage table (temp)
  - Cannot save to word_lists (auth required)
  - Session cleared on logout/timeout

Registered User:
  - Upload → wordbank_storage table (temp)
  - Save → word_lists + word_list_items (permanent)
  - Can reload saved lists anytime
  - Session persists longer (session.permanent=True)
```

---

## 🚀 Railway vs Local Differences

| Feature | Railway (Production) | Local (Development) |
|---------|---------------------|---------------------|
| WordBank Storage | `wordbank_storage` table (PostgreSQL JSONB) | `data/wordbanks/*.json` files + table fallback |
| File Persistence | ❌ Ephemeral filesystem | ✅ Persistent filesystem |
| Database Type | PostgreSQL | SQLite |
| JSON Column Type | JSONB (binary, indexed) | JSON (text) |
| Session Cookie | SameSite=None, Secure | SameSite=Lax |

---

## 📌 Important Notes

1. **Session WordBanks vs Saved Lists:**
   - `wordbank_storage` = temporary session data (guest uploads, one-time use)
   - `word_lists` = permanent saved lists (registered users only)

2. **Railway Filesystem:**
   - Don't rely on `data/wordbanks/*.json` files in production
   - Always use database-first approach (`wordbank_storage` table)

3. **Session Persistence:**
   - `session.permanent = True` at upload start and quiz init
   - Prevents session loss on mobile devices

4. **Database Cleanup:**
   - Run `clean_old_wordbanks.py` monthly to remove stale session data
   - Run `clean_word_lists.py` quarterly to remove duplicates

5. **Script Safety:**
   - Always use `--dry-run` flag first on cleanup scripts
   - Backup database before bulk deletions
   - Test scripts on local SQLite before running on Railway PostgreSQL

---

## 🔗 Related Documentation

- **Railway WordBank Fix:** `RAILWAY_WORDBANK_FIX.md`
- **WordBank vs WordLists:** `WORDBANK_VS_WORDLISTS.md`
- **Authentication Guide:** `AUTHENTICATION_GUIDE.md`
- **Admin Dashboard:** `ADMIN_USER_MANAGEMENT_COMPLETE.md`
- **Database Schema:** `scripts/ensure_db_schema.py`

---

**Last Updated:** December 3, 2025  
**Maintainer:** BeeSmart Development Team  
**Version:** 1.0
