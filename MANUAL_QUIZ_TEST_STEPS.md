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


Buzz Dust Baseline Expectations (No Bonuses)
-------------------------------------------
The app uses a dual scoring system:
- Points = academic score
- Buzz Dust = XP used for Bee Class rank/badges

For *baseline* estimation (ignoring all bonuses and badge points), Buzz Dust is:

  Buzz Dust ≈ floor(Points × 0.10)

So it takes about **10 points to earn ~1 Buzz Dust**.

Example:
- Points: 72,641
- Baseline Buzz Dust: floor(72,641 × 0.10) = 7,264

Approx Word-Points Needed Per Rank (No Bonuses, No Badge Points)
---------------------------------------------------------------
These are approximate point totals needed to reach each Bee Class threshold using ONLY the 10% multiplier.

| Bee Class | Min Buzz Dust | Approx word-points needed |
|----------|---------------:|--------------------------:|
| Apprentice | 500 | 5,000 |
| Scholar | 2,500 | 25,000 |
| Elite | 10,000 | 100,000 |
| Magistrate | 50,000 | 500,000 |
| Buzz Dust Master | 100,000 | 1,000,000 |

Notes:
- Real gameplay will often reach ranks faster due to bonuses (perfect round, streaks, etc.).
- Badge bonus points (when earned) can also add directly to Buzz Dust in the regular quiz completion flow.

Quick Manual Verification
-------------------------
1) Log in as a student.
2) Complete at least one quiz.
3) Open DevTools Console and run:
   fetch('/api/buzz-dust/info').then(r => r.json()).then(console.log)
4) Confirm:
   - total_buzz_dust increases after quizzes
   - current_class label matches thresholds once total_buzz_dust crosses them
   - any "Earn X more Buzz Dust" messaging matches the same Buzz Dust value shown in the UI (baseline-synced)
