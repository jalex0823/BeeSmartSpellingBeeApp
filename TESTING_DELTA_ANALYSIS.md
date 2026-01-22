# Testing Delta Analysis: Local vs Production

## Problem Statement

**Smoke tests pass locally** ✅ but **JavaScript errors occur in production** ❌

## Root Cause

### Current Smoke Test Limitations

The `smoke_test_import_to_report_card.py` test **only validates API endpoints**:
- ✅ `/api/upload` - Word upload
- ✅ `/api/quiz/start` - Quiz initialization  
- ✅ `/api/next` - Get next word
- ✅ `/api/answer` - Submit answer
- ✅ `/api/next` (final) - Get report card

**What it DOESN'T test:**
- ❌ JavaScript syntax errors
- ❌ Runtime JavaScript errors
- ❌ Script loading order issues
- ❌ Browser console errors
- ❌ Class definition timing
- ❌ DOM initialization sequence

### Production vs Local Differences

| Factor | Local | Production | Impact |
|--------|-------|------------|-------|
| **Network Latency** | ~0ms | 50-500ms | Scripts load slower, timing issues |
| **CDN Loading** | Local files | CDN (Three.js, etc.) | Multiple instances, load failures |
| **Browser Caching** | Fresh load | Aggressive caching | Stale scripts, version conflicts |
| **Script Order** | Predictable | Variable | Classes may not be defined when needed |
| **Error Visibility** | Console visible | Hidden in logs | Errors go unnoticed |

## Specific Issues Found

### 1. Multiple Three.js Instances
```
WARNING: Multiple instances of Three.js being imported.
```
**Cause**: Scripts with `defer` load asynchronously, and Three.js may be loaded multiple times from different sources (CDN + local).

**Location**: `templates/quiz.html:3129`
```html
<script defer src="{{ url_for('static', filename='js/vendor/three.min.js') }}?v={{ timestamp }}"></script>
```

### 2. BeeDelightManager Not Found
```
⚠️ BeeDelightManager not found (skipping).
```
**Cause**: Class definition may not be registered on `window` before DOMContentLoaded handler runs.

**Fixed**: Added `window.BeeDelightManager = BeeDelightManager;` at line 5172

### 3. QuizManager Not Ready
```
⚠️ Exit button exists but QuizManager not ready yet
```
**Cause**: Exit button setup runs before QuizManager is instantiated, especially when QuizManager class loads asynchronously.

**Fixed**: Added retry mechanism with callback for async creation

## Solution: Browser-Based Testing

### Created: `smoke_test_quiz_javascript.py`

This test:
1. ✅ Loads the actual HTML page in a browser
2. ✅ Captures JavaScript console errors
3. ✅ Verifies class definitions exist
4. ✅ Checks initialization sequence
5. ✅ Tests both local and production URLs

### Usage

```bash
# Test local
python smoke_test_quiz_javascript.py

# Test production
BASE_URL=https://beesmartspelling.app python smoke_test_quiz_javascript.py
```

### Requirements

```bash
pip install selenium
# Also requires ChromeDriver in PATH
```

## Recommendations

### 1. Add Browser Testing to CI/CD
- Run `smoke_test_quiz_javascript.py` against production after deployment
- Fail build if JavaScript errors detected

### 2. Fix Script Loading Issues
- **Check for duplicate Three.js loads**: Ensure only one instance
- **Verify script order**: Inline scripts that depend on classes should wait
- **Add error boundaries**: Catch and log initialization failures

### 3. Improve Error Visibility
- Add error logging to production
- Send JavaScript errors to monitoring service (Sentry, etc.)
- Add health check endpoint that validates JavaScript initialization

### 4. Test Both Environments
- **Local**: Fast, predictable, good for development
- **Production**: Real network conditions, catches timing issues

## Next Steps

1. ✅ Created browser-based JavaScript test
2. ⏳ Install Selenium and test against production
3. ⏳ Fix Three.js multiple instances warning
4. ⏳ Add production error monitoring
5. ⏳ Integrate browser tests into CI/CD pipeline

## Testing Checklist

- [ ] API smoke test passes (current)
- [ ] Browser JavaScript test passes (new)
- [ ] No console errors in production
- [ ] All classes defined before use
- [ ] Script loading order verified
- [ ] Network latency scenarios tested
