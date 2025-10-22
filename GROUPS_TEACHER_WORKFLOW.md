# Groups Feature - Teacher Use Case

## 📚 Teacher's Workflow

### Step 1: Teacher Creates Group
```
Teacher Actions:
1. Opens BeeSmart app
2. Clicks "🏆 Groups" menu option
3. Selects "Create Group"
4. Enters group name: "Mrs. Smith's Vocabulary Test"
5. **UPLOADS WORD LIST** - ONE of these options:
   
   Option A: Upload File
   - CSV/TXT/DOCX file with vocabulary words
   - App processes and loads words
   
   Option B: Type Words Manually
   - Type/paste words directly
   
   Option C: Use Random Play
   - Select difficulty level
   - App generates 10 words
   
   Option D: Use Current List
   - Already have words loaded
   - Use those for the group

6. Clicks "Create Group"
7. Gets GROUP CODE: "BEE123"
8. **Teacher writes code on board or shares via email/Teams/etc.**
```

### Step 2: Students Join
```
Student Actions:
1. Opens BeeSmart app
2. Clicks "🏆 Groups"
3. Selects "Join Group"
4. Enters code: "BEE123"
5. Enters their name: "Alice"
6. Sees group info:
   - Group name
   - Number of words
   - Other players already joined
7. **EVERYONE GETS THE SAME WORD LIST**
8. Clicks "Start Quiz"
```

### Step 3: Fair Competition
```
✅ Fairness Guaranteed:
- ALL students get THE SAME words
- Words in THE SAME ORDER (synchronized shuffle)
- Everyone starts fresh (no previous answers affect others)
- Teacher can monitor who's joined
- Teacher can see real-time leaderboard
```

## 🔑 Key Points for Fairness

### 1. Single Shared Word List
```python
# When teacher creates group:
group_data = {
    "word_list": [
        {"word": "photosynthesis", "sentence": "...", "hint": "..."},
        {"word": "metamorphosis", "sentence": "...", "hint": "..."},
        # ... all words
    ],
    "shuffle_seed": 12345  # Same seed for all students
}

# When each student joins:
# They get the EXACT SAME list in EXACT SAME order
student_quiz = shuffle_with_seed(group_data["word_list"], group_data["shuffle_seed"])
```

### 2. Synchronized Order
- Teacher's upload creates ONE master list
- Master list is shuffled ONCE
- ALL students get that SAME shuffled order
- No student has advantage from different order

### 3. Word List Sources

#### Option A: Teacher's Custom Vocabulary List
```
Teacher uploads: vocabulary_week12.txt

Contents:
photosynthesis
metamorphosis
chromosome
precipitation
evaporation
condensation
ecosystem
biodiversity
adaptation
evolution
```

**Result:** All 25 students spell these EXACT 10 words in THIS EXACT order

#### Option B: Teacher Uses Chapter Words
```
Teacher uploads: chapter5_terms.csv

word,definition
mitosis,Cell division process
meiosis,Reproductive cell division
DNA,Genetic material
RNA,Messenger molecule
```

**Result:** All students test on Chapter 5 vocabulary

#### Option C: Teacher Wants Random Challenge
```
Teacher selects: Random Play - Level 4 (Hard)
App generates: 10 random hard words

Result: All students get THE SAME 10 random words
(Generated ONCE when group created, not per student)
```

## 👥 Teacher Controls

### Group Dashboard (Teacher's View)
```
Group: Mrs. Smith's Vocabulary Test
Code: BEE123
Created: Oct 16, 2025 9:00 AM
Expires: Oct 17, 2025 9:00 AM (24 hours)

Word List: 10 words from "chapter5_terms.csv"
└─ photosynthesis
└─ metamorphosis
└─ chromosome
└─ ...

Students (15 joined):
┌─────────────────────────────────────────┐
│ Name        Status      Score  Progress │
│ Alice       ✅ Done     850    10/10    │
│ Bob         🏃 Active   620    7/10     │
│ Charlie     ⏸️ Paused   450    5/10     │
│ David       👋 Joined   0      0/10     │
│ Emma        👋 Joined   0      0/10     │
└─────────────────────────────────────────┘

[View Leaderboard] [End Group] [Export Results]
```

