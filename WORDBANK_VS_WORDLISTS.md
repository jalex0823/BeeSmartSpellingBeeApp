# WordBank vs Word Lists - Understanding the Difference

## Two Separate Systems for Different Purposes

Your app has **TWO** different word storage systems that serve different needs:

---

## 1. 📚 Word Lists (Permanent Saved Lists) - **ALREADY EXISTS** ✅

**Database Tables:**
- `word_lists` - The saved list metadata
- `word_list_items` - Individual words in each list

**Purpose:**
- Teachers/users create **named, organized word lists**
- Lists can be **reused multiple times**
- Has metadata (name, description, difficulty, grade level)
- Lists can be **shared** (is_public flag)
- Lists can be **favorited** (is_favorite flag)
- Permanently stored in PostgreSQL

**Use Cases:**
- "Mrs. Smith's 5th Grade Spelling List"
- "SAT Vocabulary Week 1"
- "Medical Terms - Chapter 5"

**How It Works:**
```
User creates list → Saves to word_lists table → Can load anytime for quizzes
```

**Routes:**
- `/api/saved-lists/` - Manage permanent lists
- `/api/saved-lists/<id>` - Load a specific list

---

## 2. 🎯 WordBank Storage (Session Wordbank) - **NEW FOR RAILWAY** ✅

**Database Table:**
- `wordbank_storage` - Temporary active quiz wordbank

**Purpose:**
- Stores the **CURRENT active quiz wordbank** for the session
- Handles **one-time uploads** (text files, CSV, manual typing, random words)
- NOT a permanent saved list (users don't name it or save it)
- Used once for a quiz, then typically discarded
- **Railway-safe** persistence (survives container restarts)

**Use Cases:**
- User uploads `spelling_words.txt` for today's practice
- User manually types 10 words to quiz on right now
- Random word generator creates 20 words
- Guest users uploading words (no account, can't save permanent lists)

**How It Works:**
```
Upload file → Temporarily stores in wordbank_storage → Loads into quiz → Done
```

**Routes:**
- `/api/upload` - Upload text/CSV files → Goes to wordbank_storage
- `/api/upload-manual-words` - Type words manually → Goes to wordbank_storage
- Random Play → Generates words → Goes to wordbank_storage

---

## Why Both Are Needed

### The Railway Problem (Solved by WordBankStorage)

**Before (Broken on Railway):**
```
/api/upload → session wordbank → data/wordbanks/{uuid}.json (disk file)
                                        ↓
                        Railway restarts → FILE DELETED → Words LOST ❌
```

**After (Fixed with Database):**
```
/api/upload → session wordbank → wordbank_storage table (PostgreSQL)
                                        ↓
                        Railway restarts → Database survives → Words SAFE ✅
```

### Why Not Just Use word_lists for Everything?

**Problem 1: Guest Users**
- Guests can't create permanent saved lists (no account)
- But they CAN upload a file for a quick quiz
- Solution: wordbank_storage works for both guests AND registered users

**Problem 2: One-Time Uploads**
- User uploads `homework.txt` for ONE quiz
- They don't want to save it as a permanent list
- Creating a word_list would clutter their saved lists
- Solution: wordbank_storage is temporary (can be cleaned up after quiz)

**Problem 3: Auto-Generated Content**
- Random Play generates 20 words on the fly
- These aren't manually curated lists to save
- Solution: wordbank_storage for temporary generated content

---

## Data Flow Examples

### Example 1: Teacher Creates Permanent List
```
1. Teacher clicks "Create New List"
2. Names it "Week 5 Spelling"
3. Adds 20 words with definitions
4. Saves → word_lists + word_list_items tables ✅
5. Can reuse this list every year
```

### Example 2: Student Uploads File for Quick Quiz
```
1. Student uploads spelling_homework.txt
2. Goes to /api/upload
3. Stores in wordbank_storage table ✅
4. Loads into quiz
5. After quiz: wordbank_storage entry can be deleted (temporary)
```

### Example 3: Guest User Types Words
```
1. Guest (no account) manually types 5 words
2. Goes to /api/upload-manual-words
3. Stores in wordbank_storage table ✅
4. Takes quiz
5. Session ends: wordbank_storage entry cleaned up (or kept for session recovery)
```

---

## Database Schema Comparison

### word_lists (Permanent)
```sql
word_lists:
- id, uuid, created_by_user_id
- list_name, description
- grade_level, difficulty_level
- is_public, is_favorite
- created_at, updated_at
- times_used

word_list_items:
- id, word_list_id
- word, sentence, hint
- position
```

### wordbank_storage (Temporary Session)
```sql
wordbank_storage:
- id, storage_id (UUID from session)
- words_data (JSON array of {word, sentence, hint})
- word_count
- created_at, updated_at, last_accessed
- user_id (optional, for cleanup)
```

---

## Cleanup Strategy

### word_lists
- Never auto-delete
- User manually deletes if unwanted
- Permanent storage

### wordbank_storage
- Can auto-delete after X days of inactivity
- Can delete after quiz completion (optional)
- Temporary storage with optional persistence for session recovery

**Suggested Cleanup Script:**
```python
# Delete wordbank_storage entries older than 7 days with no access
old_wordbanks = WordBankStorage.query.filter(
    WordBankStorage.last_accessed < (datetime.utcnow() - timedelta(days=7))
).delete()
```

---

## Summary

✅ **word_lists** = Permanent, named, organized, reusable word lists (like a library)  
✅ **wordbank_storage** = Temporary active quiz wordbank (like your current homework)

Both are needed because they serve fundamentally different purposes in the app!
