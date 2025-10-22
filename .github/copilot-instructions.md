# BeeSmart Spelling Bee App - AI Coding Agent Instructions

## Project Overview
A Flask-based educational web app for kids' spelling practice with multi-format word list uploads (CSV, TXT, DOCX, PDF, images via OCR) and an interactive quiz interface with dictionary integration.

## Architecture & Data Flow

### Session Management Pattern
- **Hybrid storage**: Small session metadata in cookies + large data in server-side `WORD_STORAGE` dict
- Session keys: `DATA_KEY = "wordbank_v1"` and `QUIZ_STATE_KEY = "quiz_state_v1"`
- Word lists stored via UUID: `session["wordbank_storage_id"]` → `WORD_STORAGE[uuid]`
- **Critical**: Always use `get_wordbank()` and `set_wordbank()` helpers, never access session directly
- Quiz state tracked per-session: index, order (shuffled indices), correct/incorrect counts, streak

### Dictionary System (3-tier fallback)
1. **Cache-first**: Check `DICTIONARY_CACHE` (loaded from `data/dictionary.json` at startup)
2. **API lookup**: `dictionary_api.py` with rate limiting (500ms), circuit breaker (5 failures → 5min timeout)
3. **Smart fallback**: `generate_smart_fallback()` creates pattern-based hints (-ing, -ed, -ly, -tion words)

```python
# Always use get_word_info() for definitions - handles all 3 tiers
definition = get_word_info(word)  # Returns formatted string with fill-in-the-blank
```

### File Upload Pipeline
1. **Parse**: Format-specific parsers (`parse_csv`, `parse_txt`, `parse_docx`, `parse_pdf`, `parse_image_ocr`)
2. **Deduplicate**: `normalize()` function (strips non-alnum, lowercases) for comparisons
3. **Enrich**: Auto-fetch definitions via `get_word_info()` if sentence/hint missing
4. **Store**: `set_wordbank()` + `init_quiz_state()` to shuffle and reset progress

## Critical Conventions

### OCR Graceful Degradation
```python
# pytesseract is optional - always check TESSERACT_AVAILABLE before OCR features
if not TESSERACT_AVAILABLE:
    raise RuntimeError("Image processing requires Tesseract OCR...")
# Alias for test compatibility: OCR_AVAILABLE = TESSERACT_AVAILABLE
```

### Word Record Format
```python
{"word": str, "sentence": str, "hint": str}  # sentence is primary display field
```

### Normalization for Comparisons
```python
is_correct = normalize(user_input) == normalize(correct_spelling)
# normalize() removes all non-alphanumeric and lowercases
```

## Testing Workflow

### Running Tests
```powershell
# Full feature validation (12 comprehensive tests)
python test_v15_complete_validation.py

# Quick validation with live app
python AjaSpellBApp.py  # Terminal 1: Start server on :5000
python final_test_complete.py  # Terminal 2: Test upload → wordbank → quiz flow
```

### Test Structure
- Use `app.test_client()` for route testing
- Session-based tests require `with self.app.session_transaction()` context
- Check `final_test_complete.py` for session-aware integration test pattern using `requests.Session()`

## Deployment Configuration

### Railway (Production)
- **Builder**: Dockerfile (includes Tesseract system deps)
- **Entry point**: `Procfile` → `gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 AjaSpellBApp:app`
- **Health check**: `/health` endpoint (300s timeout in `railway.toml`)
- **Port binding**: Always use `$PORT` env var (Railway assigns dynamically)

### Local Development
```powershell
pip install -r requirements.txt
python AjaSpellBApp.py  # Runs on http://localhost:5000 with debug mode
```

## Key Files & Responsibilities

- `AjaSpellBApp.py`: Main Flask app (1286 lines) - routes, session logic, upload parsers
- `dictionary_api.py`: API client with rate limiting, circuit breaker, kid-friendly normalization
- `data/dictionary.json`: Persistent cache (format: `{"words": {word: {definition, example, phonetic}}}`)
- `50Words_kidfriendly.txt`: Default word list (pipe-delimited: `word|definition|example sentence`)
- `templates/unified_menu.html`: Main landing page with 3-card menu (Upload/OCR/Quiz)
- `templates/quiz.html`: Interactive quiz interface

## API Endpoints Reference

### Upload Flow
- `POST /api/upload` → Parse file → Dedupe → Enrich → Store → Init quiz
- `POST /api/upload-enhanced` → Background processing with `GET /api/upload-progress/<id>` polling

### Quiz Flow
1. `POST /api/next` → Get current word's definition/hint (no reveal of spelling)
2. `POST /api/answer {"user_input": "...", "method": "keyboard|voice", "elapsed_ms": int}` → Validate + advance
3. `POST /api/pronounce` → Get phonetic spelling (`build_phonetic_spelling()` returns "B E E" format)
4. `POST /api/hint` → Return hint field if available

### Utility
- `GET /api/wordbank` → Current session's word list
- `POST /api/clear` → Reset wordbank + quiz state
- `GET /health` → Status check (returns v1.6)

## Common Pitfalls

1. **Never store full word lists in session directly** - Use `WORD_STORAGE` with UUID keys
2. **Default word loading**: `load_default_wordbank()` only loads if `50Words_kidfriendly.txt` exists
3. **Template variable typo**: Use `timestamp` query param for cache-busting in template routes
4. **Dictionary cache saves**: Only successful API lookups and fallbacks get cached (not errors)
5. **Quiz state initialization**: Always call `init_quiz_state()` after `set_wordbank()` to shuffle order

## UI Conventions

- **Bee theme**: Progress messages use bee metaphors ("bees gathering words", "bees storing in hive")
- **Animation system**: Fairy containers for visual polish (see `templates/unified_menu.html`)
- **Responsive design**: Mobile-first with `BeeSmart.css` in `static/css/`
- **No answer reveals during quiz**: Only show definitions/hints, not the target word spelling

## Making Changes

When modifying:
- **Upload parsers**: Update both sync (`parse_*`) and async (`process_upload_with_progress`) versions
- **Session schema**: Bump version keys (e.g., `wordbank_v2`) and add migration logic in `get_wordbank()`
- **Dictionary integration**: Changes to `dictionary_api.py` require updating `get_word_info()` caller
- **New routes**: Add to route list in `test_v15_complete_validation.py` for coverage

## Version Management
Current version: **v1.6** (check `/health` endpoint or bottom of main templates)
