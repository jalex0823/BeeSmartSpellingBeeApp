# BeeSmart Polished Tasks Implementation Plan

## Task 1: Registration UX - Cancel/Exit Functionality

### Requirements
- Add Cancel/Exit button on all registration steps
- Confirm dialog if any fields have values
- Back to Main Menu button in header
- ESC key shortcut support

### Files to Modify
- `templates/auth/register.html` - Main registration form
- Add header button and ESC listener
- Check for form changes before confirming exit

### Implementation
1. Add "Back to Main Menu" button in header
2. Track form state (pristine vs. modified)
3. Show confirmation dialog if form has values
4. Add ESC key event listener

---

## Task 2: Avatar Behavior - Stop Auto-Spin

### Requirements
- Stop all default auto-spinning on main page
- Avatars animate ONLY on interaction:
  - Tap/Click: short spin/bounce (≤800ms), return to idle
  - Hover: subtle sway, stop when hover ends
- Global toggle flag: `AvatarAnimationsEnabled`

### Files to Modify
- `templates/unified_menu.html` - Main mascot (already stopped spinning)
- `static/js/user-avatar-loader.js` - User avatar loader
- `static/js/mascot-3d.js` - Mascot behavior

### Current State
✅ Mascot auto-rotation already stopped (autoRotate: false)
✅ playMascotShow() function already implemented for click interactions
⚠️ Need to verify user avatar doesn't auto-spin
⚠️ Need to add hover sway effect

---

## Task 3: Speed Round Error Fixes

### Current Error (from screenshot)
```
SyntaxError: Unexpected token '}'
user-avatar-loader.js:1 Uncaught ReferenceError: avatar loaded: undefined
```

### Requirements
- Guard against null/undefined word lists
- Guard against timer issues
- Guard against audio reference errors
- Show graceful error: "Speed Round content failed to load. Try again."

### Files to Modify
- `templates/speed_round_quiz.html`
  - Add null checks for currentWord
  - Add try-catch around timer operations
  - Add error boundary UI
  - Validate data before use

### Implementation
1. Add error boundary div to UI
2. Wrap fetchNextWord() in try-catch
3. Add currentWord validation before timer start
4. Add fallback error state with retry button

---

## Task 4: Voice Visualization & TTS Cadence

### Requirements
- Natural speech with brief pause between words
- SSML/TTS: `<speak>spell <break time="150ms"/> banana</speak>`
- Per-word spacing: 120-200ms (configurable)
- Visualizer shows decay/gap between words

### Files to Modify
- `templates/quiz.html` - Main quiz voice visualization
- `templates/speed_round_quiz.html` - Speed round voice visualization

### Current State
✅ Voice visualizer already has natural pause animation (amber)
✅ Already implemented in quiz.html
⚠️ Need to verify Speed Round has same behavior
⚠️ Need to add SSML breaks if using Web Speech API

---

## Task 5: Speed Round Word Source - File Browser

### Requirements
- "My Uploaded Word List" button should open file browser
- Same behavior as home screen upload
- Show word count popup after selection

### Files to Modify
- `templates/speed_round_setup.html`
- Add hidden file input
- Trigger file browser on radio button click
- Show upload progress/word count

---

## Implementation Priority

1. **CRITICAL**: Task 3 - Fix Speed Round errors (blocking usage)
2. **HIGH**: Task 1 - Registration Cancel/Exit (UX improvement)
3. **MEDIUM**: Task 5 - Speed Round file browser (feature enhancement)
4. **MEDIUM**: Task 2 - Avatar hover effects (polish)
5. **LOW**: Task 4 - Verify voice visualization (already mostly done)

---

## Testing Checklist

### Task 1 - Registration
- [ ] Cancel button appears in header
- [ ] ESC key triggers cancel action
- [ ] Confirmation dialog shows if form has values
- [ ] Confirmation dialog skipped if form pristine
- [ ] Returns to main menu on confirm

### Task 2 - Avatar Animations
- [ ] No auto-spinning on page load
- [ ] Click triggers animation (≤800ms)
- [ ] Hover shows subtle sway
- [ ] Sway stops when hover ends
- [ ] Animation returns to idle state

### Task 3 - Speed Round
- [ ] Page loads without errors
- [ ] Timer starts correctly
- [ ] Input field responds
- [ ] Words advance properly
- [ ] Error boundary shows on failure
- [ ] Retry button works

### Task 4 - Voice Visualization
- [ ] Natural pauses between words (150ms)
- [ ] Visualizer shows gaps during pauses
- [ ] Amber color during pauses
- [ ] Smooth transitions

### Task 5 - File Browser
- [ ] Radio button opens file browser
- [ ] File selection uploads words
- [ ] Word count popup appears
- [ ] Speed round uses uploaded words
