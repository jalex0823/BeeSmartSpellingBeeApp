# Quiz Start Flow – Reduce Modals & Key Presses

## Current flow (4 steps / up to 3 taps)

| # | Step | Where | User action | Platform |
|---|------|--------|-------------|----------|
| 1 | **Pre-quiz overlay** | `preQuizLoadOverlay` | None (auto: "Getting your avatar ready… Loading…") | All |
| 2 | **Resume / Start Over** | `resumeModal` | Tap [Resume] or [Start Over] | Desktop only (iOS/Safari skips) |
| 3 | **Voice intro** | `voiceIntroModal` | Tap [Start with Buzzy's Voice] or [Start Silent] | iOS/Safari only |
| 4 | **Intro / Play** | `feedbackArea` (showIntroAnnouncer) | Tap [Play] (desktop) or auto-start / optional tap (mobile) | All |

- **Desktop, new quiz:** 1 tap (Play).  
- **Desktop, with unfinished quiz:** 2 taps (Resume/Start Over → Play).  
- **iOS, new quiz:** 1 tap (Voice modal) then often auto-start; sometimes 2 if “Tap to Hear” or delay.  
- **iOS, resume:** Currently resume is disabled on iOS; so same as new quiz.

So we have **up to 3 taps** (resume + voice + play) in theory; in practice **1–2 taps** per path. The “4” likely counts the **four distinct steps** (overlay + resume + voice + play).

---

## Goal

- **Target: 1 tap** to start a new quiz (choose voice and start in one action).  
- **With resume:** At most **2 taps** (Resume vs Start Over, then if “Start Over” treat like new quiz with 1 tap).

---

## Option A – Single “Ready to spell?” screen (recommended)

**Idea:** One screen after load (and after resume choice when applicable). No separate voice modal and no separate “Play” screen.

1. **Resume (desktop only):** Keep as-is: one modal [Resume] [Start Over]. One tap.  
2. **Then:** Replace “Voice intro modal” + “Intro/Play” with a **single screen** in `feedbackArea` (or one combined modal):
   - **Copy:** “Ready to spell? Choose how you’d like to start.”
   - **Buttons:** [Start with Buzzy’s voice] [Start silent]
   - **Behavior:** Tapping either:
     - Sets voice on/off (and unlocks for iOS).
     - Starts the quiz immediately (short “Get ready!” then countdown + first word).
   - No second “Play” step; no separate voice modal.

**Result:**  
- New quiz: **1 tap** (voice choice = start).  
- With resume: **2 taps** (Resume or Start Over, then if Start Over → 1 tap on “Ready to spell?”).

**Implementation outline:**

- Remove or bypass `showVoiceIntroModal()` for the normal “new quiz” path.
- In `showIntroAnnouncer()` (or a new `showCombinedStartScreen()`):
  - Always show the same UI: two buttons “With Buzzy’s voice” / “Silent”.
  - On button click: set `voiceUnlocked` / `announcerEnabled`, set `quizStarted = true`, call `loadNextWordWithIntro()` (optionally after a very short “Get ready!” line or countdown).
- On iOS, the tap that chooses voice is the user gesture; trigger any intro speech (if “With voice”) in the same handler so we don’t need a second modal.
- Keep resume modal as-is; after “Start Over” (or when there’s no resume), go straight to this single “Ready to spell?” screen.

---

## Option B – Combine Resume + Voice in one modal (desktop)

**Idea:** When resume is offered, add voice choice to the same modal so “Start Over” users don’t see a second screen.

- **Modal title:** “Quiz in progress” (unchanged).
- **Body:** “Resume where you left off, or start over. If you start over, choose voice:”
- **Buttons:** [Resume] [Start over with voice] [Start over silent]

**Result:**  
- With unfinished quiz: **1 tap** (Resume or Start over + voice in one go).  
- New quiz (no resume): still need the single “Ready to spell?” screen (1 tap).

**Implementation:** Extend `showResumeOrRestartModal()` to add two “Start over” variants (with/without voice) and pass the choice into QuizManager so it doesn’t show the voice modal again.

---

## Option C – Keep overlay; no extra tap

**Idea:** Pre-quiz overlay stays non-interactive (no “Tap to continue”). All required taps are “meaningful” (resume vs start, voice vs silent, or combined).

- No change to overlay behavior; just ensure we don’t add a tap there.
- Combine steps 3 + 4 (and optionally 2 + 3) as in A or B.

---

## Recommended path (shortest implementation)

1. **Implement Option A**
   - Single “Ready to spell?” screen: [Start with Buzzy’s voice] [Start silent] → one tap starts quiz.
   - Remove the separate **Voice intro modal** for the normal start path (or show it only when we explicitly want “first-time explainer” in the future).
   - Remove the **second “Play” step** after voice choice; the tap that chooses voice also starts the quiz.
2. **Optional: Option B** later
   - Combine Resume + “Start over with voice/silent” in one modal so desktop users with an unfinished quiz never see a second modal.
3. **Pre-quiz overlay**
   - Leave as non-interactive (Option C).

**Files to touch (for Option A):**

- `templates/quiz.html`:
  - **QuizManager constructor:** After deciding “normal” vs “resume”, for “normal” and when not iOS (or when we’re consolidating for iOS too), call a new `showCombinedStartScreen()` instead of `showVoiceIntroModal()` (iOS) or `showIntroAnnouncer()` (desktop).
  - **showCombinedStartScreen():** One block of HTML in `feedbackArea` with two buttons; on click set voice, set `quizStarted = true`, call `loadNextWordWithIntro()`. On iOS, in the same click handler trigger intro speech if “With voice” so one gesture unlocks audio.
  - **showVoiceIntroModal():** Stop calling for the default “new quiz” path (or make it conditional, e.g. only for a “first time” flag).
  - **showIntroAnnouncer():** Either remove the “Play” path and replace with the combined screen, or have it only show the combined “Ready to spell?” UI (two buttons, no separate Play).

**Testing**

- Desktop: New quiz → one screen, one tap (With voice / Silent) → quiz starts.
- Desktop: Unfinished quiz → [Resume] or [Start Over] → if Start Over, one screen, one tap → quiz starts.
- iOS: New quiz → one screen, one tap (With voice / Silent) → quiz starts (voice works from that tap).
- iOS: No resume modal; same one-tap start as above.

---

## Summary

| Current | After (Option A) |
|--------|-------------------|
| 4 steps (overlay, resume, voice, play) | 2 steps (overlay, then one “Ready to spell?” screen) |
| 1–3 taps depending on path | **1 tap** (new quiz) or **2 taps** (resume then start) |
| Two modals/screens for “how to start” (voice + play) | **One** screen (voice choice = start) |

This plan keeps the pre-quiz overlay as-is, reduces to a single “Ready to spell?” screen for starting, and optionally combines resume + start-over on desktop for at most two taps in all cases.
