# 🐝 BeeSmart Points & Buzz Dust - Quick Reference

## For Students & Parents

### What Are Points? 🧠
- Your **school score** for spelling
- Used for grades and GPA
- Shows how well you spelled the words

### What Is Buzz Dust? ✨
- **Magic XP** you earn while learning
- Used for ranks, avatars, and badges
- Makes learning feel like a game

### How to Earn More Buzz Dust
1. **Answer correctly** - Base Buzz Dust from points
2. **Perfect round** - Get all words right (+25 bonus)
3. **No hints** - Spell without help (+10 bonus)
4. **Build streaks** - Keep answering correctly (up to +250!)
5. **Daily challenges** - Complete special quizzes (+50 bonus)

### Bee Class Ranks 🏆
- 🐝 **Novice Bee** - Just getting started (0+ Buzz Dust)
- 📚 **Apprentice Bee** - Learning the hive way (500+ Buzz Dust)
- 🎓 **Scholar Bee** - Dedicated learner (2,500+ Buzz Dust)
- 🏆 **Elite Bee** - Spelling champion (10,000+ Buzz Dust)
- 👑 **Magistrate Bee** - Hive leader (50,000+ Buzz Dust)
- ✨ **Buzz Dust Master** - Legendary hero (100,000+ Buzz Dust)

---

## For Developers

### Database Fields (User model)
```python
total_buzz_dust: int      # Cumulative XP
bee_class: str            # Current rank
last_rank_up_at: datetime # When last ranked up
current_streak: int       # Consecutive correct
longest_streak: int       # All-time best
```

### Core Functions
```python
from buzz_dust_helpers import (
    calculate_quiz_buzz_dust,  # Calculate Buzz Dust from quiz
    add_buzz_dust,             # Add to user total + check rank-up
    get_bee_class,             # Get rank from total
    get_rank_progress,         # Get progress to next rank
    get_leaderboard_data       # Get sorted leaderboard
)
```

### API Endpoints
- `GET /api/buzz-dust/info` - User's Buzz Dust info
- `GET /api/buzz-dust/leaderboard?limit=50&role=student` - Leaderboard
- `GET /api/check-rank-up` - Check for recent rank-up
- `GET /points-buzz-dust-explanation` - Explanation page

### Quick Integration
```python
# In quiz completion handler:
buzz_dust, breakdown = calculate_quiz_buzz_dust(
    points=100,
    perfect_round=True,
    no_hints=True,
    streak_length=10
)

rank_info = add_buzz_dust(current_user, buzz_dust)

if rank_info['ranked_up']:
    session['ranked_up'] = True
    session['old_class_id'] = rank_info['old_class']['id']
```

### UI Components
```html
<!-- Rank Progress Bar -->
{% include 'components/rank_progress_bar.html' %}

<!-- Enable Rank-Up Animation -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/rank_up_animation.css') }}">
<script src="{{ url_for('static', filename='js/rank_up_animation.js') }}"></script>
<body data-check-rank-up="true">
```

---

## Configuration (buzz_dust_config.json)

### Default Values
- **Multiplier**: 0.10 (10% of points → Buzz Dust)
- **Perfect Round Bonus**: +25
- **Daily Challenge Bonus**: +50
- **No Hint Bonus**: +10
- **Streak Bonuses**: 5 (+5), 10 (+15), 20 (+40), 50 (+100), 100 (+250)

### Rank Thresholds
```json
{
  "novice": 0,
  "apprentice": 500,
  "scholar": 2500,
  "elite": 10000,
  "magistrate": 50000,
  "master": 100000
}
```

---

## Common Scenarios

### Scenario 1: New Student
- Completes 5 quizzes (80 points each)
- Total Points: 400
- Base Buzz Dust: 40 (10% of 400)
- With bonuses: ~100 Buzz Dust
- **Rank: Novice Bee** (needs 500 for Apprentice)

### Scenario 2: Regular Practice
- Completes 20 quizzes over 2 weeks
- Average 90 points per quiz, some perfect rounds
- Total Buzz Dust: ~600
- **Rank: Apprentice Bee** ✅

### Scenario 3: Star Student
- Completes 100 quizzes
- High accuracy, many perfect rounds
- Long streaks (20+ correct)
- Total Buzz Dust: ~12,000
- **Rank: Elite Bee** 🏆

---

## Tips for Teachers

### Encouraging Engagement
1. **Show the explanation page** to students at start of year
2. **Celebrate rank-ups** in class
3. **Create friendly competitions** using leaderboards
4. **Reward Buzz Dust** milestones with real-world prizes
5. **Use both metrics** - Points for grades, Buzz Dust for effort

### Understanding the Data
- **High Points + Low Buzz Dust** = Talented student, needs more practice
- **Low Points + High Buzz Dust** = Hard worker, improving over time
- **Both High** = Ideal student! 🌟
- **Both Low** = Needs motivation or support

---

## Migration Checklist

- [ ] Run `python scripts\migrate_buzz_dust.py`
- [ ] Verify no errors in migration output
- [ ] Test explanation page loads
- [ ] Complete a test quiz and verify Buzz Dust awarded
- [ ] Check rank progress bar displays correctly
- [ ] Trigger rank-up and verify animation

---

## File Locations

| File | Purpose |
|------|---------|
| `models.py` | Database schema |
| `buzz_dust_helpers.py` | Core logic |
| `config/buzz_dust_config.json` | Configuration |
| `templates/points_buzz_dust_explanation.html` | Explanation screen |
| `templates/components/rank_progress_bar.html` | Rank widget |
| `static/js/rank_up_animation.js` | Animation logic |
| `static/css/rank_up_animation.css` | Animation styles |
| `scripts/migrate_buzz_dust.py` | Database migration |

---

**Need more info?** See `BUZZ_DUST_IMPLEMENTATION_GUIDE.md`

**Happy Buzzing! 🐝✨**
