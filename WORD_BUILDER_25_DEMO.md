# WB25 — Word Wizard (25) (Demo / Feature-Flagged)

WB25 is an optional mini-game inside BeeSmart Spelling Bee:

- **Goal:** Make **25** valid words from one **base word**.
- **Modes:**
  - **Daily Challenge** (curated base word chosen deterministically by date)
  - **Custom Challenge** (player provides a base word)
- **Validation:**
  - words must be formable from the base word’s letters
  - minimum length: **3**
  - dictionary check uses BeeSmart’s educational dictionary sources
  - kid-friendly filtering applies (no revealing inappropriate content)

## Enable / Disable

WB25 is controlled with environment variables:

- `ENABLE_WORD_BUILDER_25` (default: `false`)
  - `true` enables the unified-menu tile and WB25 routes.
- `WORD_BUILDER_25_DEMO_MODE` (default: `true`)
  - when `true`, WB25 is **demo-safe** (no persistence/leaderboards/GPA writes).

See `.env.template` for the canonical defaults.

## Routes

- Page:
  - `GET /word-builder-25`

- APIs:
  - `POST /api/word-builder-25/start` → `{ mode: "daily" }` or `{ mode: "custom", base_word: "triangle" }`
  - `POST /api/word-builder-25/submit` → `{ word: "train" }`
  - `POST /api/word-builder-25/finish` → ends the round and returns summary

## Scoring (high level)

- Base points per accepted word (with length bonus)
- Badge category bonuses when you trigger a new category
- “All five badges” bonus
- Completion bonus when you reach 25 words
- Hard cap: **1000** points

## Notes for App Review / Demo

When `WORD_BUILDER_25_DEMO_MODE=true`, the backend should behave in a way that is safe during demos:

- returns a **GPA preview** in the `/finish` summary
- does not persist GPA or write leaderboard history

## Development

- Template: `templates/word_builder_25.html`
- Backend: WB25 logic & routes in `AjaSpellBApp.py` (search for `Word Builder 25 Challenge`)
- Optional persistence model: `WordBuilder25Session` in `models.py`