### Teacher Actions:
1. **View Live Progress** - See who's done, who's still spelling
2. **View Leaderboard** - See rankings and scores
3. **Export Results** - Download CSV with all scores
4. **End Group Early** - Stop quiz before time limit
5. **Remove Player** - If wrong student joins

## 📊 After Quiz - Teacher Gets Report

```csv
Student Name,Score,Accuracy,Time Taken,Words Correct,Words Incorrect
Alice,850,100%,5m 23s,10,0
Bob,720,80%,7m 12s,8,2
Charlie,650,70%,6m 45s,7,3
David,580,60%,8m 30s,6,4
Emma,950,100%,4m 15s,10,0
```

## 💡 Real-World Scenarios

### Scenario 1: Weekly Vocabulary Test
```
Teacher: Uploads 15 vocabulary words from textbook
Students: All take quiz during class
Result: Fair test with same words for everyone
Teacher: Exports scores to gradebook
```

### Scenario 2: Spelling Bee Competition
```
Teacher: Uses Random Play - Level 3 (challenging but fair)
Students: Compete for top score
Result: Winner gets recognized
Teacher: Sees detailed results
```

### Scenario 3: Homework Practice
```
Teacher: Creates group in evening
Students: Join from home, practice at own pace
Result: Teacher sees completion next morning
Teacher: Knows who practiced
```

### Scenario 4: Test Review
```
Teacher: Uploads words students got wrong on last test
Students: Practice those specific words
Result: Targeted review
Teacher: Monitors improvement
```

## 🎯 Implementation Details

### Word List Storage in Group
```python
{
  "group_id": "BEE123",
  "group_name": "Mrs. Smith's Vocabulary Test",
  "created_by": "Mrs. Smith",
  "word_list": [
    # SINGLE SOURCE OF TRUTH
    {"word": "photosynthesis", "sentence": "...", "hint": "..."},
    {"word": "metamorphosis", "sentence": "...", "hint": "..."},
    # ... all words uploaded by teacher
  ],
  "shuffle_seed": 12345,  # Ensures same order for all
  "players": {
    # Each player references THE SAME word_list
    "alice_123": {
      "name": "Alice",
      "current_word_index": 5,  # Position in shared list
      "answers": [...]
    }
  }
}
```

### API Flow

#### Teacher Creates with Upload:
```
POST /api/groups/create
FormData:
  group_name: "Mrs. Smith's Test"
  creator_name: "Mrs. Smith"
  word_list_file: vocabulary.csv

Server:
1. Parse uploaded file
2. Create word list with definitions
3. Generate group code
4. Store ONCE in group file
5. Return code to teacher

Response:
  group_code: "BEE123"
  word_count: 15
```

#### Student Joins:
```
POST /api/groups/join
Body:
  group_code: "BEE123"
  player_name: "Alice"

Server:
1. Load group file
2. Get THE SAME word list
3. Add Alice as player
4. Return word list to Alice

Response:
  word_list: [...] ← SAME LIST as everyone else
  word_count: 15
```

## ✅ Fairness Checklist

- [x] **Single word list** - Teacher uploads ONCE
- [x] **Same order** - Synchronized shuffle for all
- [x] **No editing** - Can't change words after creation
- [x] **No peeking** - Students don't see answers
- [x] **Time tracking** - All attempts timestamped
- [x] **Progress isolation** - One student's progress doesn't affect others
- [x] **Score transparency** - Everyone can see fair leaderboard
- [x] **Export capability** - Teacher gets complete results

## 🚨 Important Notes

1. **Word list is LOCKED after group creation** - Can't be changed
2. **Same list for ALL players** - No variations
3. **Fair randomization** - If shuffled, uses same seed
4. **Teacher uploads BEFORE students join** - List ready immediately
5. **24-hour expiration** - Automatic cleanup prevents confusion

---

**This ensures COMPLETE FAIRNESS for all students! 🎯**
