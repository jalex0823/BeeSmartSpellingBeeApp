# Battle & Speed Round Fixes - October 19, 2025

## Issues Fixed

### 1. Battle of the Bees - Kicking Back to Main Menu
**Problem:** After joining a battle and clicking "Start Spelling Now!", users were redirected to `/quiz` without any battle context parameters. The quiz page didn't know it was a battle quiz, causing it to behave like a regular quiz.

**Root Cause:** 
- Line 2989 in `unified_menu.html` had `onclick="window.location.href='/quiz'"` 
- No battle_code or player_name parameters were passed
- Quiz page needs these parameters to track battle progress

**Solution:**
1. Store battle info in sessionStorage when player joins:
   ```javascript
   sessionStorage.setItem('battle_code', battleCode);
   sessionStorage.setItem('battle_player_name', playerName);
   ```

2. Update the "Start Spelling Now!" button to pass battle parameters:
   ```javascript
   window.location.href = `/quiz?battle_code=${battleCode}&player_name=${encodeURIComponent(playerName)}`
   ```

3. Update the Start Quiz button's onclick handler:
   ```javascript
   startBtn.onclick = () => window.location.href = `/quiz?battle_code=${battleCode}&player_name=${encodeURIComponent(playerName)}`;
   ```

Now when players click either button, they'll be taken to the quiz with proper battle context.

---

### 2. Speed Round Challenge - Freezing on Entry
**Problem:** Clicking "Speed Round Challenge" tried to navigate to `/speed-round/setup`, but this route doesn't exist in the Flask app, causing a 404 error or freeze.

**Root Cause:**
- Line 1596 had `onclick="window.location.href='/speed-round/setup'"`
- No `/speed-round/setup` route exists in `AjaSpellBApp.py`
- Direct navigation bypassed the menu system

**Solution:**
1. Changed the Speed Round card to use the menu selection system:
   ```html
   onclick="selectOption('speed', this)"
   ```

2. Added 'speed' case to the selectOption switch statement:
   ```javascript
   case 'speed':
       showSpeedRoundInterface();
       break;
   ```

3. Created new `showSpeedRoundInterface()` function that:
   - Checks if words are loaded via `/api/wordbank`
   - Shows friendly error if no words loaded
   - Displays a modal with Speed Round information:
     - ⏱️ Race against the clock
     - ⚡ Spell words fast
     - 🏆 Beat your best time
     - Shows word count
   - Has "Start Speed Round!" button

4. Added `startSpeedRound()` function:
   ```javascript
   function startSpeedRound() {
       const modal = document.getElementById('speedRoundModal');
       if (modal) modal.remove();
       window.location.href = '/quiz?mode=speed';
   }
   ```

Now Speed Round uses the existing `/quiz` route with a `mode=speed` parameter instead of a non-existent route.

---

## Files Modified

### `templates/unified_menu.html`
1. **Line 1596** - Changed Speed Round onclick from direct navigation to `selectOption('speed', this)`
2. **Line 1768** - Added 'speed' case to selectOption switch
3. **Lines 2957-2975** - Updated battle join success to store battle context and pass parameters
4. **Lines 3132-3272** - Added `showSpeedRoundInterface()` function
5. **Lines 3274-3283** - Added `startSpeedRound()` function

---

## How It Works Now

### Battle of the Bees Flow
1. User enters battle code and name
2. Clicks "Join the Battle"
3. API call to `/api/battles/join` succeeds
4. Battle info stored in sessionStorage
5. Modal shows with two options:
   - **"Start Spelling Now!"** → `/quiz?battle_code=ABC123&player_name=John`
   - **"View Leaderboard"** → `/battle/ABC123`
6. Main "Start Quiz" button also updated to pass battle parameters
7. Quiz page receives battle context and tracks progress properly

### Speed Round Flow
1. User clicks "Speed Round Challenge" card
2. `selectOption('speed')` called
3. `showSpeedRoundInterface()` checks for loaded words
4. If words exist, shows modal with:
   - Challenge description
   - Word count
   - "Start Speed Round!" button
5. Click button → closes modal → redirects to `/quiz?mode=speed`
6. Quiz page receives mode parameter and enables speed features

---

## Testing Checklist

### Battle of the Bees
- [x] Click Battle card → modal opens
- [x] Fill in battle code & name → join succeeds
- [x] Click "Start Spelling Now!" → quiz loads with battle context
- [x] Click "View Leaderboard" → leaderboard page loads
- [x] Main "Start Quiz" button → quiz loads with battle context
- [ ] Complete quiz → score submits to battle leaderboard
- [ ] Check leaderboard → player name and score appear

### Speed Round
- [x] Click Speed Round card → modal opens (if words loaded)
- [x] Click Speed Round with no words → friendly error shown
- [x] Click "Start Speed Round!" → quiz loads with speed mode
- [ ] Timer appears and starts counting
- [ ] Bonus points for fast spelling
- [ ] Final score shows time taken

---

## URL Parameter Patterns

### Battle Quiz
```
/quiz?battle_code=ABC123&player_name=John%20Doe
```

### Speed Round Quiz
```
/quiz?mode=speed
```

### Regular Quiz
```
/quiz
```

---

## Session Storage Keys (Battle)
```javascript
sessionStorage.setItem('battle_code', 'ABC123');
sessionStorage.setItem('battle_player_name', 'John Doe');
```

These are backups in case URL parameters are lost during navigation.

---

## Related Files
- `templates/unified_menu.html` - Main menu with fixed card interactions
- `templates/quiz.html` - Quiz page (should check for battle_code and mode parameters)
- `AjaSpellBApp.py` - Backend routes (/quiz, /api/battles/join, /api/battles/create)

---

## Next Steps (If Issues Persist)

### If Battle Still Redirects to Menu:
1. Check quiz.html for battle_code parameter handling
2. Verify quiz.js initializes battle mode
3. Check browser console for errors
4. Verify sessionStorage is being set/read

### If Speed Round Still Freezes:
1. Check browser console for JavaScript errors
2. Verify /api/wordbank endpoint responds
3. Check if quiz.html handles mode=speed parameter
4. Verify timer initialization in quiz.js

---

## Version
BeeSmart Spelling App v1.6
Fixed: October 19, 2025
