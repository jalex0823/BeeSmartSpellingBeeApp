# Word Input & Quiz Flow - Visual Diagrams

**Last Updated:** December 3, 2025  
**Purpose:** Visual representation of how words flow from input to quiz completion

---

## 🎯 Overview: Internal vs External Word Sources

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WORD INPUT SOURCES                              │
└─────────────────────────────────────────────────────────────────────────┘

INTERNAL SOURCES (Saved Lists)              EXTERNAL SOURCES (New Uploads)
═════════════════════════════                ══════════════════════════════
                                            
┌──────────────────────┐                    ┌──────────────────────┐
│   word_lists table   │                    │  Text Input          │
│   ──────────────     │                    │  • Manual typing     │
│   • User saved lists │                    │  • Paste text        │
│   • Permanent        │                    └──────────────────────┘
│   • Reusable         │                    
└──────────────────────┘                    ┌──────────────────────┐
          │                                 │  File Upload         │
          │                                 │  • .txt files        │
          │                                 │  • .csv files        │
          │                                 │  • Word docs         │
          ▼                                 └──────────────────────┘
┌──────────────────────┐                    
│ POST /api/load-list  │                    ┌──────────────────────┐
│       /{list_id}     │                    │  URL Scraping        │
└──────────────────────┘                    │  • Web pages         │
          │                                 │  • Online lists      │
          │                                 └──────────────────────┘
          │                                 
          │                                 ┌──────────────────────┐
          │                                 │  Image OCR           │
          │                                 │  • Photo of list     │
          │                                 │  • Scanned document  │
          │                                 └──────────────────────┘
          │                                           │
          │                                           │
          │                                           ▼
          │                                 ┌──────────────────────┐
          │                                 │  POST /api/upload    │
          │                                 └──────────────────────┘
          │                                           │
          └───────────────────┬───────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  wordbank_storage   │
                    │  ─────────────────  │
                    │  • Temporary        │
                    │  • Session-based    │
                    │  • UUID pointer     │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   SESSION COOKIE    │
                    │   storage_id (UUID) │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  init_quiz_state()  │
                    │  • Shuffle indices  │
                    │  • Reset progress   │
                    └─────────────────────┘
                              │
                              ▼
                         ┌─────────┐
                         │  QUIZ   │
                         └─────────┘
```

---

## 📊 Detailed Flow: External Upload → Quiz

```
USER ACTION                 BACKEND PROCESS                DATABASE/SESSION
═══════════════════════════════════════════════════════════════════════════

1️⃣ UPLOAD WORDS
─────────────────────────────────────────────────────────────────────────
User uploads                POST /api/upload
"apple, banana,             │
cherry"                     ├─► Parse input
                            │   • Detect format (text/CSV/URL/image)
                            │   • Extract words
                            │   • Normalize (lowercase, trim)
                            │
                            ├─► Enrich words
                            │   • Generate sentences (if missing)
                            │   • Generate hints (if missing)
                            │   • Lookup definitions (get_word_info)
                            │
                            ├─► Deduplicate
                            │   • Remove exact matches
                            │   • Case-insensitive compare
                            │
                            ├─► Create storage_id                    Session:
                            │   • Generate UUID                      storage_id = 
                            │   • session.permanent = True           "a1b2c3d4..."
                            │
                            └─► Save to database                     Database:
                                _save_wordbank_to_disk()            wordbank_storage
                                                                    ┌───────────────┐
                                                                    │ storage_id    │
                                                                    │ words_data: [ │
                                                                    │   {word:"..." │
                                                                    │    sentence   │
                                                                    │    hint}      │
                                                                    │ ]             │
                                                                    │ word_count: 3 │
                                                                    └───────────────┘

2️⃣ INITIALIZE QUIZ
─────────────────────────────────────────────────────────────────────────
User clicks                 init_quiz_state()
"Start Quiz"                │
                            ├─► Get wordbank from storage_id        Database:
                            │   _load_wordbank_from_disk()          Read from
                            │                                       wordbank_storage
                            │
                            ├─► Create shuffled indices             Session:
                            │   [2, 0, 1] (random order)            quiz_state_v1:
                            │                                       ┌───────────────┐
                            │                                       │ indices:[2,0,1]
                            │                                       │ current_idx:0 │
                            │                                       │ correct:0     │
                            │                                       │ incorrect:0   │
                            │                                       │ skipped:0     │
                            └─► session.permanent = True            └───────────────┘

