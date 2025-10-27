# 📊 Visual Flow Diagram - Retry System

## State Transitions

```
                          START QUIZ
                             ↓
                      ┌──────────────┐
                      │ Word Loaded  │
                      └──────┬───────┘
                             ↓
                      ┌──────────────┐
                      │ User Inputs  │
                      │ Spelling     │
                      └──────┬───────┘
                             ↓
                      ┌──────────────┐
                      │ Submit       │
                      │ Answer       │
                      └──────┬───────┘
                             ↓
                    ┌────────────────────┐
                    │ Check if Correct?  │
                    └─────┬────────┬─────┘
                   YES    │        │    NO
                        ┌─┘        └─┐
                        ↓            ↓
                    ┌────────┐   ┌──────────────────────┐
                    │ CORRECT│   │ isRetryAttempt?      │
                    │(100%)  │   │ hasRetried?          │
                    └───┬────┘   │ retryAvailable?      │
                        │        └─┬──┬────┬────────────┘
                        │    FALSE  │  │    TRUE
                        │        ┌──┘  └────┐
                        ↓        ↓          ↓
                   ┌────────┐ ┌──────────────────────────┐
                   │ANNOUNCE│ │SHOW CHOICE BUTTONS       │
                   │SUCCESS │ │(Retry / Show Answer)     │
                   │POINTS  │ │⏱️ 10-second timer       │
                   └───┬────┘ │                          │
                       │      └──┬─────────────────┬─────┘
                       │         │                 │
                       │    TIMEOUT            USER CLICKS
                       │    (10 sec)           /      \
                       │      │                /        \
                       ↓      │               ↓          ↓
                   ┌────────────────┐    ┌────────┐  ┌──────────┐
                   │AUTO-ADVANCE    │    │ RETRY  │  │SHOW      │
                   │NEXT WORD       │    │ PATH   │  │ANSWER    │
                   └────────────────┘    └───┬────┘  └────┬─────┘
                                             │           │
                                    ┌────────┴───┐    ┌──┴──────────┐
                                    │            │    │             │
                                    ↓            ↓    ↓             ↓
                              ┌──────────────┐  ┌─────────────────┐
                              │INPUT WINDOW  │  │SHOW CORRECT     │
                              │20-second     │  │SPELLING MESSAGE │
                              │NO ANSWER!    │  │"No problem! 📚" │
                              └──────┬───────┘  │SHOW [Next Word] │
                                     │         │BUTTON          │
                                  SUBMIT       └────────┬────────┘
                                  ANSWER              │
                                     │        ┌────────┴────────┐
                                  ┌──┴──┐     │                 │
                             ┌────┤CHECK├─────┴─┐               │
                             │    └──┬──┘       │               │
                          YES│       │NO    ALWAYS          ALWAYS
                             │       │        │                │
                       ┌──────┴┐  ┌──┴──┐     │                │
                       ↓       │  ↓     │     │                │
                  ┌────────┐   │ ┌─────────┐ │                │
                  │CORRECT │   │ │NO MORE  │ │                │
                  │(33%)   │   │ │RETRIES  │ │                │
                  │AUTO    │   │ │SHOW     │ │                │
                  │NEXT    │   │ │ANSWER   │ │                │
                  └───┬────┘   │ └────┬────┘ │                │
                      │        │      │      │                │
                      │        └──────┴──────┴────┐            │
                      │                          │            │
                      │          ┌────────────────┴───────────┘
                      │          │ CLICK [Next Word]
                      │          │
                      └──────┬───┴───────────────┐
                             ↓                   ↓
                        ┌─────────────────────────────┐
                        │ LOAD NEXT WORD              │
                        │ (Back to top)               │
                        └─────────────────────────────┘
```

---

## Message Display Timeline

```
TIMELINE:
Time: 0 ms               1000 ms              2000 ms              3000 ms
  │                        │                    │                    │
  ├─ INCORRECT ──────────────┼──────────────────┼────────────────────┤
  │  answer submitted        │                  │                    │
  │                          │                  │                    │
  ├─ BUTTONS APPEAR ─────────┼──────────────────┼────────────────────┤
  │  (No message!)           │ ← USER MUST      │                    │
  │                          │   CLICK NOW      │                    │
  ├─ TIMER: 10 SECONDS ──────┼────────────────┐ │ ← User clicked    │
  │                          │                │ │   OR timeout       │
  │                          └────────────────┼─┼────────────────────┤
  │                                           │ │ MESSAGE APPEARS!   │
  │                                           │ │ "No problem! 📚"   │
  │                                           │ │ OR timer for retry │
  │                                           │ │                    │
  │                                           └─┴────────────────────┤
```

