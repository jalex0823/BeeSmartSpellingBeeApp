# Groups Feature - Design Document

## 🎯 Feature Overview
Enable multiple players to compete against each other using the same word list, tracking scores and creating a competitive spelling bee experience.

## 🎮 Use Cases

### Scenario 1: Classroom Competition
- Teacher creates a group with 20 words
- Students join using a group code
- Everyone spells the same words
- Leaderboard shows who's winning
- Teacher can monitor progress

### Scenario 2: Family Game Night
- Parent creates a group
- Kids join with simple code
- Everyone practices same words
- Real-time scores displayed
- Fun competitive atmosphere

### Scenario 3: Study Group
- Student creates study session
- Friends join to practice together
- Same word list for consistency
- Compare results afterward

## 🏗️ Architecture Options

### Option A: Session-Based (No Backend Database)
**Pros:**
- No database needed
- Quick to implement
- Works with current architecture

**Cons:**
- Groups disappear when server restarts
- Limited to single server instance
- Can't persist history

### Option B: Database-Backed (Recommended for Production)
**Pros:**
- Persistent groups
- Can save history
- Multi-server support
- Better scalability

**Cons:**
- Requires database setup
- More complex

### Option C: Hybrid Approach (Recommended for MVP)
**Pros:**
- Start simple with in-memory
- Can migrate to database later
- File-based persistence option

## 💡 Recommended Implementation: Hybrid File-Based

### Data Structure
```python
{
  "group_id": "ABC123",
  "group_name": "Mrs. Smith's Class",
  "created_by": "teacher_name",
  "created_at": "2025-10-16T21:00:00",
  "word_list": [...],  # List of word objects
  "expires_at": "2025-10-17T21:00:00",  # 24 hour expiration
  "players": {
    "player_id_1": {
      "name": "Alice",
      "joined_at": "...",
      "current_word_index": 5,
      "correct_count": 4,
      "incorrect_count": 1,
      "completed": false,
      "completion_time": null,
      "score": 400,  # Points system
      "last_active": "..."
    }
  }
}
```

## 🔑 Key Features

### 1. Group Creation
- **Who:** Teacher/Host creates the group
- **Input:** Group name, word list (upload or random)
- **Output:** 6-digit group code (e.g., "BEE123")
- **Storage:** Save to `data/groups/{group_id}.json`

### 2. Join Group
- **Who:** Students/Players join
- **Input:** Group code + player name
- **Output:** Join confirmation, start quiz
- **Validation:** Check if code exists and not expired

### 3. Quiz Synchronization
- **Word Order:** Same shuffle seed for all players
- **Progress:** Each player tracks own position
- **Scoring:** Points based on:
  - Correctness (100 points)
  - Speed (bonus points)
  - Streak (multiplier)

### 4. Live Leaderboard
- **Display:** Real-time rankings
- **Metrics:**
  - Current score
  - Words completed
  - Accuracy percentage
  - Completion status
- **Update:** Every time player answers

### 5. Group Management
- **Host Controls:**
  - View all players
  - Remove player
  - End group early
  - Export results
- **Auto-cleanup:** Delete expired groups (>24 hours)

## 🎨 User Flow

### Creating a Group
```
1. User clicks "🏆 Groups" menu option
2. Modal appears: "Create or Join Group?"
3. Click "Create Group"
4. Enter group name
5. Choose word list source:
   - Upload file
   - Use Random Play
   - Use current word list
6. Click "Create"
7. Get group code: "BEE123"
8. Share code with others
9. Host can start quiz immediately
```

### Joining a Group
```
1. User clicks "🏆 Groups" menu option
2. Modal appears: "Create or Join Group?"
3. Click "Join Group"
4. Enter 6-digit code: "BEE123"
5. Enter player name
6. Click "Join"
7. See group info + leaderboard
8. Click "Start Quiz"
9. Begin spelling!
```

### During Quiz
```
- Player sees current word
- Player spells word
- Instant feedback (correct/incorrect)
- Score updates
- See current rank badge
- Continue to next word
- Leaderboard updates after each word
```

### After Completion
```
- Show final score
- Show final ranking
- Show detailed results
- Option to view leaderboard
- Option to play again
```

## 📊 Scoring System

### Base Points
- **Correct Answer:** 100 points
- **Incorrect Answer:** 0 points

### Speed Bonus (if answered quickly)
- **< 5 seconds:** +50 bonus
- **5-10 seconds:** +25 bonus
- **10-20 seconds:** +10 bonus
- **> 20 seconds:** 0 bonus

### Streak Multiplier
- **3+ correct in row:** 1.5x multiplier
- **5+ correct in row:** 2x multiplier
- **10+ correct in row:** 3x multiplier

