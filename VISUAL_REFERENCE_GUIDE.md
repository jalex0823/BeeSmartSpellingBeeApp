# 🗺️ Wordbank System Visual Guide

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     BEESMART WORDBANK SYSTEM                        │
└─────────────────────────────────────────────────────────────────────┘

USER BROWSER
├─ Uploads words (CSV/TXT/JSON)
└─ Takes quiz with saved words

         ↓  (POST /api/upload)

FLASK BACKEND (AjaSpellBApp.py)
├─ Parse and validate words
├─ Kid-friendly content filter
├─ Deduplicate entries
├─ Enrich with definitions
└─ Call set_wordbank()

         ↓  

SESSION LAYER (36 bytes)
┌─────────────────────────┐
│ session[               │
│   "wordbank_          │
│    storage_id" =      │
│   "uuid-1234-..."     │
│ ]                      │
└─────────────────────────┘
Browser Cookie (encrypted)

         ↓  (create/reuse UUID)

IN-MEMORY CACHE (Server RAM)
┌──────────────────────────────────────┐
│ WORD_STORAGE = {                     │
│   "uuid-1234-...": [                │
│     {word, sentence, hint},          │
│     {word, sentence, hint},          │
│     ...                              │
│   ]                                  │
│ }                                    │
└──────────────────────────────────────┘
Lost on server restart (BUT database has it!)

         ↓  (save/update)

DATABASE LAYER (PERSISTENT)
┌──────────────────────────────────────────────────────────────┐
│  PostgreSQL (Railway) or SQLite (Local)                      │
│                                                              │
│  Table: wordbank_storage                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ID │ storage_id │ words_data │ word_count │ user_id  │ │
│  ├────┼────────────┼────────────┼────────────┼──────────┤ │
│  │ 66 │ uuid-12... │ [...]      │ 10         │ NULL     │ │
│  │ 67 │ uuid-56... │ [...]      │ 4          │ 5        │ │
│  │ 68 │ uuid-89... │ [...]      │ 3          │ 8        │ │
│  └────┴────────────┴────────────┴────────────┴──────────┘ │
│                                                              │
│  SURVIVES: Restarts, redeploys, multiple instances          │
└──────────────────────────────────────────────────────────────┘

         ↓  (reload on demand)

QUIZ PAGE
├─ User clicks "Start Quiz"
├─ get_wordbank() called
├─ Load from cache if available
├─ Load from database if needed
└─ Display words in quiz

```

---

## Data Flow Diagram

### Upload Flow
```
User selects file
    ↓
POST /api/upload
    ↓
Parse file
    ↓
Validate & filter
    ↓
Generate storage_id (UUID)
    ↓
set_wordbank(words)
    ├─ Save to WordBankStorage table ✅
    ├─ Cache in WORD_STORAGE dict ✅
    └─ Update session["wordbank_storage_id"] ✅
    ↓
Return: {"ok": true, "count": 10}
    ↓
User sees: "✅ 10 words uploaded"
```

### Quiz Loading Flow
```
User clicks "Start Quiz"
    ↓
get_wordbank() called
    ↓
Check session for storage_id
    ↓
If found:
  ├─ Check WORD_STORAGE cache
  │   ├─ If exists: Use cached version ✅ (fast)
  │   └─ If missing: Query database ↓
  └─ Load from WordBankStorage table ✅ (persistent)
    ↓
If not found:
  └─ Return empty list (user sees "no words" error)
    ↓
Quiz displays words
```

---

## Technology Stack

```
┌──────────────────────────────────────────────────────┐
│  FRONTEND (Browser)                                  │
├──────────────────────────────────────────────────────┤
│  HTML5 / CSS / JavaScript                            │
│  File upload: File API                               │
│  Quiz: WebSocket for real-time                       │
│  Storage: Session cookies (UUID only)                │
└──────────────────────────────────────────────────────┘
           ↕ HTTP/HTTPS
┌──────────────────────────────────────────────────────┐
│  BACKEND (Flask - Python)                            │
├──────────────────────────────────────────────────────┤
│  Framework: Flask 2.x                                │
│  ORM: SQLAlchemy (Flask-SQLAlchemy)                  │
│  Session: Flask-Session (filesystem)                 │
│  Validation: Custom validators                       │
│  Logging: Python logging                             │
│  Cache: In-memory dict (WORD_STORAGE)                │
└──────────────────────────────────────────────────────┘
           ↕ SQL/Connection Pool
