# 🧪 BeeSmart Manual Testing Guide

## ✅ Server Status
**Flask Server Running:** http://127.0.0.1:5000

---

## 🎯 Test Plan Overview

We'll test 3 critical flows:
1. **Logged-In User Flow** (Database saves)
2. **Guest Mode Flow** (Session-based, no database)
3. **Teacher Dashboard Flow** (View students)

---

## 📋 Test Flow 1: Logged-In User (NEW USER)

### Step 1: Registration
1. Open browser: http://127.0.0.1:5000
2. Click **"Sign In"** or **"Register"** button
3. Or go directly to: http://127.0.0.1:5000/auth/register
4. Fill in form:
   - Username: `test_user_123` (or any unique name)
   - Display Name: `Test User`
   - Password: `test123`
   - Grade Level: `5th Grade` (optional)
   - Teacher Key: Leave blank (or use `BEE-2025-SMITH-XXXX` to link to teacher)
5. Click **"Create Account"**
6. Should redirect to: http://127.0.0.1:5000/auth/dashboard

**Expected Result:**
- ✅ Registration successful
- ✅ Auto-logged in
- ✅ Redirected to student dashboard
- ✅ Dashboard shows: "Welcome, Test User!"
- ✅ Stats show all zeros (new user)

---

### Step 2: Start Quiz
1. From dashboard, click **"🚀 Start New Quiz"**
2. Or go to: http://127.0.0.1:5000
3. Should see default 50 words loaded
4. Click **"Start Quiz"** button

**Expected Result:**
- ✅ Quiz starts
- ✅ Word definition appears
- ✅ Timer starts (honey jar drains)
- ✅ Voice announcement plays

**Check Backend (Database):**
```bash
# Open new terminal:
python init_db.py check
```
- Should show **1 new QuizSession** created
- `completed: False`

---

### Step 3: Answer Words
1. Listen to word and definition
2. Type the word in input box
3. Click **"Submit"** or press **Enter**
4. Repeat for at least 5-10 words
5. Try to get some correct and some wrong

**Expected Result:**
- ✅ Correct answers: Green message, points animation
- ✅ Incorrect answers: Orange message, shows correct spelling
- ✅ Points accumulate (check honey pot)
- ✅ Progress bar updates

---

### Step 4: Complete Quiz
1. Continue answering all 50 words (or click "Exit Quiz" after 10+)
2. If exit early, you'll see progress summary
3. If complete all words, you'll see final results

**Expected Result:**
- ✅ Final score displayed
- ✅ Grade shown (A, B, C, etc.)
- ✅ Accuracy percentage calculated
- ✅ Total points awarded

**Check Backend (Database):**
```bash
python init_db.py check
```
- QuizSession: `completed: True`
- QuizSession: `grade: A` (or B, C, etc.)
- QuizSession: `total_points: 1500+`
- QuizResult: Should have 10+ records
- WordMastery: Should have records for each word attempted

---

### Step 5: View Dashboard
1. Go to: http://127.0.0.1:5000/auth/dashboard
2. Refresh page if needed

**Expected Result:**
- ✅ Total Points updated (should match quiz points)
- ✅ Quizzes Completed: 1
- ✅ Average Accuracy: Shows percentage
- ✅ Recent Quiz History table shows your quiz
- ✅ Words to Practice section may show struggling words

---

### Step 6: Take Another Quiz (Optional)
1. Click **"Start New Quiz"** from dashboard
2. Complete another quiz
3. Check dashboard again

**Expected Result:**
- ✅ Quizzes Completed: 2
- ✅ Total Points increased
- ✅ History shows both quizzes
- ✅ Word mastery updates

---

## 📋 Test Flow 2: Guest Mode (No Login)

### Step 1: Open Incognito/Private Browser
1. Open **Incognito** window (Chrome: Ctrl+Shift+N)
2. Go to: http://127.0.0.1:5000
3. Should see main menu

**Expected Result:**
- ✅ No login prompt
- ✅ Can access all features
- ✅ No database saves

---

### Step 2: Complete Quiz as Guest
1. Upload word list or use defaults
2. Start quiz
3. Complete 10+ words
4. Check final results

**Expected Result:**
- ✅ Quiz works perfectly
- ✅ Points calculated
- ✅ No errors
- ✅ No prompt to login

**Check Backend (Database):**
```bash
python init_db.py check
```
- QuizSession count: **Should NOT increase** (guest mode)
- QuizResult count: **Should NOT increase** (guest mode)

---

### Step 3: Verify Session Storage
1. Open browser DevTools (F12)
2. Go to: Application → Cookies → http://127.0.0.1:5000
3. Should see session cookie

**Expected Result:**
- ✅ Session cookie exists
- ✅ Quiz data stored in Flask session (not database)
- ✅ Refresh page: quiz state persists

---

## 📋 Test Flow 3: Teacher Dashboard

### Step 1: Login as Teacher
1. Open browser: http://127.0.0.1:5000/auth/login
2. Login with:
   - Username: `teacher_smith`
   - Password: `teacher123`
3. Should redirect to: http://127.0.0.1:5000/teacher/dashboard

**Expected Result:**
- ✅ Teacher dashboard loads
- ✅ Shows Teacher Key: `BEE-2025-SMITH-XXXX`
- ✅ Class stats: 2 students (alex_student, sara_student)
- ✅ Student list table shows both students

---

### Step 2: Test Teacher Key Copy
1. Click **"📋 Copy"** button next to Teacher Key
2. Paste somewhere (Notepad, etc.)

