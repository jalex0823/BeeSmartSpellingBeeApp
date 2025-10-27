# ✅ Pre-Testing Checklist

## System Status Check

### Flask Server
- [ ] **Server Running:** `python AjaSpellBApp.py` is running
- [ ] **Port Accessible:** Can reach http://localhost:5000
- [ ] **No Errors:** Check terminal - no critical errors
- [ ] **Wiktionary Loaded:** Shows "✅ Loaded X words from Simple English Wiktionary"

### Browser Setup  
- [ ] **Quiz Page Loads:** http://localhost:5000/quiz shows quiz interface
- [ ] **No 404 Errors:** Page loads completely without network errors
- [ ] **Developer Tools Open:** F12 opens console successfully
- [ ] **Console Clear:** No errors visible before test

### Code Files
- [ ] **quiz.html Modified:** All retry choice code present
- [ ] **No Syntax Errors:** Linter errors are only template parsing (expected)
- [ ] **Functions Defined:** `startRetryChoiceCountdown`, `handleRetryChoiceYes`, `handleRetryChoiceNo` all exist
- [ ] **CSS Present:** `.retry-choice-btn`, `.retry-choice-timer` styles loaded

### Documentation Files Created
- [ ] **READY_FOR_TESTING.md** - Main test guide
- [ ] **QUICK_TEST_GUIDE.md** - Quick reference
- [ ] **RETRY_FIX_FINAL_SUMMARY.md** - Technical details
- [ ] **TEST_RETRY_FLOW_MANUAL.md** - Detailed steps
- [ ] **console_test.js** - Console helper

---

## Pre-Test Verification

### HTML Elements
```javascript
// Paste in console to verify:
console.log("retryChoiceYes:", !!document.getElementById('retryChoiceYes'));
console.log("retryChoiceNo:", !!document.getElementById('retryChoiceNo'));
console.log("retryChoiceTimer:", !!document.getElementById('retryChoiceTimer'));
console.log("feedbackArea:", !!document.getElementById('feedbackArea'));
console.log("spellingInput:", !!document.getElementById('spellingInput'));
```

Expected output: All should be **true**

### JavaScript Functions
```javascript
// Paste in console to verify:
console.log("startRetryChoiceCountdown:", typeof window.quizGameInstance?.startRetryChoiceCountdown);
console.log("handleRetryChoiceYes:", typeof window.quizGameInstance?.handleRetryChoiceYes);
console.log("handleRetryChoiceNo:", typeof window.quizGameInstance?.handleRetryChoiceNo);
console.log("startRetryInputWindow:", typeof window.quizGameInstance?.startRetryInputWindow);
console.log("showRetryInputExpired:", typeof window.quizGameInstance?.showRetryInputExpired);
```

Expected output: All should be **"function"**

---

## Quick System Check Commands

Run these in terminal:

```powershell
# Check Flask running
Get-Process python | Where-Object CommandLine -like "*AjaSpellBApp*"
# Expected: Returns Python process info

# Check port 5000 listening
netstat -ano | findstr :5000
# Expected: Shows LISTENING on port 5000
```

---

## Final Readiness Check

| Item | Status | Notes |
|------|--------|-------|
| Flask Server | ☐ Running | Check terminal |
| Quiz Page | ☐ Loading | http://localhost:5000/quiz |
| Console | ☐ Open | F12 to open |
| No Errors | ☐ Clean | Check console for red errors |
| HTML Ready | ☐ Present | Choice buttons exist |
| Functions | ☐ Defined | All 5 new functions present |
| Docs | ☐ Created | Test guides created |
| Timer CSS | ☐ Loaded | Styles working |
| Logging | ☐ Ready | console.log ready to debug |

---

## Go/No-Go Decision

### GO ✅ if:
- [ ] Flask server running without errors
- [ ] Quiz page loads completely
- [ ] Console shows no JavaScript errors
- [ ] All HTML elements present
- [ ] All functions defined
- [ ] Ready to spell words wrong!

### NO-GO ❌ if:
- [ ] Server won't start
- [ ] Quiz page shows 404
- [ ] JavaScript syntax errors in console
- [ ] Missing HTML elements
- [ ] Missing functions
- **→ Debug issues before testing**

---

## Test Start Confirmation

When ready to begin testing, confirm:

✅ I have verified the checklist above  
✅ Flask server is running  
✅ http://localhost:5000/quiz loads successfully  
✅ Console is open and ready  
✅ I'm ready to spell words wrong intentionally!  

Then proceed to **READY_FOR_TESTING.md** → "How to Test" section

---

**Remember:** The goal is to make the choice buttons appear WITHOUT showing the answer immediately. Watch carefully and use the console logs to verify the flow!

Let me know when you're ready! 🚀