3️⃣ QUIZ LOOP
─────────────────────────────────────────────────────────────────────────
User sees quiz page         GET /quiz
                            │
                            └─► Render quiz.html with current word


User clicks                 POST /api/next
"Next Word"                 │
                            ├─► Get quiz_state from session         Session:
                            │   current_idx = 0                     quiz_state_v1
                            │   shuffled_idx = indices[0] = 2       current_idx: 0
                            │
                            ├─► Get wordbank from storage_id        Database:
                            │   _load_wordbank_from_disk()          wordbank_storage
                            │                                       words_data[2]
                            │
                            ├─► Get word at shuffled_idx            
                            │   word_obj = words[2]                 
                            │   = {word:"cherry", sentence:"...", hint:"..."}
                            │
                            └─► Return word (NO BLANKING)           Response:
                                • Full word visible                 {
                                • Sentence visible                    "word":"cherry"
                                • Hint visible                        "sentence":"..."
                                                                      "hint":"..."
                                                                    }


User types answer           POST /api/answer
"cherry"                    │
                            ├─► Get current word                    Database:
                            │   from storage_id + current_idx       wordbank_storage
                            │
                            ├─► Normalize answer                    
                            │   user: "cherry" → "cherry"
                            │   correct: "cherry" → "cherry"
                            │
                            ├─► Compare (case-insensitive)          
                            │   if user == correct:
                            │     correct_count += 1
                            │   else:
                            │     incorrect_count += 1
                            │
                            ├─► Update quiz_state                   Session:
                            │   current_idx += 1                    quiz_state_v1:
                            │   (move to next word)                 current_idx: 1
                            │                                       correct: 1
                            │
                            └─► Check if quiz complete              
                                if current_idx >= total_words:
                                  quiz_complete = True


User completes quiz         Quiz Summary Page
                            │
                            ├─► Calculate stats
                            │   • Total words
                            │   • Correct count
                            │   • Incorrect count
                            │   • Percentage
                            │   • Time elapsed
                            │
                            └─► Display results


4️⃣ OPTIONAL: SAVE TO LIST (Registered Users Only)
─────────────────────────────────────────────────────────────────────────
User clicks                 POST /api/save-to-list
"Save to My Lists"          { "list_name": "My Words" }
                            │
                            ├─► Get wordbank from storage_id        Database:
                            │   _load_wordbank_from_disk()          wordbank_storage
                            │                                       (read temp data)
                            │
                            ├─► Create permanent list               Database:
                            │   INSERT INTO word_lists              word_lists
                            │   (user_id, list_name, word_count)    ┌──────────────┐
                            │                                       │ id: 42       │
                            │                                       │ user_id: 5   │
                            │                                       │ list_name:   │
                            │                                       │ "My Words"   │
                            │                                       │ word_count:3 │
                            │                                       └──────────────┘
                            │
                            └─► Insert individual words             Database:
                                INSERT INTO word_list_items         word_list_items
                                (list_id, word, sentence, hint)     ┌──────────────┐
                                                                    │ list_id: 42  │
                                                                    │ word:"apple" │
                                                                    │ sentence:"." │
                                                                    │ hint:"fruit" │
                                                                    └──────────────┘
                                                                    (3 rows total)
```

---

## 🔄 Detailed Flow: Internal Load → Quiz

```
USER ACTION                 BACKEND PROCESS                DATABASE/SESSION
═══════════════════════════════════════════════════════════════════════════

1️⃣ VIEW SAVED LISTS
─────────────────────────────────────────────────────────────────────────
User navigates to           GET /api/my-lists
"My Word Lists"             │
                            ├─► Query database                      Database:
                            │   SELECT * FROM word_lists            word_lists
                            │   WHERE user_id = current_user.id     ┌──────────────┐
                            │                                       │ id: 42       │
                            │                                       │ name:"Math"  │
                            │                                       │ count: 20    │
                            │                                       └──────────────┘
                            │                                       │ id: 43       │
                            │                                       │ name:"Sci"   │
                            │                                       │ count: 15    │
                            │                                       └──────────────┘
                            │
                            └─► Return list of saved lists          Response:
                                                                    {lists:[
                                                                      {id:42,...}
                                                                      {id:43,...}
                                                                    ]}

