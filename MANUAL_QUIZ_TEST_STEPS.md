"""
Manual Quiz Flow Test Steps
============================

Complete this flow manually in the browser:

1. Open: http://localhost:5000

2. Import Words:
   - Click "Manual Entry" or "Text File" button
   - Enter these words:
     * apple - I ate an apple - A red fruit
     * banana - The banana is yellow - A yellow fruit  
     * cat - The cat sleeps - A pet

3. Start Quiz:
   - Click "Start Quiz" button
   - Verify quiz page loads

   Timer Check (60s)
   - On the quiz page, verify the honey-jar countdown appears and starts at **60**
   - Let it run for a few seconds and confirm the number decreases (59, 58, ...)
   - Confirm the honey fill level visibly drops as time counts down

4. Answer Questions:
   - Type each word correctly
   - Check feedback after each answer
   - Note points earned

5. Complete Quiz:
   - Answer all 3 questions
   - Verify quiz completion message

6. View Report Card:
   - Check accuracy percentage
   - Verify total points
   - Check grade assigned
   - View detailed results

Expected Results:
-----------------
✓ 3 words imported successfully
✓ Quiz starts with first question
✓ Correct answers earn points
✓ Completion shows report card with:
  - 100% accuracy (if all correct)
  - Total points (varies by speed)
  - Grade (A+ expected for perfect)
  - Individual word results

Automated Test Available:
-------------------------
Run: python test_complete_quiz_flow.py


Buzz Dust Expectations
----------------------
The app uses a dual scoring system:
- Points = academic score (grades/GPA)
- Buzz Dust = XP used for Bee Class rank/badges

Important:
- **Buzz Dust is separate from Points/grades.**
- A student can have high Points but still be **Novice** if they have not earned much Buzz Dust yet.

Buzz Dust is earned during gameplay (e.g., from quiz activity and bonuses). It is **not** derived from lifetime points on page load.

Quick Manual Verification
-------------------------
1) Log in as a student.
2) Complete at least one quiz.
3) Open DevTools Console and run:
   fetch('/api/buzz-dust/info').then(r => r.json()).then(console.log)
4) Confirm:
   - total_buzz_dust increases after quizzes
   - current_class label matches thresholds once total_buzz_dust crosses them
   - any "Earn X more Buzz Dust" messaging matches the same Buzz Dust value shown in the UI

Badge vs Points Mismatch Check
------------------------------
- The Bee Class badge/rank should be driven by **total_buzz_dust** only (not lifetime points).
- If the UI ever shows a badge that looks out-of-sync:
  1) Run the `/api/buzz-dust/info` fetch above
  2) Verify the UI badge label matches `data.current_class.label`
  3) Verify the progress message matches `data.dust_needed`
