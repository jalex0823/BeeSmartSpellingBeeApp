# BeeSmart Spelling Bee App — Mobile Readiness Checklist

A shareable, checkbox-style checklist for functional QA and mobile app-store readiness (iOS + Android). Use this in GitHub issues/PRs or copy into Notion/Docs. Includes a lightweight test log.

## Core Functional QA
- [ ] Upload via POST `/api/upload` supports TXT/CSV; records enriched to `{word, sentence, hint}`.
- [ ] Dedupe normalization removes non‑alphanum and lowercases before compare.
- [ ] After storing words, call `init_quiz_state()` (shuffle indices, reset progress).
- [ ] Wordbank persistence uses `get_wordbank()` / `set_wordbank()` only; atomic writes verified.
- [ ] Wordbank survives refresh and restart; state remains consistent.
- [ ] Quiz endpoints work: `POST /api/next`, `POST /api/answer` with `{user_input, method, elapsed_ms}`.
- [ ] Sentence remains visible during countdown; honey jar timer overlays without hiding it.
- [ ] Scoring/stats: correct, incorrect, streak, points, retry (33% points) correct.
- [ ] Definitions never leak answers; `_blank_word` and `_filter_definition` applied.
- [ ] Dictionary flow: cache → `data/dictionary.json` → `dictionary_api.lookup_word` (500ms + circuit breaker) → `generate_smart_fallback()`.
- [ ] OCR feature gated by `TESSERACT_AVAILABLE`/`OCR_AVAILABLE`; disabled gracefully if absent.
- [ ] Health endpoint responds (e.g., `{version: "1.6"}`); utilities `GET /api/wordbank`, `POST /api/clear` OK.
- [ ] Admin/auth flows work; DEV-only reset peek allowed when `ALLOW_DEV_RESET_PEEK=1`.

## Avatars & Assets
- [ ] Total avatars = 39; `avatar_catalog.py` is source of truth.
- [ ] Apple compliance: ALL avatar names end with " Avatar".
- [ ] GLB files present under `static/assets/avatars/glb_files/`.
- [ ] Thumbnails under `glb_files/AvatarThumbnails/` (no honeycomb fallback for defined avatars).
- [ ] Key mappings:
  - [ ] Robo Bee Avatar → `BuzzbotBee.glb`
  - [ ] Super Bee Avatar → `SuperBee.glb`
  - [ ] Knight Bee Avatar → `KnightBee.glb`
- [ ] Franken Bee thumbnail uses `AvatarThumbnails/FrankenBee!.png` (or alias), not honeycomb.
- [ ] `/api/avatars` returns catalog names, GLB & thumbnail URLs; sorted/deduped.
- [ ] Run `python count_avatars.py` → 39; run `python test_avatar_assets.py` → pass.
- [ ] `cleanup_railway_database.py` syncs DB with catalog; no drift.

## Mobile UX & Compatibility
- [ ] Voice announcer initializes once; consistent female voice; iOS Safari `voiceschanged` handled.
- [ ] Mute toggle reliable; persists in-session.
- [ ] Visualizer performance: DPR capped; adaptive density; pauses when tab hidden.
- [ ] Timer morph fades waves only; sentence remains visible; layout stable.
- [ ] Touch ergonomics: buttons ≥ 44px; inputs avoid iOS zoom (≥16px font size).
- [ ] Word list page fixed 3-per-row hex grid; responsive 3→2→1.
- [ ] “View list” modal displays word strings (not objects).
- [ ] PWA assets exist (`/service-worker.js`, `/.well-known/*`); offline graceful behavior.

## Performance & Stability
- [ ] Smooth startup; no heavy main-thread stalls.
- [ ] Dictionary requests respect 500ms limit; circuit breaker prevents lock-ups.
- [ ] No memory leaks across long sessions; canvas resizing stable.
- [ ] Minimal reflow/repaint; overlays z-index correct.

## Accessibility (A11y)
- [ ] Accessible names/roles; aria-live for feedback/hints.
- [ ] Adequate contrast; readable font sizes.
- [ ] Audio doesn’t auto-play on iOS without user gesture; voice intro modal shown.
- [ ] Mute available; no essential info conveyed only via audio/animation.

## Data, Storage & Security
- [ ] Hybrid session respected: small cookie metadata; active list in `WORD_STORAGE` server-side.
- [ ] No full word lists in session; UUID indirection intact.
- [ ] Only successful dictionary results cached to `data/dictionary.json`.
- [ ] `.env` exists; no secrets hardcoded; DB schema ensured via `scripts/ensure_db_schema.py`.

## App Store Readiness
### iOS (Apple)
- [ ] Avatar names end with " Avatar"; assets conform.
- [ ] Icons and splash configured; PWA/packaged assets consistent.
- [ ] Kids-safe content; age rating appropriate; COPPA alignment if needed.
- [ ] SpeechSynthesis usage complies with user gesture policy; privacy disclosures ready.

### Android (Google)
- [ ] Speech/audio consistent; microphone optional (not required for quiz).
- [ ] Adaptive icon & splash; minimal permissions.
- [ ] Privacy policy present; tracking-free verified.

## Test Scenarios
- [ ] E2E: Upload → Quiz start → Voice announce → Countdown → Submit (correct/incorrect) → Retry → Next → Report → Exit modal.
- [ ] Edge: Empty wordbank handling.
- [ ] Edge: All incorrect; retry math/points verified.
- [ ] Network: Slow/unavailable dictionary; fallback path.
- [ ] Device: iOS Safari voice delay; Android Chrome high DPR.
- [ ] Offline: Quiz and word list degrade gracefully.
- [ ] Regression: Sentence visible during countdown; word list modal shows strings; hex grid responsive.

---

## Lightweight Test Log Template
Fill one per device/OS/build.

- Tester:
- Date:
- Commit/Build:
- Device/OS:
- Browser/WebView:
- Network (WiFi/Cell; good/poor/offline):

Results:
- Core functions: PASS/FAIL — notes:
- Avatars & assets: PASS/FAIL — notes:
- Mobile UX: PASS/FAIL — notes:
- Performance: PASS/FAIL — notes:
- Accessibility: PASS/FAIL — notes:
- Data/Security: PASS/FAIL — notes:
- Store readiness: PASS/FAIL — notes:

Issues found:
- …

Workarounds:
- …

Artifacts:
- Screenshots/recordings links:

---

## Optional local run (Windows PowerShell)
```powershell
# Start app
C:/Users/JefferyAlexander/AppData/Local/Programs/Python/Python310/python.exe "C:\Temp\bs\BeeSmartSpellingBeeApp\AjaSpellBApp.py"

# Health check
Invoke-WebRequest -UseBasicParsing http://localhost:5000/health

# Avatars (if scripts present)
python count_avatars.py
python test_avatar_assets.py

# Ensure DB schema
python scripts/ensure_db_schema.py
```
