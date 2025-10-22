# BeeSmart Spelling Bee App

![CI/CD Pipeline](https://github.com/jalex0823/BeeSmartSpellingBeeApp/actions/workflows/ci.yml/badge.svg)
[![Railway Deploy](https://img.shields.io/badge/Railway-Deployed-brightgreen)](https://railway.app)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

A Flask-based spelling quiz application that supports uploading word banks in various formats (CSV, TXT, DOCX, PDF).

## Features

- Upload word banks in multiple formats
- Interactive spelling quiz with progress tracking
- Support for sentences and hints
- Streak tracking and statistics
- Saved Word Lists (create, manage, and reuse lists during quizzes)
- Secure password reset flow (hashed, expiring tokens; generic responses)
- Optional Redis-backed rate limiting for forgot-password requests

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python AjaSpellBApp.py
   ```

3. Open your browser to `http://localhost:5000`

### Password Reset (Dev & Tests)

For security, password reset responses are always generic. In development and CI, you can enable a test-only token peek to automate positive reset flows.

- Enable dev token peek (disabled by default):
   - PowerShell (Windows):
      ```powershell
      $env:ALLOW_DEV_RESET_PEEK='1'
      ```
   - bash (macOS/Linux):
      ```bash
      export ALLOW_DEV_RESET_PEEK=1
      ```
- Dev-only endpoint: `GET /dev/peek-reset-token?identifier=<email-or-username>` → `{ "token": "..." }`
   - Only available when `ALLOW_DEV_RESET_PEEK=1`.

Run the included e2e scripts:

- Ensure schema (one-time):
   ```powershell
   C:/Users/JefferyAlexander/Dropbox/BeeSmartSpellingBeeApp/.venv/Scripts/python.exe scripts/ensure_db_schema.py
   ```
- Positive reset path (dev-only):
   ```powershell
   $env:ALLOW_DEV_RESET_PEEK='1'; C:/Users/JefferyAlexander/Dropbox/BeeSmartSpellingBeeApp/.venv/Scripts/python.exe scripts/e2e_positive_reset.py
   ```
- Unittest covering generic + positive flows:
   ```powershell
   $env:ALLOW_DEV_RESET_PEEK='1'; C:/Users/JefferyAlexander/Dropbox/BeeSmartSpellingBeeApp/.venv/Scripts/python.exe test_password_reset_flow.py
   ```

After a successful reset, the login page shows a one-time banner:

> Your password was updated. You can sign in now.

The banner auto-hides after a few seconds.

### Optional Redis Rate Limiting

Forgot-password requests are rate limited. In production or scaled setups, you can enable shared rate limiting via Redis by setting one of:

- `REDIS_URL` (e.g., `redis://:password@hostname:6379/0`)
- `REDIS_CONNECTION_STRING` (same format)

If Redis isn’t available, an in-memory fallback is used.

## Mobile Readiness (iOS/Android)

This app can be shipped to the App Store and Play Store either as a wrapped WebView (Capacitor/Cordova), a PWA (Trusted Web Activity on Android), or a native client (React Native/Flutter) calling these APIs.

- WebView shell (recommended for fastest path):
   - Use Capacitor to wrap the deployed web app URL.
   - Ensure HTTPS, set secure cookies, and consider keeping all auth same-origin to avoid cross-site cookie constraints.
- PWA + TWA (Android):
   - Add a web manifest and a service worker for basic offline/asset caching.
   - Publish as a Trusted Web Activity for a lightweight Play Store presence.
- Native client (React Native/Flutter):
   - Call the Flask APIs directly; prefer token-based auth for cross-origin (consider adding a JWT login endpoint).

Mobile checklist we’ll tackle when we start wrapping:

- Security and cookies
   - Force HTTPS in production.
   - Set SESSION_COOKIE_SECURE=true and appropriate SameSite (Lax if same-origin; None + Secure if cross-origin).
   - If moving to native client auth, add a token-based login in addition to the session-based flow.
- CORS
   - If a native app will call APIs from a different origin, enable CORS for the app’s scheme/hosts.
- PWA
   - Add manifest.json, icons, and a simple service worker for caching static assets and basic offline UX.
- UX
   - Verify audio/pronunciation works with background audio permissions as needed.
   - Confirm touch targets, viewport meta, and mobile keyboard UX.
- Notifications (optional follow-up)
   - Integrate FCM/APNs if we later want reminders or streak nudges.

## Railway Deployment

This app is configured to deploy on Railway.

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python app and deploy using the included configuration files
3. The app will be available at your Railway-provided URL

### Files for Railway:

- `requirements.txt` - Python dependencies
- `Procfile` - Tells Railway how to run the app
- `railway.toml` - Railway configuration
- `templates/unified_menu.html` - Main landing page
- `/health` - Simple status endpoint

## File Formats

### CSV Format
```csv
word,sentence,hint
cat,The cat sat on the mat,animal
dog,The dog barked loudly,pet
```

### TXT Format
```
word
word|sentence
word|sentence|hint
```

### DOCX and PDF

Words can be extracted from document text, one word per line.

---

## Help & Troubleshooting

- Password reset testing
   - If the dev token peek returns 404 or disabled, set `ALLOW_DEV_RESET_PEEK=1` in your environment and retry.
- Rate limiting
   - If you see 429s on forgot-password, configure Redis via `REDIS_URL`/`REDIS_CONNECTION_STRING` or slow down requests during tests.
- OCR uploads (images)
   - OCR is optional and requires Tesseract; if not installed, image OCR features will be disabled gracefully.
- Railway port binding
   - Railway assigns a dynamic port. The included `Procfile` uses gunicorn and binds to `$PORT` automatically. Verify `/health` returns a version string.
- Sessions
   - Ensure `SECRET_KEY` is set in production to keep sessions secure.
- Dependencies
   - For DOCX/PDF parsing, ensure the related packages from `requirements.txt` are installed in your environment.

If you run into something not covered here, please open an issue with steps to reproduce and any logs from the server console.