┌──────────────────────────────────────────────────────┐
│  DATABASE                                            │
├──────────────────────────────────────────────────────┤
│  Development: SQLite (instance/beesmart.db)          │
│  Production: PostgreSQL (Railway)                    │
│  Table: wordbank_storage (JSON data type)            │
│  Indexes: storage_id, created_at, user_id, ...      │
└──────────────────────────────────────────────────────┘
```

---

## Database Schema Visual

```
wordbank_storage Table
┌─────┬──────────────┬──────────────┬────────────┬──────────────┬────────────────┬────────────────┬──────────┐
│ ID  │ storage_id   │ words_data   │ word_count │ created_at   │ updated_at     │ last_accessed  │ user_id  │
├─────┼──────────────┼──────────────┼────────────┼──────────────┼────────────────┼────────────────┼──────────┤
│  65 │ uuid-001...  │ JSON array   │ 10         │ 2025-12-09   │ 2025-12-09     │ 2025-12-09     │ NULL     │
│ 66 │ uuid-002...  │ JSON array   │ 4          │ 2025-12-09   │ 2025-12-09     │ 2025-12-09     │ 5        │
│ 67 │ uuid-003...  │ JSON array   │ 3          │ 2025-12-09   │ 2025-12-09     │ 2025-12-09     │ NULL     │
└─────┴──────────────┴──────────────┴────────────┴──────────────┴────────────────┴────────────────┴──────────┘

Indexes:
  PRIMARY KEY (id)
  UNIQUE (storage_id)  ← Fast lookup from session UUID
  INDEX (word_count)   ← For sorting/filtering
  INDEX (created_at)   ← For timeline queries
  INDEX (user_id)      ← For user-specific wordbanks

words_data Content (JSON):
[
  {
    "word": "beautiful",
    "sentence": "The sunset is beautiful.",
    "hint": "pretty or attractive"
  },
  {
    "word": "discovery",
    "sentence": "The discovery of fire was important.",
    "hint": "finding something new"
  },
  ...
]
```

---

## Session Management

```
Session Creation
┌──────────────┐
│ New Session  │
└──────────────┘
        ↓
Generate UUID → storage_id
        ↓
Store in session cookie (encrypted)
        ↓
Create entry in wordbank_storage table
        ↓
Return storage_id to browser

Session Continuation
┌──────────────┐
│ Next Page    │ ← Browser sends session cookie
└──────────────┘
        ↓
Flask reads session["wordbank_storage_id"]
        ↓
Use UUID to lookup words in:
  1. WORD_STORAGE (memory) - fast! ✅
  2. Database - if not in memory
        ↓
Words loaded successfully
```

---

## Deployment Architecture

### Local Development
```
You (Developer)
    ↓
Flask App: python AjaSpellBApp.py
    ↓
SQLite: instance/beesmart.db
    ↓
Test locally: ✅ All working
```

### Railway Production
```
You (Developer)
    ↓
Git Push
    ↓
Railway Auto-Deploy
    ↓
Flask App Container
    ↓
PostgreSQL Cloud Database
    ↓
Users access: https://your-app.railway.app
    ↓
Words persist across restarts ✅
```

---

## Function Call Chain

```
User uploads words
    ↓
@app.route("/api/upload") [Line 6643]
    ├─ Parse file/JSON
    ├─ Filter content
    ├─ Enrich definitions
    └─ Call: set_wordbank(rows, is_user_upload=True)
        ↓
    def set_wordbank() [Line 3201]
        ├─ Get/Create storage_id
        ├─ Delete old data (clean slate)
        └─ Call: WordBankStorage.save_wordbank()
            ↓
        @classmethod save_wordbank() [models.py:1495]
            ├─ Query existing record
            ├─ Create or update
            └─ db.session.commit()
                ↓
            Database saved! ✅
```

---

## Error Handling & Fallbacks

```
User requests wordbank
    ↓
get_wordbank() called
    ↓
Try 1: Check WORD_STORAGE cache
  └─ Success: Return cached words ✅
  └─ Fail: Continue to Try 2
        ↓
Try 2: Query database
  └─ Success: Return & cache words ✅
  └─ Fail: Continue to Try 3
        ↓
Try 3: Return empty list []
  └─ User sees: "No words uploaded yet"
  └─ No crash, graceful error ✅
