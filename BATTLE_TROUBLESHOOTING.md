# 🏆 Battle of the Bees - Troubleshooting Guide

## Issue: "Start a Battle" Button Not Working

### What Should Happen

When you click "Start a Battle":
1. Modal popup appears with two tabs: "Start a Battle" and "Join the Battle"
2. You fill in:
   - **Battle Name** (e.g., "The Battle Royal")
   - **Your Name** (e.g., "Jeff" or "Mrs. Smith")
3. Click "⚔️ Create Battle!" button
4. System creates battle and shows you:
   - **Battle Code** (e.g., "BATTLE123")
   - Instructions to share with students
   - Button to view leaderboard

### Testing Steps (After Deployment)

Wait 2-3 minutes for Railway to deploy, then:

#### Step 1: Open Console
1. Press F12 to open Developer Tools
2. Click "Console" tab
3. Clear any existing logs (trash icon)

#### Step 2: Click Battle Option
1. Go to main menu
2. Click the "Battle of the Bees" card
3. **Check console** - Should see:
   ```
   selectOption called with type: battle
   ```

#### Step 3: Fill Out Form
1. Fill in "Battle Name": `Test Battle`
2. Fill in "Your Name": `Jeff`
3. Click "⚔️ Create Battle!" button

#### Step 4: Check Console Output
**Expected console logs:**
```
🎯 createBattle() called
Battle Name: Test Battle
Creator Name: Jeff
📡 Sending battle creation request...
📡 Response status: 200
📡 Response data: {status: 'success', battle_code: 'BATTLE...', ...}
```

**If you see errors, note them and share**

### Common Issues & Solutions

#### Issue 1: Modal Doesn't Appear
**Symptoms**: Click "Battle of the Bees", nothing happens

**Check:**
- Console for JavaScript errors
- Try refreshing page (Ctrl+R)
- Try different browser (Chrome/Edge)

**Console logs to look for:**
```
selectOption called with type: battle
```

#### Issue 2: "Create Battle" Button Does Nothing
**Symptoms**: Click button, nothing happens

**Check Console for:**
```
🎯 createBattle() called
Battle Name: [your input]
Creator Name: [your input]
```

**If you DON'T see these logs:**
- Button click isn't registering
- JavaScript error blocking execution
- Check for red error messages in console

**If you DO see these logs but it stops:**
- API request failed
- Check for network errors (Network tab)

#### Issue 3: "No Words in Session" Error
**Symptoms**: Error message: "Please upload or generate words first"

**Solution:**
1. Go back to main menu
2. Upload a word list first (CSV, TXT, or type words)
3. THEN try creating battle

**The Battle system uses your current word list!**

#### Issue 4: API Request Fails
**Symptoms**: Console shows error after request

**Check:**
- Network tab (F12 → Network)
- Look for `/api/battles/create` request
- Status should be 200
- If 400/500, check response for error message

### Battle Code System

#### ✅ YES - You Will Get a Battle Code!

When you successfully create a battle, you'll see:

```
┌──────────────────────────┐
│   🏆 Battle Created!     │
├──────────────────────────┤
│                          │
│  Your Battle Code is:    │
│                          │
│    BATTLE7X9K            │ ← This is what you share!
│                          │
│  📋 Share this code      │
│     with your students!  │
│                          │
│  ⏰ Battle lasts 24 hrs  │
│                          │
│  👀 View Leaderboard     │ ← Click to monitor
│                          │
└──────────────────────────┘
```

#### How to Share with Students

**Option 1: Give them the code**
- Students click "Join the Battle"
- Enter code: `BATTLE7X9K`
- Enter their name
- Start spelling!

**Option 2: Share direct link**
```
https://beesmartspellingbee.up.railway.app/battle/BATTLE7X9K
```

Students just click, enter name, and go!

### Battle Workflow

```
TEACHER (You):
├─ 1. Upload word list
├─ 2. Click "Battle of the Bees"
├─ 3. Click "Start a Battle"
├─ 4. Fill in details
├─ 5. Get BATTLE CODE
├─ 6. Share code with students
└─ 7. Monitor leaderboard

STUDENTS:
├─ 1. Click "Battle of the Bees"
├─ 2. Click "Join the Battle"
├─ 3. Enter BATTLE CODE
├─ 4. Enter their name
└─ 5. Start quiz!

REAL-TIME:
├─ Students answer words
├─ Scores update live
├─ Leaderboard shows rankings
└─ Export grades when done
```

### API Endpoints (For Reference)

The system uses these endpoints:
- `POST /api/battles/create` - Creates battle, returns code
- `POST /api/battles/join` - Students join with code
- `GET /api/battles/{code}/leaderboard` - View rankings
- `POST /api/battles/{code}/progress` - Track student progress

### Debugging Checklist

- [ ] Console shows `createBattle() called`
- [ ] Console shows battle name and creator name
- [ ] Console shows `Sending battle creation request...`
- [ ] Console shows `Response status: 200`
- [ ] Console shows response data with `battle_code`
- [ ] Modal appears with battle code
- [ ] Battle code is 6-10 characters (e.g., BATTLE7X9K)
- [ ] "View Leaderboard" button appears
- [ ] Can click to go to `/battle/{code}`

### If Still Not Working

**Collect this info:**
1. Full console logs (screenshot or copy-paste)
2. Network tab showing `/api/battles/create` request
3. Any red error messages
4. Browser you're using (Chrome, Edge, Safari, Firefox)
5. What happens when you click button (nothing, error, etc.)

**Then:**
- Share console logs with me
- I can pinpoint the exact issue
- We'll fix it!

### Expected Behavior Video Tutorial

**What you should see:**
1. ✅ Click "Battle of the Bees" → Modal appears
2. ✅ Fill in name and battle name
3. ✅ Click "Create Battle" → Loading animation
4. ✅ Success modal with BIG battle code
5. ✅ Button to view leaderboard
6. ✅ Click button → Go to `/battle/BATTLECODE`
7. ✅ See leaderboard page (empty at first)
8. ✅ Share code with students
9. ✅ Students join and appear on leaderboard
10. ✅ Live updates as they answer questions

---

## Quick Reference

**Battle Code Format**: `BATTLE` + random characters (e.g., `BATTLE7X9K`)
**Battle Duration**: 24 hours
**Word Limit**: Uses your current word list
**Student Limit**: Unlimited!
**Real-time**: Yes, leaderboard updates live
**Export**: Yes, can export grades as CSV/PDF

---

**Status**: Debugging logs deployed
**Next**: Test after 2-3 min deployment
**Report**: Share console logs if issues persist
