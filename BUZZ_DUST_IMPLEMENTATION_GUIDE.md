# Buzz Dust & Ranking System - Implementation Guide

## 🎯 Overview

The BeeSmart app now features a **dual scoring system**:
- **Points**: Academic scores for grades, GPA, and teacher reports
- **Buzz Dust**: Gamified XP for ranks, avatars, and leaderboards

This guide explains how to use and integrate the new system.

---

## 📁 Files Created

### Core System Files
1. **`models.py`** - Updated User model with Buzz Dust fields:
   - `total_buzz_dust` (Integer)
   - `bee_class` (String: novice, apprentice, scholar, elite, magistrate, master)
   - `last_rank_up_at` (DateTime)
   - `current_streak` (Integer)
   - `longest_streak` (Integer)

2. **`buzz_dust_helpers.py`** - Core calculation logic:
   - `get_bee_class(total_buzz_dust)` - Get current rank
   - `calculate_quiz_buzz_dust(points, ...)` - Calculate Buzz Dust from quiz
   - `add_buzz_dust(user, amount)` - Add Buzz Dust and check rank-up
   - `get_rank_progress(total_buzz_dust)` - Get progress toward next rank
   - `get_leaderboard_data(limit, role_filter)` - Get leaderboard

3. **`config/buzz_dust_config.json`** - Configuration:
   - Buzz Dust multiplier (default: 0.10 = 10% of points)
   - Bonuses (perfect round, streaks, speed, etc.)
   - Bee class thresholds
   - UI settings

### Templates
4. **`templates/points_buzz_dust_explanation.html`** - In-app explanation screen
5. **`templates/components/rank_progress_bar.html`** - Reusable rank progress component

### JavaScript & CSS
6. **`static/js/rank_up_animation.js`** - Rank-up celebration animation
7. **`static/css/rank_up_animation.css`** - Animation styles

### Migration
8. **`scripts/migrate_buzz_dust.py`** - Database migration script

### API Routes (in AjaSpellBApp.py)
9. `/api/buzz-dust/info` - Get user's Buzz Dust info
10. `/api/buzz-dust/leaderboard` - Get leaderboard
11. `/api/check-rank-up` - Check for recent rank-up
12. `/points-buzz-dust-explanation` - Explanation page

---

## 🚀 Getting Started

### Step 1: Run Database Migration

```powershell
cd c:\Temp\BeeSmartSpellingBeeApp
python scripts\migrate_buzz_dust.py
```

This adds the required columns to the `users` table.

### Step 2: Verify Configuration

Check `config/buzz_dust_config.json` and adjust thresholds/bonuses if needed:

```json
{
  "buzz_dust": {
    "multiplier": 0.10,
    "bonuses": {
      "perfect_round": 25,
      "daily_challenge": 50,
      "no_hint": 10,
      "streaks": {
        "5": 5,
        "10": 15,
        "20": 40
      }
    }
  }
}
```

### Step 3: Update Quiz Completion Logic

In your quiz result handler (e.g., after a quiz is completed), add:

```python
from buzz_dust_helpers import calculate_quiz_buzz_dust, add_buzz_dust

# Calculate Buzz Dust earned
buzz_dust, breakdown = calculate_quiz_buzz_dust(
    points=quiz_points,
    perfect_round=(correct_answers == total_questions),
    no_hints=(hints_used == 0),
    streak_length=current_user.current_streak,
    daily_challenge=False  # Set True if this is a daily challenge
)

# Add to user's total and check for rank-up
rank_info = add_buzz_dust(current_user, buzz_dust)

# Store rank-up info in session for animation
if rank_info['ranked_up']:
    session['ranked_up'] = True
    session['old_class_id'] = rank_info['old_class']['id']

# Include in response
return jsonify({
    'quiz_complete': True,
    'points': quiz_points,
    'buzz_dust_earned': buzz_dust,
    'buzz_dust_breakdown': breakdown,
    'ranked_up': rank_info['ranked_up']
})
```

---

## 🎨 UI Integration

### Show Rank Progress Bar

Add to any template (profile, dashboard, quiz results):

```html
{% if current_user.is_authenticated %}
  {% set rank_progress = get_rank_progress(current_user.total_buzz_dust or 0) %}
  {% include 'components/rank_progress_bar.html' %}
{% endif %}
```

You'll need to pass `rank_progress` from your route:

```python
from buzz_dust_helpers import get_rank_progress

@app.route('/profile')
@login_required
def profile():
    rank_progress = get_rank_progress(current_user.total_buzz_dust or 0)
    return render_template('profile.html', rank_progress=rank_progress)
```

### Enable Rank-Up Animation

Add to quiz results page or layout:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/rank_up_animation.css') }}">
<script src="{{ url_for('static', filename='js/rank_up_animation.js') }}"></script>

<!-- Set flag to auto-check for rank-up on page load -->
<body data-check-rank-up="true">
```

### Link to Explanation Page

Add a menu item or help button:

```html
<a href="{{ url_for('points_buzz_dust_explanation') }}">
  ✨ How Points & Buzz Dust Work
