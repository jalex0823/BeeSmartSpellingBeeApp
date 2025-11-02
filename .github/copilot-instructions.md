# BeeSmart Spelling Bee App — AI agent quickstart

This repo is a Flask app for kids’ spelling practice with uploads, an interactive quiz, avatars, and admin/auth. Below are the minimum patterns to follow so edits fit the system and tests/CI remain green.

## Core architecture
- Session data is hybrid: small metadata in cookies; the active word list lives server‑side in `WORD_STORAGE`.
- Always use `get_wordbank()`/`set_wordbank()` and `init_quiz_state()`; never read/write the session keys directly.
    - Keys: `DATA_KEY="wordbank_v1"`, `QUIZ_STATE_KEY="quiz_state_v1"`; `session["wordbank_storage_id"]` is a legacy UUID pointer.
- Definitions flow is orchestrated by `get_word_info(word)`:
    1) Simple English Wiktionary cache (background‑loaded), 2) `DICTIONARY_CACHE` file, 3) live API via `dictionary_api.lookup_word` (500ms rate limit + circuit breaker), 4) `generate_smart_fallback()`.
    - Backend blanks answers using `_blank_word` and filters with `_filter_definition` so spelling is never revealed.

## Uploads and word model
- Parsers enrich each record to the shape `{"word": str, "sentence": str, "hint": str}`; `sentence` is what the quiz shows.
- Dedupe and correctness checks use a normalization that removes non‑alphanum and lowercases before compare.
- After any set of words is stored, call `init_quiz_state()` to shuffle indices and reset progress/counters.
- OCR is optional: gate any image OCR on `TESSERACT_AVAILABLE` (alias `OCR_AVAILABLE`).

## Avatars in a nutshell
- Static assets live under `static/assets/avatars/`.
    - OBJ avatars: one folder per avatar; GLB avatars live in `glb_files/` with thumbnails in `glb_files/AvatarThumbnails/`.
- Use the JSON provided by avatar APIs/templates; don’t hardcode paths—prefer the `urls` fields when available.
- Quick local asset sanity: run the VS Code task “Avatar: Asset Consistency (localhost)” which calls `test_avatar_assets.py`.

## Auth and password reset
- Reset flow is generic by default. A dev‑only peek is available when `ALLOW_DEV_RESET_PEEK=1` at `/dev/peek-reset-token?identifier=…` for e2e.
- See scripts: `scripts/ensure_db_schema.py`, `scripts/e2e_forgot_reset.py`, `scripts/e2e_positive_reset.py`.

## Key routes and pages (examples)
- Upload: `POST /api/upload` (parse → dedupe → enrich → store → `init_quiz_state`).
- Quiz step: `POST /api/next`, answer: `POST /api/answer` with `{"user_input","method","elapsed_ms"}`.
- Utilities: `GET /api/wordbank`, `POST /api/clear`, health: `GET /health` → `{version: "1.6"}`.
- UI: `templates/unified_menu.html`, `magical_quiz.html`, `speed_round_quiz.html`; PWA endpoints include `/service-worker.js` and `/.well-known/*`.

## Local dev and tests
- Python 3.11. Install deps then run `AjaSpellBApp.py` to serve on http://localhost:5000.
- Representative checks (Windows PowerShell):
    - Ensure DB schema: use `scripts/ensure_db_schema.py`.
    - Run comprehensive flow: `python test_v15_complete_validation.py`; or start the app then `python final_test_complete.py`.
    - Many focused tests exist (avatar, upload, definitions); CI also runs on pushes via `.github/workflows/`.

## Conventions and pitfalls
- Don’t stash full word lists in the session—only via helpers; keep the UUID indirection intact.
- After changing session schema, bump the `*_v1` keys and migrate within `get_wordbank()`.
- Only cache successful dictionary results to `data/dictionary.json`.
- Keep definitions kid‑friendly and never reveal the answer; rely on `get_word_info` filtering/blanking.

## Pointers
- Main app: `AjaSpellBApp.py` (routes, session logic, uploads, quiz, auth, avatars).
- Dictionary: `dictionary_api.py` + `data/dictionary.json`.
- Avatars: templates under `templates/*avatar*`, JS under `static/js/*avatar*`, assets under `static/assets/avatars/`.
- CI: `ci.yml` and `avatar-asset-check.yml` lint, basic tests, and optional Railway deploy.