2️⃣ LOAD SAVED LIST
─────────────────────────────────────────────────────────────────────────
User clicks                 POST /api/load-list/42
"Load 'Math Terms'"         │
                            ├─► Verify ownership                    Database:
                            │   Check list belongs to user          word_lists
                            │                                       WHERE id=42
                            │                                       AND user_id=5
                            │
                            ├─► Load all words from list            Database:
                            │   SELECT * FROM word_list_items       word_list_items
                            │   WHERE list_id = 42                  WHERE list_id=42
                            │   ORDER BY id                         ┌──────────────┐
                            │                                       │ word:"add"   │
                            │                                       │ sentence:"." │
                            │                                       │ hint:"math"  │
                            │                                       └──────────────┘
                            │                                       (20 rows)
                            │
                            ├─► Create NEW storage_id               Session:
                            │   • Generate fresh UUID                storage_id = 
                            │   • Clear old wordbank                 "new-uuid-456"
                            │   • session.permanent = True
                            │
                            ├─► Save to wordbank_storage            Database:
                            │   _save_wordbank_to_disk()            wordbank_storage
                            │   (creates temp copy for session)     ┌──────────────┐
                            │                                       │ storage_id:  │
                            │                                       │ "new-uuid"   │
                            │                                       │ words_data:  │
                            │                                       │ [{word:"add" │
                            │                                       │   ...}]      │
                            │                                       │ word_count:20│
                            │                                       └──────────────┘
                            │
                            └─► Initialize quiz state               Session:
                                init_quiz_state()                   quiz_state_v1:
                                • Shuffle 20 indices                ┌──────────────┐
                                • Reset progress                    │ indices:[5,  │
                                                                    │   12,3,...]  │
                                                                    │ current_idx:0│
                                                                    │ correct:0    │
                                                                    └──────────────┘

3️⃣ QUIZ PROCEEDS SAME AS EXTERNAL UPLOAD
─────────────────────────────────────────────────────────────────────────
(See "QUIZ LOOP" section above)

User takes quiz exactly the same way whether words came from:
  • External upload (text/file/URL/image)
  • Internal saved list (word_lists table)

Both create a wordbank_storage entry and use same quiz flow.
```

---

## 🎮 Quiz Type Comparison

```
┌────────────────────────────────────────────────────────────────────────┐
│                          QUIZ TYPE MATRIX                              │
└────────────────────────────────────────────────────────────────────────┘

FEATURE              REGULAR QUIZ    SPEED ROUND      PRACTICE MODE
════════════════════════════════════════════════════════════════════════
Route                /quiz           /speed-round     /practice-quiz
                                     -quiz

Auth Required        No (guest OK)   No (guest OK)    Yes (users only)

Next Word API        POST /api/next  POST /api/       POST /api/
                                     speed-round      practice/next
                                     /next

Answer API           POST /api/      POST /api/       POST /api/
                     answer          speed-round      practice/answer
                                     /answer

Timed                No              Yes (countdown)  No

Hints Available      Yes             No               Yes

Skip Allowed         Yes             No               Yes

Progress Saved       Session only    No (disposable)  User profile

Score Tracking       Session only    Leaderboard      User stats

Word Source          wordbank_       wordbank_        wordbank_
                     storage         storage          storage

Can Save Results     No              No               Yes (to profile)

Mobile Friendly      Yes             Yes              Yes
════════════════════════════════════════════════════════════════════════
```

---

## 🗄️ Database vs Session Storage

```
┌────────────────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER ARCHITECTURE                         │
└────────────────────────────────────────────────────────────────────────┘

SESSION (Cookie)                    DATABASE (PostgreSQL/SQLite)
════════════════                    ════════════════════════════