---

## Code Execution Flow

```
handleAnswerSubmit()
    │
    ├─ result = validate answer
    │
    ├─ await showFeedback(result)
    │  │
    │  ├─ if result.correct:
    │  │  └─ Show success message (announces, points, etc)
    │  │
    │  └─ else (incorrect):
    │     │
    │     ├─ if isRetryAttempt OR hasRetried:
    │     │  └─ Show second failure (no more retries)
    │     │
    │     └─ else (first failure):
    │        ├─ feedbackArea.innerHTML = buttons ONLY
    │        ├─ startRetryChoiceCountdown(word)
    │        │  │
    │        │  ├─ Show 10-second timer
    │        │  │
    │        │  └─ If timeout OR user clicks:
    │        │     ├─ if handleRetryChoiceYes():
    │        │     │  ├─ feedbackArea.innerHTML = timer only
    │        │     │  └─ startRetryInputWindow()
    │        │     │     │
    │        │     │     └─ After submit (goes back to handleAnswerSubmit)
    │        │     │
    │        │     └─ if handleRetryChoiceNo():
    │        │        └─ feedbackArea.innerHTML = "No problem" + answer
    │        │
    │        └─ return (STOP HERE - don't load next)
    │
    ├─ updateScoreDisplay()
    │
    ├─ if result.correct:
    │  ├─ if quiz_complete: show badges/level
    │  └─ else: setTimeout(() => loadNextWord(), 800)
    │
    └─ (if incorrect: return stops execution here ↑)
       (Next word only loads from button click)
```

---

## State Variables

```
TRACKING RETRY USAGE:

isRetryAttempt: boolean
  - false: User hasn't used retry yet
  - true: User has attempted retry
  - Used by: handleRetryChoiceYes() to mark retry started
  - Check: if isRetryAttempt → no more retries offered

hasRetried: boolean
  - false: Initial state
  - true: User successfully completed or abandoned retry
  - Used by: Track if retry was used
  - Check: if hasRetried → no retry available

retryAvailable: boolean
  - true: User can still retry this word
  - false: No more retries available
  - Used by: Show/hide retry button
  - Check: if retryAvailable → show retry option

retryChoiceTimeoutId: number
  - ID of 10-second choice countdown timer
  - Cleared when: User clicks button or timer expires
  - Used by: Cancel choice countdown if user clicks

retryInputTimeoutId: number
  - ID of 20-second retry input timer
  - Cleared when: Time expires or user submits
  - Used by: Track retry window timer
```

---

## Button Lifecycle

```
BUTTON CREATION & REMOVAL:

Incorrect Answer
    ↓
showFeedback() called
    ├─ HTML created: #retryChoiceYes, #retryChoiceNo
    │
    ├─ Buttons added to feedbackArea.innerHTML
    │
    ├─ startRetryChoiceCountdown() called
    │
    └─ Event listeners attached:
       ├─ #retryChoiceYes → handleRetryChoiceYes()
       └─ #retryChoiceNo → handleRetryChoiceNo()

Wait for user...
    ↓
User clicks button
    ├─ Event listener fires
    │
    ├─ Button ID read (#retryChoiceYes or #retryChoiceNo)
    │
    ├─ Corresponding handler called
    │
    ├─ Buttons removed (innerHTML replaced)
    │
    └─ New content shown (timer or answer)

After choice is made
    └─ No more buttons until next word
```

---

## CSS State Classes

```
VISUAL STATES:

.feedback-area.feedback-success
  └─ Applied: When answer is CORRECT
     Colors: Green background
     Icons: ✅, 🎉, 📚

.feedback-area.feedback-error
  └─ Applied: When answer is INCORRECT
     Colors: Red/orange background
     Icons: ❌, ⏱️

.retry-choice-container
  └─ Applied: When showing choice buttons
     Layout: Flex, 2 buttons side-by-side
     Animation: Button hover effects

.retry-choice-btn.retry
  └─ Applied: To ✅ Retry button
     Color: Green
     Animation: Hover scale

.retry-choice-btn.show-answer
  └─ Applied: To ❌ Show Answer button
     Color: Red
     Animation: Hover scale

.retry-countdown-timer
  └─ Applied: To retry timer display
     Animation: countdownPulse (normal)

.countdown-critical
  └─ Applied: When timer ≤ 3 seconds
     Animation: countdownCriticalPulse (faster)
     Color: Red
```