</a>
```

---

## 📊 Bee Class Ranks

| Rank | Label | Min Buzz Dust | Emoji |
|------|-------|---------------|-------|
| 1 | Novice Bee | 0 | 🐝 |
| 2 | Apprentice Bee | 10,000 | 📚 |
| 3 | Scholar Bee | 50,000 | 🎓 |
| 4 | Elite Bee | 200,000 | 🏆 |
| 5 | Magistrate Bee | 1,000,000 | 👑 |
| 6 | Buzz Dust Master | 2,000,000 | ✨ |

---

## 🔧 API Usage Examples

### Get User's Buzz Dust Info

```javascript
fetch('/api/buzz-dust/info')
  .then(res => res.json())
  .then(data => {
    console.log('Total Buzz Dust:', data.total_buzz_dust);
    console.log('Current Class:', data.current_class.label);
    console.log('Progress:', data.progress_percent + '%');
  });
```

### Get Leaderboard

```javascript
fetch('/api/buzz-dust/leaderboard?limit=50&role=student')
  .then(res => res.json())
  .then(data => {
    data.leaderboard.forEach(entry => {
      console.log(`#${entry.rank}: ${entry.display_name} - ${entry.total_buzz_dust} Buzz Dust`);
    });
  });
```

### Check for Rank-Up (after quiz)

```javascript
fetch('/api/check-rank-up')
  .then(res => res.json())
  .then(data => {
    if (data.ranked_up) {
      // Trigger animation
      window.rankUpAnimator.trigger(
        data.old_class,
        data.new_class,
        data.total_buzz_dust
      );
    }
  });
```

---

## 🧪 Testing

### Manual Testing Checklist

1. **Run Migration**: ✅ No errors, all columns added
2. **Complete Quiz**: ✅ Buzz Dust awarded, displayed correctly
3. **Check Rank Progress**: ✅ Progress bar shows correct percentage
4. **Rank Up**: ✅ Animation triggers when crossing threshold
5. **Leaderboard**: ✅ Shows users sorted by Buzz Dust
6. **Explanation Page**: ✅ Loads with all 6 Bee Classes

### Test Script

```python
# Test Buzz Dust calculation
from buzz_dust_helpers import calculate_quiz_buzz_dust, get_bee_class

# Perfect quiz with 100 points
dust, breakdown = calculate_quiz_buzz_dust(
    points=100,
    perfect_round=True,
    no_hints=True,
    streak_length=10
)

print(f"Buzz Dust: {dust}")
print(f"Breakdown: {breakdown}")

# Test rank determination
bee_class = get_bee_class(50000)
print(f"At 50,000 Buzz Dust: {bee_class['label']}")  # Should be "Scholar Bee"
```

---

## 📚 Key Concepts

### Points vs Buzz Dust

**Points**:
- Academic metric
- Used for: Grades, GPA, teacher reports
- Calculated from: Correct answers, difficulty, quiz length
- **NOT affected by**: Streaks, speed, game progression

**Buzz Dust**:
- Gamification metric
- Used for: Ranks, avatars, leaderboards, badges
- Calculated from: Points × multiplier + bonuses
- **Affected by**: Perfect rounds, streaks, speed, daily challenges

### Independence

- High Points + Low Buzz Dust = Great student, few quizzes taken
- High Buzz Dust + Mixed Points = Lots of practice, improving
- Both High = Star performer! 🌟

---

## 🎯 Next Steps

### Recommended Enhancements

1. **Update Quiz Results Template**: Show Buzz Dust breakdown
2. **Add Leaderboard Page**: Display top students by Buzz Dust
3. **Profile Page**: Show rank progress prominently
4. **Daily Challenges**: Award bonus Buzz Dust
5. **Achievements**: Unlock badges at rank milestones
6. **Avatar Unlocks**: Require certain Bee Classes for premium avatars

### Example: Update Quiz Results

```html
<!-- quiz_results.html -->
<div class="quiz-results">
  <h2>Quiz Complete!</h2>
  
  <div class="score-section">
    <h3>📊 Academic Score</h3>
    <p class="points">{{ points }} / {{ max_points }} Points</p>
    <p class="grade">Grade: {{ grade }}</p>
  </div>
  
  <div class="buzz-dust-section">
    <h3>✨ Buzz Dust Earned</h3>
    <p class="dust-total">+{{ buzz_dust_earned }} Buzz Dust</p>
    
    <div class="dust-breakdown">
      {% if buzz_dust_breakdown.base %}
        <span>Base: +{{ buzz_dust_breakdown.base }}</span>
      {% endif %}
      {% if buzz_dust_breakdown.perfect_round %}
        <span>Perfect Round: +{{ buzz_dust_breakdown.perfect_round }}</span>
      {% endif %}
      {% if buzz_dust_breakdown.streak %}
        <span>Streak Bonus: +{{ buzz_dust_breakdown.streak }}</span>
      {% endif %}
    </div>
  </div>
  
  <div class="rank-progress">
    {% include 'components/rank_progress_bar.html' %}
  </div>
</div>
```

---

## 🐛 Troubleshooting

### "Column does not exist" errors
**Solution**: Run `python scripts\migrate_buzz_dust.py`

### Buzz Dust not calculating
**Solution**: Check that you're calling `calculate_quiz_buzz_dust()` and `add_buzz_dust()` in quiz completion

### Rank-up animation not showing
**Solution**: 
1. Include CSS and JS files in template
2. Set `data-check-rank-up="true"` on body
3. Ensure session has `ranked_up` flag

### Config not loading
**Solution**: Verify `config/buzz_dust_config.json` exists and is valid JSON

---

## 📞 Support

For questions or issues:
1. Check this documentation
2. Review `buzz_dust_helpers.py` docstrings
3. Test with `python scripts\migrate_buzz_dust.py --verify`

---

**Happy Buzzing! 🐝✨**