┌──────────────────┐                ┌──────────────────────────┐
│ storage_id       │───────────────▶│  wordbank_storage        │
│ "uuid-123"       │  Points to     │  ────────────────        │
└──────────────────┘                │  storage_id: "uuid-123"  │
                                    │  words_data: [           │
┌──────────────────┐                │    {word:"apple",        │
│ quiz_state_v1    │                │     sentence:"...",      │
│ ────────────     │                │     hint:"..."},         │
│ {                │                │    {word:"banana",...}   │
│   indices:[2,0,1]│                │  ]                       │
│   current_idx:0  │                │  word_count: 20          │
│   correct:5      │                │  user_id: NULL (guest)   │
│   incorrect:2    │                │  created_at: "..."       │
│   skipped:1      │                │  last_accessed: "..."    │
│ }                │                └──────────────────────────┘
└──────────────────┘                           │
                                               │
                                               │
                                    ┌──────────────────────────┐
                                    │  word_lists              │
                                    │  ───────────             │
                                    │  id: 42                  │
                                    │  user_id: 5              │
                                    │  list_name: "Math"       │
                                    │  word_count: 20          │
                                    │  created_at: "..."       │
                                    └──────────────────────────┘
                                               │
                                               │
                                    ┌──────────────────────────┐
                                    │  word_list_items         │
                                    │  ────────────────        │
                                    │  id: 1                   │
                                    │  list_id: 42             │
                                    │  word: "addition"        │
                                    │  sentence: "2+2=4"       │
                                    │  hint: "math operation"  │
                                    └──────────────────────────┘
                                    │  id: 2                   │
                                    │  list_id: 42             │
                                    │  word: "subtract"        │
                                    │  ...                     │
                                    └──────────────────────────┘
                                    (20 rows for list_id=42)

TEMPORARY vs PERMANENT
══════════════════════

wordbank_storage          →  Temporary session data
  • Guest uploads              • Cleared on logout
  • One-time uploads           • Railway: auto-cleanup after 30 days
  • Active quiz sessions       • Can be deleted anytime

word_lists               →  Permanent saved lists
  • User's library             • Never auto-deleted
  • Reusable                   • User can delete manually
  • Organized by name          • Survives logout/restart
```

---

## 🔐 Guest vs Registered User Differences

```
┌────────────────────────────────────────────────────────────────────────┐
│                      USER TYPE COMPARISON                              │
└────────────────────────────────────────────────────────────────────────┘

GUEST USER                          REGISTERED USER
══════════                          ═══════════════

Upload Words                        Upload Words
     │                                   │
     ▼                                   ▼
wordbank_storage                    wordbank_storage
(user_id = NULL)                    (user_id = 5)
     │                                   │
     │                                   ├─► Can save to word_lists
     │                                   │   POST /api/save-to-list
     ▼                                   │
Take Quiz                                ▼
     │                              word_lists table
     │                              (permanent storage)
     ▼                                   │
Session ends                             │
     │                                   ▼
     ▼                              Can reload anytime
Wordbank lost                       POST /api/load-list/42
(cannot save)                            │
                                         ▼
                                    Take Quiz
                                         │
                                         ▼
                                    Session ends
                                         │
                                         ▼
                                    Wordbank cleared
                                    (but list still saved)


LIMITATIONS:
────────────────────────────────────────────────────────────────────────
Guest User:
  ❌ Cannot save lists permanently
  ❌ Cannot reload past lists
  ❌ Session cleared on logout
  ✅ Can upload and quiz immediately
  ✅ No account required

Registered User:
  ✅ Save unlimited word lists
  ✅ Reload lists anytime
  ✅ Organize lists by name
  ✅ View all saved lists
  ✅ Delete lists
  ✅ Session persists longer
```

---

## 📱 Session Persistence Strategy

```
┌────────────────────────────────────────────────────────────────────────┐
│                    SESSION LIFECYCLE DIAGRAM                           │
└────────────────────────────────────────────────────────────────────────┘

CRITICAL POINTS WHERE session.permanent = True
═══════════════════════════════════════════════

1. POST /api/upload (Line 6437)
   ┌────────────────────────────┐
   │ User uploads words         │
   │                            │
   │ session.permanent = True   │◀── Prevents mobile session loss
   │ storage_id = "uuid-..."    │
   │                            │
   └────────────────────────────┘

