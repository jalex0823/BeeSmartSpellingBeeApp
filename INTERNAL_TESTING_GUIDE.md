# 🐝 BeeSmart Spelling Bee - Internal Testing Guide

**Version:** 2.0 (Version Code 2)  
**Testing Phase:** Internal Testing  
**Last Updated:** November 3, 2025

---

## 📱 How to Join the Test

### Step 1: Get the Testing Link
1. The testing coordinator will send you a Google Play testing link
2. Link format: `https://play.google.com/apps/internaltest/...`
3. **Important:** You must use the same Gmail account that was added to the tester list

### Step 2: Opt-In to Testing
1. Click the testing link on your Android device (or computer)
2. Click **"Become a tester"** button
3. Accept the terms and conditions
4. Wait a few minutes for activation (usually instant)

### Step 3: Download the App
1. Once opted in, click **"Download it on Google Play"**
2. Or search for **"BeeSmart Spelling Bee"** in Google Play Store
3. Install the app (should show "Internal test" label)
4. Open and start testing!

---

## 🎯 What to Test

### Priority 1: Core Functionality ⭐⭐⭐

#### 1. **Word Upload System**
- [ ] **Text File Upload**
  - Try uploading a .txt file with word lists
  - Expected format: One word per line, or "word, sentence, hint"
  - Test with 10, 50, and 100+ word lists
  - ✅ **Success:** Words appear in quiz
  - ❌ **Bug:** File rejected, words missing, app crashes

- [ ] **Image OCR Upload** (if available)
  - Upload a clear image with printed text
  - Try handwritten text (lower accuracy expected)
  - ✅ **Success:** Text extracted and words loaded
  - ❌ **Bug:** No words extracted, app crashes

- [ ] **Manual Word Entry**
  - Enter words one at a time through the UI
  - ✅ **Success:** Words saved and appear in quiz
  - ❌ **Bug:** Words don't save, UI freezes

#### 2. **Quiz Modes**
- [ ] **Magical Quiz**
  - Start a quiz with uploaded words
  - Try voice input (tap microphone icon)
  - Try keyboard input
  - Use hint button
  - Use pronounce button (hear the word)
  - Complete entire quiz
  - ✅ **Success:** Smooth flow, points awarded, progress saved
  - ❌ **Bug:** Crashes mid-quiz, points not saved, audio issues

- [ ] **Speed Round**
  - Start a speed round quiz
  - Test under time pressure
  - ✅ **Success:** Timer works, bonus points for speed
  - ❌ **Bug:** Timer freezes, no speed bonuses

#### 3. **Points & Progression**
- [ ] Earn honey points by completing quizzes
- [ ] Check points display in dashboard
- [ ] Verify level progression (Busy Bee → Flower Flyer → Honey Collector → Spelling Star → Word Wizard → Queen Bee)
- [ ] Earn badges (Perfect Game, Speed Demon, Hot Streak, etc.)
- [ ] ✅ **Success:** Points accumulate, levels unlock, badges appear
- [ ] ❌ **Bug:** Points reset, levels don't unlock, badges missing

#### 4. **Avatar System**
- [ ] **Avatar Selection**
  - Open avatar picker (honeycomb layout)
  - Try selecting different avatars
  - Verify preview shows correctly
  - Save avatar selection
  - Check avatar appears in dashboard

- [ ] **Avatar Unlocking**
  - Complete quizzes to earn points
  - Check if new avatars unlock at point thresholds
  - Look for unlock notification popup
  - ✅ **Success:** Avatars unlock, notification appears, 3D model loads
  - ❌ **Bug:** Avatars stay locked, no notification, 3D model broken

### Priority 2: Authentication & User Management ⭐⭐

#### 5. **Registration**
- [ ] Create a new account (student role)
- [ ] Try with/without email
- [ ] Select starting avatar
- [ ] ✅ **Success:** Account created, auto-logged in, avatar saved
- [ ] ❌ **Bug:** Registration fails, no redirect, avatar not saved

