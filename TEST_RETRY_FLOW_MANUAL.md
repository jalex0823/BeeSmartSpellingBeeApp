# ✅ Retry Flow Manual Test Guide

## Test Scenario: Verify Retry Button Prevents Auto-Correct

**Goal:** Ensure clicking "Retry" button prevents the correct answer from showing during the 20-second retry window.

---

## 📋 Pre-Test Checklist

- [ ] Flask server running on http://localhost:5000
- [ ] Browser console open (F12 → Console tab)
- [ ] No network errors
- [ ] Ready to type quickly

---

## 🎯 Test Steps

### Step 1: Start Quiz
1. Navigate to http://localhost:5000
2. Click "Quiz" or go directly to /quiz
3. Wait for first word to appear

### Step 2: First Incorrect Answer
1. See word displayed (e.g., "BICYCLE")
2. Deliberately spell it WRONG (e.g., type "BYCICLE")
3. Press Enter or click Next
4. **Expected Result:** 
   - ✅ Feedback message: "Not quite right..." or similar
   - ✅ Two buttons appear: "✅ Retry" and "❌ Show Answer"
   - ✅ 10-second countdown timer visible
   - ✅ **NO correct spelling shown yet**

**Console Check:**
```
✅ User chose INCORRECT - Retry available (first attempt)
```

### Step 3: Click "Retry" Button
1. Click the green "✅ Retry" button
2. **Expected Result:**
   - ✅ Choice buttons DISAPPEAR
   - ✅ Input field ENABLED with placeholder "Retry your spelling..."
   - ✅ Input field is FOCUSED (cursor ready)
   - ✅ Feedback area HIDDEN
   - ✅ 20-second countdown timer appears
   - ✅ **NO correct spelling shown**
   - ✅ Only the input field visible for typing

**Console Check:**
```
✅ User chose to RETRY
```

**Audio Check:**
- Should hear announcement: "You have 20 seconds to type your retry. Good luck!"

### Step 4: Attempt Retry (Wrong Again)
1. Type WRONG spelling again (e.g., "BYCICLE" again)
2. Press Enter
3. Wait for feedback
4. **Expected Result:**
   - ✅ **NO Retry button this time** ← KEY DIFFERENCE
   - ✅ Shows: "No problem! 📚 The correct spelling is: BICYCLE"
   - ✅ Shows "Next Word" button
   - ✅ **0 points awarded** (not 33%)
   - ✅ **Cannot retry again**

**Console Check:**
```
✅ User chose INCORRECT - NO more retries (second attempt after retry)
```

**Audio Check:**
- Should hear announcement: "The correct spelling is: B, I, C, Y, C, L, E"

### Step 5: Click "Next Word"
1. Click "Next Word" button
2. Should advance to next word in list
3. **Expected Result:** Quiz continues normally

---

## 🧪 Alternative Test: Click "Show Answer" First Time

1. Get first incorrect answer (same as Step 2)
2. **Instead of** clicking Retry, click "❌ Show Answer"
3. **Expected Result:**
   - ✅ Correct spelling shown immediately
   - ✅ "Next Word" button shown
   - ✅ 0 points awarded (no retry bonus)
   - ✅ **Cannot retry** - choice is final

---

## 🧪 Edge Case: Retry Timeout

1. Get first incorrect answer
2. Click "Retry" button
3. **DON'T type anything** for 20 seconds
4. **Expected Result:**
   - ✅ 20-second countdown reaches 0
   - ✅ Message: "Time's up! ⏰"
   - ✅ Correct spelling displayed
   - ✅ "Next Word" button shown

---

## 🐛 Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Correct answer shows immediately after clicking Retry | `isRetryAttempt` not set | Check console for errors, reload page |
| Retry button appears after 2nd wrong answer | `isRetryAttempt` not persisting | Check browser session state |
| Input field disabled during retry | `handleRetryChoiceYes()` not running | Check console for JavaScript errors |
| Buttons still visible during retry | `hideRetryButton()` failed | Check button element IDs |
| No countdown timer appears | `startRetryInputWindow()` not called | Check console logs |

---

## 📊 Expected Button States

| State | Retry Button | Show Answer Button | Next Word Button |
|-------|---|---|---|
| After 1st wrong answer | ✅ Visible | ✅ Visible | ❌ Hidden |
| During 20-sec retry | ❌ Hidden | ❌ Hidden | ❌ Hidden |
| After 2nd wrong answer | ❌ Hidden | ❌ Hidden | ✅ Visible |
| After correct retry | ❌ Hidden | ❌ Hidden | ✅ Visible |

---

## 🎯 Success Criteria (ALL must pass)

- [x] First incorrect answer shows choice buttons
- [x] Clicking "Retry" hides buttons
- [x] 20-second countdown shows during retry
- [x] **No correct answer shown during retry** ← KEY TEST
- [x] After retry timeout or 2nd wrong, "No more retries" message shows
- [x] Final message shows correct spelling
- [x] Can advance to next word
- [x] Console shows proper log messages
- [x] No JavaScript errors in console

---

## 🚀 When Test Passes

Once all criteria pass:
1. ✅ Mark tests as complete
2. ✅ Take screenshots
3. ✅ Commit changes
4. ✅ Deploy to Railway
5. ✅ Test in production

---

**Test Date:** ___________  
**Tester:** ___________  
**Result:** ☐ PASS ☐ FAIL  
**Notes:** _______________________________