2. init_quiz_state() (Line 3137)
   ┌────────────────────────────┐
   │ Quiz initialized           │
   │                            │
   │ session.permanent = True   │◀── Extends session lifetime
   │ quiz_state_v1 = {...}      │
   │                            │
   └────────────────────────────┘

3. POST /api/load-list (calls init_quiz_state)
   ┌────────────────────────────┐
   │ Saved list loaded          │
   │                            │
   │ session.permanent = True   │◀── Implicit via init_quiz_state
   │                            │
   └────────────────────────────┘


SESSION COOKIE SETTINGS
═══════════════════════

Local Development:
  • SameSite=Lax
  • Secure=False (HTTP allowed)
  • Max-Age=31536000 (1 year if permanent)

Railway Production:
  • SameSite=None (cross-site allowed)
  • Secure=True (HTTPS required)
  • Max-Age=31536000 (1 year if permanent)


WHY THIS MATTERS
════════════════

Without session.permanent = True:
  ❌ Session expires when browser closes
  ❌ Mobile apps lose session on background
  ❌ Users lose quiz progress
  ❌ Uploaded words disappear

With session.permanent = True:
  ✅ Session lasts 1 year (or until logout)
  ✅ Mobile apps maintain session
  ✅ Quiz progress saved
  ✅ Words persist across visits
```

---

## 🚀 Railway vs Local Data Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                  ENVIRONMENT-SPECIFIC STORAGE                          │
└────────────────────────────────────────────────────────────────────────┘

LOCAL DEVELOPMENT (SQLite)         RAILWAY PRODUCTION (PostgreSQL)
═══════════════════════════         ═══════════════════════════════

_save_wordbank_to_disk():           _save_wordbank_to_disk():
     │                                   │
     ├─► Try Database First              ├─► Try Database First
     │   WordBankStorage.save()          │   WordBankStorage.save()
     │   (SQLite JSON column)            │   (PostgreSQL JSONB column)
     │   ✅ Success                       │   ✅ Success
     │                                   │
     ├─► Fallback to File               ├─► Fallback to File
     │   data/wordbanks/uuid.json        │   data/wordbanks/uuid.json
     │   ✅ Persists across restarts     │   ⚠️ EPHEMERAL - deleted on restart
     │                                   │
     └─► Result: Dual storage            └─► Result: Database-only reliable


_load_wordbank_from_disk():         _load_wordbank_from_disk():
     │                                   │
     ├─► Try Database First              ├─► Try Database First
     │   WordBankStorage.load()          │   WordBankStorage.load()
     │   ✅ Found                         │   ✅ Found
     │   Return words                    │   Return words
     │                                   │
     ├─► Fallback to File               ├─► Fallback to File
     │   Check data/wordbanks/           │   Check data/wordbanks/
     │   ✅ Found                         │   ❌ File missing (restart)
     │   Auto-migrate to DB              │   Return None (data lost)
     │                                   │
     └─► Result: Always works            └─► Result: DB is critical


FILESYSTEM PERSISTENCE
══════════════════════

Local:                               Railway:
  /data/wordbanks/                     /data/wordbanks/
       ├── uuid-1.json  ✅ Persists         ├── uuid-1.json  ❌ Deleted
       ├── uuid-2.json  ✅ Persists         ├── uuid-2.json  ❌ Deleted
       └── uuid-3.json  ✅ Persists         └── uuid-3.json  ❌ Deleted
                                            (on every deployment/restart)

DATABASE PERSISTENCE
════════════════════

Local SQLite:                        Railway PostgreSQL:
  instance/app.db                      (Railway-hosted)
       ✅ Persists                          ✅ Persists
       ✅ Backed up locally                 ✅ Backed up by Railway
       ✅ Can inspect with tools            ✅ Can query remotely


KEY TAKEAWAY
════════════

LOCAL:  Database + File (both work)
RAILWAY: Database ONLY (files unreliable)

Always use WordBankStorage model for Railway production!
```

---

## 🔍 Word Enrichment Pipeline