#### 6. **Login**
- [ ] Log out and log back in
- [ ] Try "Remember me" checkbox
- [ ] Test wrong password (should fail gracefully)
- [ ] ✅ **Success:** Login works, session persists
- [ ] ❌ **Bug:** Can't log in, session expires immediately

#### 7. **Password Reset**
- [ ] Click "Forgot password"
- [ ] Enter email/username
- [ ] Check email for reset link (may take a few minutes)
- [ ] Click link and set new password
- [ ] Log in with new password
- [ ] ✅ **Success:** Reset email received, password changed
- [ ] ❌ **Bug:** No email received, reset link doesn't work

#### 8. **Dashboards**
- [ ] **Student Dashboard**
  - View quiz history
  - Check accuracy stats
  - See struggling words
  - Browse badge collection
  - View level progress

- [ ] **Teacher/Parent Dashboard** (if applicable)
  - View linked students
  - Check class statistics
  - Export reports

### Priority 3: Cross-Device & Performance ⭐

#### 9. **Device Compatibility**
- [ ] Test on phone (small screen)
- [ ] Test on tablet (large screen)
- [ ] Test on different Android versions (if possible)
- [ ] Rotate device (portrait ↔ landscape)
- [ ] ✅ **Success:** Layout adapts, no UI breaks
- [ ] ❌ **Bug:** UI overlaps, text cut off, crashes on rotation

#### 10. **Performance**
- [ ] App startup time (should be < 3 seconds)
- [ ] Avatar 3D model loading (should be < 5 seconds)
- [ ] Quiz transitions (should be smooth)
- [ ] Large word list handling (100+ words)
- [ ] ✅ **Success:** Fast and responsive
- [ ] ❌ **Bug:** Slow loading, lag, freezing

---

## 🐛 How to Report Issues

### When You Find a Bug:
1. **Take a screenshot** (Power + Volume Down on most Android devices)
2. **Note the exact steps** to reproduce:
   - What were you doing?
   - What button did you tap?
   - What happened vs. what should have happened?

3. **Collect device info:**
   - Device model (e.g., Samsung Galaxy S23, Pixel 7)
   - Android version (Settings → About phone)
   - App version (should be version code 2)

4. **Send report to:** [Your email or feedback form URL]

### Bug Report Template:
```
📱 Device: [Samsung Galaxy S23]
📋 Android Version: [13]
🐝 App Version: [2.0 (2)]

🐛 Bug Description:
[What went wrong?]

🔄 Steps to Reproduce:
1. [First I did this...]
2. [Then I tapped this...]
3. [Then this happened...]

📸 Screenshot:
[Attach screenshot if available]

💬 Additional Notes:
[Anything else that might help?]
```

---

## ✅ Testing Checklist Summary

Quick checklist for complete testing coverage:

**Core Features:**
- [ ] Upload words (text file, manual entry, OCR)
- [ ] Complete magical quiz
- [ ] Complete speed round quiz
- [ ] Earn points and badges
- [ ] Select and unlock avatars

**User Flow:**
- [ ] Register new account
- [ ] Log in/out
- [ ] Password reset
- [ ] View dashboards

**Quality:**
- [ ] Test on different screen sizes
- [ ] Check performance/speed
- [ ] Verify no crashes
- [ ] Confirm data persists after closing app

---

## 📞 Support & Questions

**Having trouble?**
- Email: [your-email@example.com]
- Test coordinator: Jeff Alexander

**Google Play Console:**
- [Link to your Play Console if you want testers to see crash reports]

---

## 🎉 Thank You for Testing!

Your feedback is invaluable! Every bug you find helps make BeeSmart better for students everywhere. 

**Expected testing timeline:**
- Internal testing: 1-2 weeks
- Bug fixes and updates
- Open testing (wider release)
- Production launch

---

## 🔍 Known Issues

*(Update this section as issues are discovered and fixed)*

### Currently Known:
- Deobfuscation file warning (not critical - stack traces are readable)
- [Add any other known issues here]

### Fixed in This Version:
- Avatar preview text contrast improved
- Thumbnail validation automated
- [Add other fixes from previous versions]

---

**Happy Testing! 🐝✨**
