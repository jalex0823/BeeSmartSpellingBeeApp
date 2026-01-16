# TestFlight Testing Checklist - Build 46/46

**Priority:** 🔴 CRITICAL - Multiple critical fixes require testing

---

## 🔴 CRITICAL: IAP Purchase & Entitlements (TEST FIRST)

**Issue Fixed:** Purchases complete but avatars remain locked (broken in build 45, fixed in 46)

**Test Steps:**
1. Launch app → Main menu → Tap "Avatars" tile
2. Find locked avatar (BK Bee, Firefighter Bee, or any premium)
3. Tap locked avatar → Purchase button appears
4. Complete purchase in sandbox
5. ✅ **CRITICAL:** Verify avatar unlocks immediately
6. ✅ **CRITICAL:** Verify avatar stays unlocked after app restart
7. Test "Restore Purchases" → Verify previously purchased avatars restore
8. Test guest purchase (no login) → Verify purchase works without account
9. Try purchasing same avatar twice → Verify duplicate prevented

**Success:** All purchases unlock avatars immediately and persist

---

## 🔴 CRITICAL: BK Bee & Firefighter Bee Avatars

**New Avatars Added**

**Test:**
- Verify both avatars appear in picker
- Test purchase: BK Bee ($1.99) and Firefighter Bee ($1.99)
- Test Honey Points unlock: 30,000 points each
- Verify 3D models and thumbnails load correctly
- Product IDs: `beesmart.avatar.bk_bee` and `beesmart.avatar.firefighter_bee`

---

## 🟡 HIGH: Quiz Stats Accumulation

**Issue Fixed:** Quiz stats not accumulating after completion

**Test Steps:**
1. Complete a quiz (answer all questions)
2. View report card → Verify stats displayed
3. Return to main menu → Verify stats update
4. ✅ Verify `total_lifetime_points` increases
5. ✅ Verify `total_quizzes_completed` increases
6. ✅ Verify `cumulative_gpa` and `average_accuracy` update
7. Complete 3-5 quizzes → Verify stats accumulate (not reset)
8. Close and reopen app → Verify stats persist

**Success:** Stats accumulate after each quiz and persist

---

## 🟡 HIGH: Login & Session

**Issue Fixed:** 500 error on login

**Test:**
- Login with existing account → Verify no 500 errors
- Verify login completes successfully
- Verify user stats display correctly
- Test logout/login cycle → Verify session persists

---

## 🟢 MEDIUM: Speed Round

**Test:**
- Start Speed Round → Verify no timeout issues
- Complete Speed Round → Verify points/currency awarded
- Verify elite_buzz_dust awarded (if applicable)

---

## 🟢 LOW: UI/UX

**Test:**
- Main menu → "Avatars" tile visible and works
- Quiz → Honey Hint letter pattern works
- Export/Import buttons hidden (as intended)

---

## 📋 Quick Test Scenarios

**Scenario 1: New User First Purchase**
1. Fresh install → Launch → Don't login
2. Navigate to Avatars → Purchase BK Bee or Firefighter Bee
3. Expected: Avatar unlocks immediately

**Scenario 2: Restore Purchases**
1. Login → Tap "Restore Purchases"
2. Expected: Previously purchased avatars restore

**Scenario 3: Stats Accumulation**
1. Complete 3 quizzes → Check stats after each
2. Expected: Stats increase with each quiz
3. Close/reopen app → Expected: Stats persist

---

## ✅ Pre-Submission Checklist

- [ ] IAP purchases unlock avatars correctly
- [ ] Restore purchases works
- [ ] Guest purchases work
- [ ] Quiz stats accumulate correctly
- [ ] Stats persist after app restart
- [ ] Login works without 500 errors
- [ ] BK Bee and Firefighter Bee accessible
- [ ] No crashes or critical errors

---

## 🐛 Report Issues With:

1. Issue description
2. Steps to reproduce
3. Expected vs actual behavior
4. Device/OS info
5. Screenshots (if applicable)
6. Build: 46/46

---

**Priority Order:**
1. 🔴 IAP Purchase & Entitlements (TEST FIRST)
2. 🟡 Quiz Stats
3. 🟡 Login/Session
4. 🟢 Other Features

**Build:** 46/46 | **Date:** January 16, 2025