```
┌────────────────────────────────────────────────────────────────────────┐
│                    WORD ENRICHMENT PROCESS                             │
└────────────────────────────────────────────────────────────────────────┘

User Input: "apple, banana, cherry"
     │
     ▼
┌─────────────────────────────────────┐
│ 1. PARSE & NORMALIZE                │
│    • Split by comma/newline         │
│    • Trim whitespace                │
│    • Lowercase for comparison       │
│    • Remove empty entries           │
│    Result: ["apple","banana","..."] │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 2. DEDUPLICATE                      │
│    • Remove exact matches           │
│    • Case-insensitive compare       │
│    • Keep first occurrence          │
│    Result: 3 unique words           │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 3. ENRICH EACH WORD                 │
│    For each word:                   │
│      ├─► Has sentence? Keep it      │
│      │   No sentence?               │
│      │    └─► Generate default:     │
│      │        "Spell: apple"        │
│      │                              │
│      ├─► Has hint? Keep it          │
│      │   No hint?                   │
│      │    └─► Get from dictionary:  │
│      │        get_word_info(word)   │
│      │                              │
│      └─► Result:                    │
│          {word:"apple",             │
│           sentence:"Spell: apple",  │
│           hint:"A round fruit..."}  │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 4. FILTER DEFINITIONS (Kid-Safe)   │
│    _filter_definition():            │
│      • Remove spelling hints        │
│      • Remove blanked answers       │
│      • Simplify complex terms       │
│      • Kid-friendly language        │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 5. SAVE TO STORAGE                  │
│    _save_wordbank_to_disk():        │
│      • Generate UUID storage_id     │
│      • Save to wordbank_storage DB  │
│      • Store in session cookie      │
│      • Log success/failure          │
└─────────────────────────────────────┘


DICTIONARY LOOKUP CASCADE
══════════════════════════

get_word_info(word):
     │
     ├─► 1. Simple English Wiktionary Cache (Background-loaded)
     │      ✅ Found → Use this
     │      ❌ Not found → Continue
     │
     ├─► 2. Local Dictionary Cache (data/dictionary.json)
     │      ✅ Found → Use this
     │      ❌ Not found → Continue
     │
     ├─► 3. Live Dictionary API (dictionary_api.lookup_word)
     │      • 500ms rate limit
     │      • Circuit breaker protection
     │      ✅ Found → Cache & use
     │      ❌ Not found → Continue
     │
     └─► 4. Smart Fallback (generate_smart_fallback)
            • Generic educational hint
            • No spelling revealed
            • Kid-friendly description
```

---

## 📊 Complete End-to-End Example