**Expected Result:**
- ✅ Button shows "✅ Copied!"
- ✅ Key copied to clipboard
- ✅ Button reverts to "📋 Copy" after 2 seconds

---

### Step 3: Test Student Search
1. Type in search box: "alex"
2. Only alex_student should show
3. Clear search, both students reappear

**Expected Result:**
- ✅ Search filters in real-time
- ✅ Case-insensitive
- ✅ Shows matching students only

---

### Step 4: View Student Details
1. Click **"View Details"** for alex_student
2. Should go to: http://127.0.0.1:5000/teacher/student/3

**Expected Result:**
- ⚠️ **NOTE:** This page may not exist yet (Phase 5 feature)
- If 404: This is expected, we'll build it next
- If loads: Check it shows student's quiz history

---

### Step 5: Add New Student to Class
1. Register a new student account with Teacher Key
2. Go to: http://127.0.0.1:5000/auth/register
3. Enter teacher key: `BEE-2025-SMITH-XXXX` (copy from teacher dashboard)
4. Complete registration
5. Go back to teacher dashboard

**Expected Result:**
- ✅ New student appears in teacher's student list
- ✅ Total students count increased
- ✅ Student linked automatically

---

## 🐛 Common Issues & Solutions

### Issue 1: Database Not Saving
**Symptoms:** Dashboard shows zeros, no quiz history

**Check:**
```bash
python init_db.py check
# Should show QuizSession and QuizResult records
```

**Solution:**
1. Check user is logged in (top right shows username)
2. Verify database file exists: `beesmart.db`
3. Check terminal for errors

---

### Issue 2: Server Crashes
**Symptoms:** Page won't load, connection refused

**Solution:**
```bash
# Stop server (Ctrl+C in terminal)
# Restart:
python AjaSpellBApp.py
```

---

### Issue 3: Guest Mode Errors
**Symptoms:** Errors when not logged in

**Solution:**
- Check browser console (F12 → Console)
- Look for JavaScript errors
- Verify no "login required" messages

---

### Issue 4: Dashboard Not Updating
**Symptoms:** Stats don't change after quiz

**Solution:**
1. Hard refresh page (Ctrl+Shift+R or Cmd+Shift+R)
2. Check database:
   ```bash
   python init_db.py check
   ```
3. Verify quiz was completed (check terminal logs)

---

## ✅ Success Criteria

After completing all tests, you should have:

### Database Records:
- [ ] At least 1 QuizSession (completed: True)
- [ ] 10+ QuizResult records
- [ ] 10+ WordMastery records
- [ ] 1+ new User (your test account)
- [ ] 1+ TeacherStudent link (if used teacher key)

### Functional Tests:
- [ ] Can register and login
- [ ] Can complete quiz while logged in
- [ ] Dashboard shows quiz results
- [ ] Guest mode works without login
- [ ] Teacher dashboard shows students
- [ ] Teacher key copy works
- [ ] Search/filter works

### UI Tests:
- [ ] No JavaScript errors in console
- [ ] All animations work (timer, bees, points)
- [ ] Mobile responsive (test on phone or resize browser)
- [ ] Voice announcements play

---

## 📊 Verification Commands

### Check Database:
```bash
python init_db.py check
```

### Query Specific Data:
```python
# Open Python shell:
python

# Import models:
from models import db, User, QuizSession, QuizResult
from AjaSpellBApp import app

# Check data:
with app.app_context():
    # All users
    users = User.query.all()
    print(f"Users: {len(users)}")
    
    # All quiz sessions
    sessions = QuizSession.query.all()
    print(f"Quiz Sessions: {len(sessions)}")
    
    # Recent sessions
    recent = QuizSession.query.order_by(QuizSession.session_start.desc()).limit(5).all()
    for s in recent:
        print(f"Session {s.id}: Grade {s.grade}, Points {s.total_points}")
    
    # User's quizzes
    user = User.query.filter_by(username='test_user_123').first()
    if user:
        print(f"User: {user.display_name}")
        print(f"Quizzes: {user.total_quizzes_completed}")
        print(f"Points: {user.total_lifetime_points}")
```

---

## 🎯 What to Test Next Session

After manual testing passes, we'll implement:

### Phase 4: Achievement System
- [ ] Define 9 achievement types
- [ ] Add `check_achievements()` function
- [ ] Create Achievement records when unlocked
- [ ] Display badges on student dashboard
- [ ] Show notifications: "🎉 Achievement Unlocked!"

### Phase 5: Enhanced Teacher Features
- [ ] Student detail page (`/teacher/student/<id>`)
- [ ] CSV export for class data
- [ ] PDF report generation
- [ ] Email reports to parents
- [ ] Custom word list management

---

## 💡 Testing Tips

1. **Keep DevTools Open (F12)**
   - Monitor Console for errors
   - Check Network tab for failed requests
   - Use Application tab to inspect cookies/sessions

2. **Test in Multiple Browsers**
   - Chrome (primary)
   - Firefox
   - Safari (if on Mac)
   - Edge

3. **Test Mobile**
   - Resize browser to phone size (F12 → Toggle Device Toolbar)
   - Or test on actual phone at: http://192.168.7.233:5000

4. **Document Bugs**
   - Screenshot the issue
   - Note steps to reproduce
   - Check browser console for errors
   - Check server terminal for errors

---

## 🐝 Happy Testing! Let's Make Sure Everything Buzzes Smoothly! 🚀