### Example Calculation
```
Word 1: Correct in 4s = 100 + 50 = 150 points
Word 2: Correct in 6s = 100 + 25 = 125 points (streak: 2)
Word 3: Correct in 3s = (100 + 50) × 1.5 = 225 points (streak: 3!)
Total: 500 points
```

## 🗂️ File Structure

```
data/
  groups/
    BEE123.json      # Active group
    XYZ789.json      # Another group
  groups_archive/
    BEE123_20251016.json  # Completed/expired
```

## 🛠️ Backend Implementation

### New API Endpoints

#### 1. Create Group
```
POST /api/groups/create
Body: {
  "group_name": "Mrs. Smith's Class",
  "creator_name": "Mrs. Smith",
  "word_list_source": "current|upload|random",
  "difficulty": 3  // if random
}
Response: {
  "group_code": "BEE123",
  "group_id": "uuid...",
  "expires_at": "..."
}
```

#### 2. Join Group
```
POST /api/groups/join
Body: {
  "group_code": "BEE123",
  "player_name": "Alice"
}
Response: {
  "player_id": "uuid...",
  "group_info": {...},
  "word_count": 10
}
```

#### 3. Get Leaderboard
```
GET /api/groups/{group_code}/leaderboard
Response: {
  "players": [
    {
      "rank": 1,
      "name": "Alice",
      "score": 850,
      "completed": 8,
      "accuracy": 87.5
    }
  ]
}
```

#### 4. Update Progress
```
POST /api/groups/{group_code}/progress
Body: {
  "player_id": "uuid...",
  "word_index": 3,
  "is_correct": true,
  "elapsed_ms": 4500,
  "score": 150
}
Response: {
  "updated": true,
  "current_rank": 2,
  "leaderboard": [...]
}
```

#### 5. Get Group Info
```
GET /api/groups/{group_code}
Response: {
  "group_name": "...",
  "created_by": "...",
  "player_count": 5,
  "word_count": 10,
  "active_players": 3
}
```

## 🎨 Frontend Components

### 1. Groups Menu Card
```html
<div class="menu-option theme-competitive" onclick="selectOption('groups')">
  <div class="option-icon">🏆</div>
  <div class="option-title">Groups</div>
  <div class="option-description">Compete with friends!</div>
  <div class="kid-tip">👥 Multiplayer spelling fun!</div>
</div>
```

### 2. Group Modal
- Create or Join selector
- Code input for joining
- Group name input for creating
- Word source selector

### 3. Leaderboard Component
- Live updating list
- Player avatars/emojis
- Score displays
- Rank badges (🥇🥈🥉)
- Progress bars

### 4. Group Quiz Interface
- Standard quiz interface
- Leaderboard panel (collapsible)
- Rank indicator in corner
- Live score counter

## 🔒 Security Considerations

1. **Rate Limiting:** Max 5 group creates per hour per IP
2. **Code Validation:** 6 alphanumeric chars only
3. **Name Sanitization:** No special chars, max 30 chars
4. **Expiration:** Auto-delete after 24 hours
5. **Player Limit:** Max 50 players per group

## 📱 Mobile Considerations

- Responsive leaderboard (swipeable)
- Touch-friendly code input
- Compact score display
- Portrait/landscape support

## 🚀 Implementation Phases

### Phase 1: Basic MVP (2-3 hours)
- [x] Group creation with code generation
- [x] Join group functionality
- [x] Basic leaderboard
- [x] File-based storage
- [x] Simple scoring

### Phase 2: Enhanced Features (2-3 hours)
- [ ] Speed bonuses
- [ ] Streak multipliers
- [ ] Live updates (polling)
- [ ] Host controls
- [ ] Export results

### Phase 3: Polish (1-2 hours)
- [ ] Animations
- [ ] Sound effects
- [ ] Rank badges
- [ ] Achievement system
- [ ] Social sharing

## 🎯 Success Metrics

- Groups created per day
- Average players per group
- Completion rate
- Return rate (players joining multiple groups)
- Average session duration

## 💭 Future Enhancements

1. **Team Mode:** Players compete in teams
2. **Tournament Bracket:** Elimination style
3. **Practice Mode:** Join group without scoring
4. **Spectator Mode:** Watch without playing
5. **Voice Chat:** Built-in communication
6. **Replays:** Watch best performances
7. **Achievements:** Badges and awards
8. **Global Leaderboard:** Cross-group rankings

---

**Status:** Design Complete - Ready for Implementation
**Priority:** Medium-High (Great engagement feature)
**Complexity:** Medium (File-based) / High (Full database)
**Time Estimate:** 4-6 hours for MVP
