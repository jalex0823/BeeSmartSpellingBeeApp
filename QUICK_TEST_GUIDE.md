# 🧪 Quick Test: Retry Flow Manual Testing

## Setup
1. ✅ Open http://localhost:5000/quiz in browser
2. ✅ Open Developer Console (F12 → Console tab)
3. ✅ Wait for first word to load

## Test Procedure

### Step 1: Get First Word Wrong
1. **Look at** the word displayed in the quiz
2. **Type** a WRONG spelling (e.g., if word is "BICYCLE", type "BYCICLE")
3. **Press Enter** or click Submit

### Expected Result Step 1:
✅ **See TWO buttons appear immediately:**
- 🟢 "✅ Retry" (green button)
- 🔴 "❌ Show Answer" (red button)

✅ **Timer shows:** "Choosing in 10 seconds..."

✅ **NO correct answer shown yet** ← This is the key fix!

✅ **Console shows:**
```
⏱️ Starting 10-second choice countdown...
```

---

### Step 2: Click "Retry" Button
1. **Click** the green "✅ Retry" button BEFORE the 10 seconds expire
2. **Watch** what happens

### Expected Result Step 2:
✅ **Buttons DISAPPEAR immediately**

✅ **Input field ENABLED** with placeholder "Retry your spelling..."

✅ **20-second countdown timer appears** with message "⏱️ Time to Retry: 20"

✅ **NO correct answer shown** ← Still hidden!

✅ **Console shows:**
```
🟢 Retry button clicked
✅ User chose to RETRY
```

---

### Step 3: Type Wrong Answer Again During Retry
1. **Type** another WRONG spelling (can be same or different)
2. **Press Enter** to submit

### Expected Result Step 3:
✅ **NO retry button this time** ← Key difference!

✅ **Message shows:** "No problem! 📚 The correct spelling is: [WORD]"

✅ **"Next Word" button appears** (not Retry button)

✅ **Console shows:**
```
User chose INCORRECT - NO more retries (second attempt after retry)
```

---

## 🎯 What This Test Verifies

| Feature | Status |
|---------|--------|
| Choice buttons appear on first wrong | ✅ |
| No answer shown during choice period | ✅ |
| Retry button works | ✅ |
| 20-second retry input window appears | ✅ |
| No answer shown during retry typing | ✅ |
| Second wrong shows "no more retries" | ✅ |
| Only Next Word button shown (no retry) | ✅ |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Correct answer shows immediately | Check console for errors, reload page |
| Buttons don't respond to clicks | Open browser console (F12), check for JS errors |
| Timer doesn't countdown | Check if retryChoiceSeconds element exists |
| Retry button won't click | Check if buttons have the right IDs: retryChoiceYes, retryChoiceNo |

---

## ✅ Success Criteria

All of these must be TRUE:
- [ ] Choice buttons appear (not auto-answer)
- [ ] 10-second timer counts down
- [ ] Clicking Retry shows 20-second window
- [ ] No answer visible during retry
- [ ] Second wrong shows "no more retries"
- [ ] Console shows proper log messages
- [ ] Can advance to next word

---

**Test Started:** ___________  
**Result:** ☐ PASS ☐ FAIL  
**Notes:** _________________________________