---

## Event Listener Attachment

```
WHEN LISTENERS ARE ATTACHED:

Page Load (setupExitQuiz)
  └─ General listeners:
     ├─ Exit button
     ├─ Next Word button
     ├─ Stay button
     └─ ❌ NOT retry buttons (they don't exist yet!)

Incorrect Answer (startRetryChoiceCountdown)
  ├─ Buttons created in HTML
  │
  ├─ Button elements cloned:
  │  └─ removeEventListener() on old versions
  │     (prevents duplicate listeners)
  │
  └─ Fresh listeners attached:
     ├─ #retryChoiceYes → handleRetryChoiceYes()
     └─ #retryChoiceNo → handleRetryChoiceNo()

Button Click
  ├─ Listener fires
  ├─ Handler executes
  ├─ Buttons removed/hidden
  └─ No more listeners active (buttons gone)
```

---

## Data Flow Diagram

```
INPUT
  │
  ├─ Spelling from user
  ├─ Submitted to API
  └─ Validated on backend
       │
       ↓
   RESPONSE
       │
       ├─ correct: boolean
       ├─ word: string
       ├─ sentence: string
       ├─ points: { earned, breakdown }
       └─ progress: { correct, incorrect, streak }
            │
            ↓
   showFeedback()
       │
       ├─ If correct:
       │  └─ Update score
       │     Announce success
       │     Show points
       │     Load next word
       │
       └─ If incorrect:
          ├─ Reset streak
          ├─ Check retry availability
          │  ├─ If first failure:
          │  │  └─ Show choice buttons
          │  │     (Wait for user)
          │  └─ If second failure:
          │     └─ Show correct spelling
          │        + Next Word button
          └─ Return (stop execution)
               │
               ↓
            WAIT FOR USER CLICK
               │
       ┌───────┴───────┐
       │               │
       ↓               ↓
   Retry          Show Answer
       │               │
       ├─ Set flag     └─ Update feedback
       ├─ Show timer      with message
       ├─ Enable input    + answer
       └─ Wait submit     + Next Word btn
           │
           ↓
        USER SUBMITS
           │
           ↓
        Back to handleAnswerSubmit()
           (cycle continues)
```

---

## Success Conditions

```
✅ CORRECT FIRST ATTEMPT
   Answer submitted
   Result: correct = true
   ├─ Show success message
   ├─ Award 100% points
   ├─ Auto-advance to next word
   └─ Stats updated

✅ INCORRECT → RETRY → CORRECT
   First attempt wrong
   ├─ Show choice buttons (no answer)
   ├─ User clicks Retry
   ├─ Show input window (no answer)
   ├─ User types correct spelling
   ├─ Show success message
   ├─ Award 33% points
   ├─ Auto-advance to next word
   └─ Stats updated (correct, 1 retry)

✅ INCORRECT → SHOW ANSWER
   First attempt wrong
   ├─ Show choice buttons (no answer)
   ├─ User clicks Show Answer
   ├─ Show "No problem!" message
   ├─ Show correct spelling
   ├─ Show Next Word button
   ├─ User clicks Next Word
   └─ Load next word (no points)

✅ INCORRECT → RETRY → INCORRECT
   First attempt wrong
   ├─ Show choice buttons
   ├─ User clicks Retry
   ├─ Show input window
   ├─ User types wrong again
   ├─ Show "Not quite right" message
   ├─ Show correct spelling
   ├─ Show Next Word button
   ├─ User clicks Next Word
   └─ Load next word (no points)
```

---

## Summary

```
THREE CRITICAL FIXES:

1️⃣  HALT EXECUTION
    if (!result.correct) return;
    
    Effect: Stops auto-advance until user chooses

2️⃣  SHOW BUTTONS ONLY
    feedbackArea.innerHTML = buttons + timer
    (No message, no answer)
    
    Effect: Clear, simple choice interface

3️⃣  DEFER MESSAGES
    Message HTML only added after user clicks
    
    Effect: User focus on choice, then sees result
```

**Status: ✅ ALL FIXES COMPLETE & TESTED**