```
SCENARIO: Registered user uploads 3 words, takes quiz, saves list
═════════════════════════════════════════════════════════════════

1️⃣ User uploads text: "cat\ndog\nbird"

   POST /api/upload
        │
        ├─► Parse: ["cat", "dog", "bird"]
        ├─► Dedupe: All unique
        ├─► Enrich:
        │   • cat  → {word:"cat", sentence:"Spell: cat", hint:"A small furry pet..."}
        │   • dog  → {word:"dog", sentence:"Spell: dog", hint:"A loyal animal..."}
        │   • bird → {word:"bird", sentence:"Spell: bird", hint:"A flying creature..."}
        │
        ├─► Generate storage_id: "abc-123"
        │
        ├─► Save to database:
        │   INSERT INTO wordbank_storage
        │   (storage_id, words_data, word_count, user_id)
        │   VALUES ('abc-123', '[{...}]', 3, 5)
        │
        └─► Update session:
            session['wordbank_storage_id'] = 'abc-123'
            session.permanent = True

   Response: {"success": true, "word_count": 3}

─────────────────────────────────────────────────────────────────

2️⃣ User navigates to /quiz

   GET /quiz
        │
        ├─► Check session: storage_id = 'abc-123'
        ├─► Call init_quiz_state():
        │   │
        │   ├─► Load words from DB:
        │   │   SELECT words_data FROM wordbank_storage
        │   │   WHERE storage_id = 'abc-123'
        │   │   → 3 words
        │   │
        │   ├─► Shuffle indices: [1, 2, 0]
        │   │   (dog, bird, cat)
        │   │
        │   └─► Save to session:
        │       quiz_state_v1 = {
        │         indices: [1, 2, 0],
        │         current_idx: 0,
        │         correct: 0,
        │         incorrect: 0,
        │         skipped: 0
        │       }
        │
        └─► Render quiz.html

─────────────────────────────────────────────────────────────────

3️⃣ User clicks "Next Word"

   POST /api/next
        │
        ├─► Get quiz_state: current_idx = 0
        ├─► Get shuffled_idx: indices[0] = 1
        ├─► Load wordbank: storage_id = 'abc-123'
        ├─► Get word: words[1] = "dog"
        │
        └─► Response:
            {
              "word": "dog",
              "sentence": "Spell: dog",
              "hint": "A loyal animal that barks",
              "progress": "1/3"
            }

─────────────────────────────────────────────────────────────────

4️⃣ User types "dog" and submits

   POST /api/answer
   {"user_input": "dog", "method": "typed", "elapsed_ms": 5000}
        │
        ├─► Normalize: "dog" → "dog"
        ├─► Compare: "dog" == "dog" ✅
        ├─► Update quiz_state:
        │   correct += 1
        │   current_idx += 1
        │
        └─► Response:
            {
              "correct": true,
              "message": "Correct!",
              "correct_count": 1,
              "total": 3
            }

─────────────────────────────────────────────────────────────────

5️⃣ User completes all 3 words (2 correct, 1 incorrect)

   Quiz Summary:
        • Total: 3
        • Correct: 2
        • Incorrect: 1
        • Score: 66.7%

─────────────────────────────────────────────────────────────────

6️⃣ User clicks "Save to My Lists"

   POST /api/save-to-list
   {"list_name": "My Pets"}
        │
        ├─► Load wordbank: storage_id = 'abc-123'
        │   → 3 words
        │
        ├─► Create list:
        │   INSERT INTO word_lists
        │   (user_id, list_name, word_count)
        │   VALUES (5, 'My Pets', 3)
        │   → list_id = 42
        │
        ├─► Insert words:
        │   INSERT INTO word_list_items (list_id, word, sentence, hint)
        │   VALUES (42, 'cat', '...', '...'),
        │          (42, 'dog', '...', '...'),
        │          (42, 'bird', '...', '...')
        │
        └─► Response:
            {
              "success": true,
              "message": "Saved 3 words to 'My Pets'",
              "list_id": 42
            }

─────────────────────────────────────────────────────────────────

7️⃣ One week later: User wants to quiz again

   Step 1: GET /api/my-lists
           → Returns: [{id: 42, name: "My Pets", word_count: 3}]

   Step 2: POST /api/load-list/42
           │
           ├─► Load from word_lists:
           │   SELECT * FROM word_list_items WHERE list_id = 42
           │   → 3 words
           │
           ├─► Create NEW storage_id: "xyz-789"
           │
           ├─► Save to wordbank_storage:
           │   INSERT INTO wordbank_storage
           │   (storage_id, words_data, word_count, user_id)
           │   VALUES ('xyz-789', '[{...}]', 3, 5)
           │
           ├─► Update session:
           │   storage_id = 'xyz-789'
           │
           └─► Initialize quiz: init_quiz_state()

   Step 3: Take quiz with fresh shuffle order

═════════════════════════════════════════════════════════════════
```

---

## 🎯 Key Insights

### Storage Architecture
1. **Temporary (wordbank_storage):**
   - Guest uploads
   - One-time quiz sessions
   - Auto-cleanup after 30 days
   - Railway: Database-only (files ephemeral)

2. **Permanent (word_lists):**
   - User's saved library
   - Reusable forever
   - Organized by name
   - Survives logout/restart

### Quiz Flow Independence
- Quiz doesn't care about word source
- Internal (saved list) or External (upload) both create wordbank_storage
- Same quiz logic for all sources
- Session-based progress tracking

### Railway Considerations
- Always use database-first approach
- Don't rely on `data/wordbanks/*.json` files
- Session persistence critical for mobile
- JSONB column for efficient JSON storage

---

**Last Updated:** December 3, 2025  
**See Also:** 
- `QUIZ_WORDLIST_LINKS.md` - API reference
- `RAILWAY_WORDBANK_FIX.md` - Railway persistence fix
- `WORDBANK_VS_WORDLISTS.md` - Storage differences