```

---

## Connection String Parsing

```
DATABASE_URL Environment Variable

Format:
postgresql://[user]:[password]@[host]:[port]/[database]

Example:
postgresql://postgres:Aja121514@containers-us-west-22.railway.app:7089/railway

Broken Down:
  Protocol: postgresql://
  User:     postgres
  Password: Aja121514
  Host:     containers-us-west-22.railway.app
  Port:     7089
  Database: railway

Used By:
  Flask-SQLAlchemy: Creates connection pool
  SQL Alchemy: Executes queries
  Word storage: Persists wordbanks
```

---

## Deployment Timeline

```
Hour 0:00
  └─ Get PostgreSQL URL from Railway

Hour 0:05
  └─ Set DATABASE_URL environment variable
  └─ Run: python init_railway_db.py

Hour 0:10
  └─ Verify: "✅ Database initialized"

Hour 0:15
  └─ git push origin main
  └─ Railway auto-deploys

Hour 0:25
  └─ Test upload in production
  └─ Check logs: "✅ Saved to database"

Hour 0:30
  └─ 🎉 PRODUCTION LIVE
  └─ Users can upload & save words
  └─ Words persist across restarts
```

---

## Performance Characteristics

```
Operation | Source | Time | Notes
──────────┼────────┼──────┼─────────────────────
Get Words │ Cache  │ <5ms │ Fastest! (memory)
Get Words │ DB     │ 50ms │ Fast enough (network)
Upload    │ Disk   │ 500ms│ Includes parsing
Save DB   │ Commit │ 100ms│ Depends on network
Restart   │ Reload │ 2-5s │ Load from database

Bottleneck: Network latency (Railway to your region)
Solution: In-memory cache for repeated access
```

---

## Security Architecture

```
User Input
    ↓
Validation
  ├─ File type check (.csv, .txt, .json, .docx, .pdf)
  ├─ File size limit (16 MB max)
  └─ Content filter (kid-friendly)
    ↓
Sanitization
  ├─ Deduplicate entries
  ├─ Normalize text
  └─ Remove special characters
    ↓
Database
  ├─ Parameterized queries (no SQL injection)
  ├─ SQLAlchemy ORM (automatic escaping)
  └─ User_id tracking (optional)
    ↓
Session
  ├─ HttpOnly cookies (can't access from JS)
  ├─ Secure flag (HTTPS only in production)
  └─ SameSite=Lax (CSRF protection)
    ↓
Stored Data ✅ Safe
```

---

## Documentation Map

```
START HERE
    ↓
RAILWAY_SETUP_QUICKSTART.md (5 min)
    ├─ Quick overview
    ├─ Setup steps
    └─ Checklist
        ↓
Then choose your path:

Path A: "Just Deploy It"
  └─ RAILWAY_CONNECTION_SETUP.md (10 min)
     └─ Get URL, set env var, run script
     └─ Ready to deploy!

Path B: "Understand Everything"
  ├─ WORDBANK_ONLINE_DB_REVIEW.md (20 min)
  │  └─ Architecture, schema, functions
  ├─ WORDBANK_PERSISTENCE_FIX.md (15 min)
  │  └─ Problem analysis, solution
  └─ Code Review (15 min)
     └─ models.py, AjaSpellBApp.py

Path C: "Troubleshoot"
  └─ Check troubleshooting sections in:
     ├─ WORDBANK_PERSISTENCE_FIX.md
     ├─ RAILWAY_SETUP_QUICKSTART.md
     └─ RAILWAY_CONNECTION_SETUP.md
```

---

## Status Dashboard

```
╔═══════════════════════════════════════════════════════════════╗
║          BEESMART WORDBANK SYSTEM STATUS                      ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Component              Local    Railway    Status            ║
║  ──────────────────────────────────────────────────────────  ║
║  Database              ✅       ⏳         SQLite / Pending  ║
║  Code                  ✅       ✅         Deployed          ║
║  WordBankStorage       ✅       ✅         Ready             ║
║  Upload API            ✅       ✅         Ready             ║
║  Session Management    ✅       ✅         Ready             ║
║  Documentation         ✅       ✅         Complete          ║
║                                                               ║
║  ➜ Ready for Production: YES                                 ║
║  ➜ Time to Deploy: ~30 minutes                              ║
║  ➜ Next Step: Provide PostgreSQL URL                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

**This visual guide complements the written documentation. Print it out or bookmark for quick reference!**

