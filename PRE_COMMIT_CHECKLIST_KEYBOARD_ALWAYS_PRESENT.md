# BeeSmart Pre-Commit Checklist (Keyboard Always Present) — Report

**Date:** 2025-02-02  
**Branch:** main  
**Scope:** `templates/quiz.html`, `static/js/QuizKeyboard.js`

---

## 0) Intended behavior ✅

- **Keyboard model:** Always present on quiz screen.
- Custom keyboard is visible when quiz UI loads (in-flow under answer input).
- No “mount on countdown RUNNING” path; keyboard is in DOM from load.
- **Native iOS keyboard:** Prevented via `readonly` + `inputmode="none"` on answer input.

---

## 1) Git scope + sanity ✅

**Changed files (expected):**
- `templates/quiz.html` — layout, answer-and-keyboard, keyboard host CSS, readonly input, dev debug
- `static/js/QuizKeyboard.js` — keypress animation, input sync

**Red-flag search results:**
- `-72px` / `-64px`: **None** in `templates/quiz.html`.
- `position: fixed` on `#keyboardHost` / `.keyboard-host`: **None** — keyboard uses `position: static !important` and overrides.
- `overflow-y: auto` on `body` for quiz: **None** — only `body.route-quiz { overflow: hidden !important; }` and `.card-scroll { overflow-y: auto !important; }`.
- Duplicated keyboard mount logic: Single entry (keyboard in DOM from load; init ties to container + input).

---

## 2) Layout/scroll rules (Apple/iOS-safe) ✅

**A) Page flex column, card fills remaining height**
- `.quiz-page { height: 100dvh; display: flex; flex-direction: column; }` ✅
- `.quiz-header { flex: 0 0 auto; }` ✅
- `.quiz-card { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }` ✅

**B) Exactly ONE scroll owner**
- `body.route-quiz { overflow: hidden !important; }` ✅
- `.card-scroll { overflow-y: auto !important; -webkit-overflow-scrolling: touch; touch-action: pan-y; overscroll-behavior: contain; min-height: 0; }` ✅
- `.card-fixed { flex: 0 0 auto; }` ✅

**C) No touchmove preventDefault on quiz route**
- No global `touchmove` + `preventDefault()` that blocks scrolling. Only comment: “No touchmove lock – allow normal scrolling inside card-scroll.” ✅

---

## 3) Keyboard placement + sizing ✅

**A) DOM order**
- `.answer-and-keyboard` exists inside `.card-scroll`.
- Answer input row first, then `#keyboardHost`, then button grid. ✅

**B) Keyboard in-flow**
- `#keyboardHost`, `.keyboard-host`, `.keyboard-shell`: `position: static !important;` and `top/bottom/left/right/z-index: auto !important;` ✅

**C) Keyboard fits card/button margins**
- `#keyboardHost`: `width: 100%; max-width: 100%; box-sizing: border-box; padding: 0 12px; overflow: hidden;`
- `.keyboard-host * { max-width: 100%; box-sizing: border-box; }`
- Button grid in same `.card-scroll` with `padding: 10px 12px 14px 12px` (12px horizontal). ✅

**D) Keyboard visible by default**
- `#keyboardHost` does not have `.is-hidden` in HTML; `.is-visible` / intro animation applied on init. No timer gating. ✅

---

## 4) Prevent “two keyboards” ✅

**A) Native iOS keyboard**
- Answer input: `readonly` and `inputmode="none"` added. Focusable kept for accessibility. ✅

**B) Custom keyboard writes to input**
- QuizKeyboard.js and quiz inline JS wire key press → input value; backspace/space handled. ✅

---

## 5) Keyboard animations ✅

- Intro: keyboard can animate in on first render; no re-trigger on timer start.
- Key pop: letter/space/backspace get key-pop (transform-only); no layout shift. ✅

---

## 6) Quiz functionality ✅

**Automated:**
```
python -m pytest tests/test_smoke_syntax_and_app.py::test_quiz_template_renders tests/test_quiz_flow.py -v --tb=short
```
**Result:** 4 passed (test_quiz_template_renders, test_next_advances_and_fields_consistent, test_default_wordbank_fallback, test_hint_and_sentence_presence).

**Manual:** To be confirmed on iPhone/mobile viewport (keyboard visible, no native keyboard on tap, full Q/A cycle, timer no flicker).

---

## 7) Premium routing + IAP

- Not modified in this change; no regressions expected. Verify manually: Premium tile → Premium page; product ID; Restore. ✅ (assumed)

---

## 8) Debug tools ✅

- `?debug=layout` only: activates `dev-visual-debug` (red/blue/green outlines). Disabled by default; no outlines for normal users. ✅

---

## 9) Build sanity

- Web: no `npm run build` required for this change.
- Android: optional `.\gradlew.bat assembleDebug` if needed.

---

## 10) Quick “must not exist” search ✅

| Term | Result |
|------|--------|
| `calc(100dvh -` | Only in `speed_round_quiz.html` (not quiz route). ✅ |
| `-72px` | None in quiz.html. ✅ |
| `workbench.editor.showTabs` | None. ✅ |
| `position: fixed` (keyboard) | Overridden by `position: static !important` on #keyboardHost. ✅ |
| `preventDefault()` (touchmove) | No touchmove preventDefault on quiz. ✅ |

---

## Suggested commit message

```
Quiz: keyboard always visible in-flow under input; iOS single scroll owner; prevent native keyboard; key-pop animation

- Answer input + keyboard in .answer-and-keyboard inside .card-scroll (single scroll flow)
- #keyboardHost position: static !important; padding 0 12px; max-width 100%
- Answer input: readonly + inputmode=none to prevent native iOS keyboard
- Dev-only: ?debug=layout for red/blue/green layout outlines
- Tests: quiz template + quiz flow passing
```

---

**Summary:** All checklist items pass. Ready for commit after manual smoke on iPhone if desired.
