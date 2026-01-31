# BeeSmart Quiz Keyboard – Smoke Test Checklist

Use this checklist in the browser to verify the custom on-screen keyboard before committing.

## Normal Quiz (`/quiz` or equivalent)

- [ ] **Before countdown**: Keyboard is **not** visible during loading, instructions, or round intro.
- [ ] **Countdown starts**: Keyboard **appears** exactly when the countdown timer is shown and starts ticking.
- [ ] **Native keyboard**: Tapping the answer field does **not** open the system keyboard.
- [ ] **Keys**: Only A–Z, Space, Backspace (no numbers, emojis, punctuation).
- [ ] **Backspace**: Removes last character reliably.
- [ ] **Space**: Works (no leading space).
- [ ] **Submit / timer end**: When you submit or timer hits 0, keyboard **disables** immediately (dimmed, no taps).
- [ ] **Game over**: When round/game complete screen shows, keyboard is **unmounted** (gone from DOM).

## Speed Round Quiz

- [ ] **Before answer phase**: Keyboard is **not** visible until the answer phase starts.
- [ ] **Answer phase**: Keyboard **appears** when countdown/answer phase begins.
- [ ] **Submit / complete**: On submit or round complete, keyboard **disables** and **unmounts**.

## General (both flows)

- [ ] **Tap targets**: Keys are easy to tap (no mis-taps); min key height feels at least 44px.
- [ ] **Phone + tablet**: Works without scrolling; keyboard fixed to bottom with safe-area (e.g. iOS notch).
- [ ] **Hex keys** (if enabled): Hex styling does not cause mis-taps; tap target remains large. (Hex is off by default; set `useHexKeys: true` in keyboard options to enable after QA.)

---

## Draft Commit Message

```
feat: BeeSmart quiz keyboard + teacher dashboard + startup error logging

- Custom on-screen keyboard (A–Z, Space, Backspace) for quiz/speed round only
- Keyboard lifecycle tied to countdown: mount when timer starts, disable on submit/timer end, unmount on game over
- BeeSmart theme (honey/gold), optional hex key styling, key sounds, Submit key animation
- Input attributes (spellcheck/autocorrect/inputmode) set to prevent native keyboard
- Teacher dashboard: layout aligned with admin (stat cards, table, key strip), bees/orbs hidden
- AjaSpellBApp: define app early + try/except around startup with "STARTUP FAILED:" traceback to stderr
```

After smoke test passes: commit, push, redeploy, then re-check deployment (Non-Zero Exit Code fix).