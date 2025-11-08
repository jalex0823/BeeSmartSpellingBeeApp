# Changelog

All notable changes to this project will be documented in this file.

## 2025-11-07

### Added
- Loading overlay restored with pulsing “Tap to Start” button and readable system checks.
- Real readiness checks wired:
  - Environment: GET `/health`.
  - Dictionary/wordbank reachability: GET `/api/wordbank`.
  - Avatars: probe `/static/js/user-avatar-loader.js`.
  - Quiz UI: probe `window.QuizCelebrations` or `/static/js/quiz-celebrations.js`.
  - Session: session cookie presence or server reachability fallback.
- localStorage flag (`bs_skip_overlay`) to skip overlay after first successful start. Override with `?forceLoad=1`.

### Branding
- Global crest initialization in `base.html` via `window.BeeSmartBrand.logoPath`.
- Runtime logo replacement script (`static/js/brand-logo-replacer.js`) applied across pages.

### Avatars
- Name → image sync on podium via `static/js/avatar-name-sync.js` with debounce and race safety.

### Misc
- `.gitignore` tightened to exclude video formats and mobile `node_modules/`.

### Notes
- Overlay exposes `window.LoadingScreenManager` for future hook-ins (`mark`, `hide`, `show`, `isComplete`).
- Reduced-motion respected; overlay animations calm when system setting is enabled.
