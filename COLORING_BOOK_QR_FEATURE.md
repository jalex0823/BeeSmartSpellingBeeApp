# Coloring Book QR Code Feature

## Overview

The **Coloring Book QR Scanner** allows users to scan QR codes printed in the physical BeeSmart Coloring Book to automatically load letter-based spelling word lists into the app. Each coloring book page features a QR code for one letter of the alphabet (A–Z), containing 5 kid-friendly words per letter.

## How It Works

### User Flow
1. User taps the **"Scan Coloring Book"** tile on the main menu.
2. A camera modal opens using the device's rear camera.
3. User points the camera at the QR code on their coloring book page.
4. The QR code is decoded client-side → a `set_id` (e.g. `a-set-01`) is extracted.
5. The app calls `POST /wordlists/from-set` to create (or fetch) the word list.
6. A success modal shows the words added.
7. The word list appears in the user's **Saved Word Lists**.

### QR Code Format
QR codes can encode either:
- A **raw set ID**: `a-set-01`
- A **URL**: `https://beesmartapp.com/q/coloring/a-set-01`

Both formats are supported by the client-side parser (`_extractSetIdFromQR`).

## Architecture

### Frontend (`unified_menu.html`)
- **Tile**: `#tileQRScanner` — auth-gated (not premium), replaces the old deactivated "Extract from Image" tile.
- **Modal**: `#qrScannerModal` — full-screen overlay with camera viewport.
- **Library**: [html5-qrcode v2.3.8](https://github.com/mebjas/html5-qrcode) loaded via CDN (`unpkg.com`).
- **Functions**:
  - `openQRScanner()` — opens modal, starts camera.
  - `closeQRScanner()` — stops camera, hides modal.
  - `_onQRCodeSuccess(decodedText)` — extracts set_id, calls API, shows result.
  - `_extractSetIdFromQR(raw)` — parses URL or raw token to get the set_id.

### Backend (`coloring_book_api.py`)

#### Blueprints
- `coloring_book_bp` — word list CRUD endpoints.
- `coloring_book_qr_bp` — QR landing route for direct URL scans (browser/web).

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/wordlists/from-set` | Login required | Create/fetch word list from a set_id |
| POST | `/wordlists/<list_id>/words/complete` | Login required | Mark a word as completed |
| GET | `/coloring-book/status` | Login required | Get overall A–Z progress |
| GET | `/q/coloring/<set_id>` | Public (redirects) | QR landing route for browser scans |

#### Word Sets (A–Z)
Each letter has a word set with ID format `{letter}-set-01` containing 5 words:
- **a**: ant, apple, acorn, airplane, astronaut
- **b**: bear, butterfly, balloon, banana, bridge
- ... (26 total sets, 130 words)
- **z**: zebra, zipper, zeppelin, zinnia, zombie

### Database Models
- `WordSet` — stores the 26 letter sets (seeded on startup via `seed_word_sets()`).
- `ColoringBookList` — per-user list for each scanned letter.
- `ColoringBookListItem` — individual words within a list, with completion tracking.
- `UserEntitlement` — unlocked rewards (hidden avatar).

## Hidden Avatar Unlock

When a user completes **all 26 letter sets** (every word in every set marked complete), they unlock the hidden **Spelling Champion** avatar (`avatar.spelling_champion`). This is tracked automatically by the `complete_word` endpoint.

## Tile History

The QR scanner tile replaces the previous **"Extract from Image"** (OCR) tile which was:
1. Originally a premium-gated OCR upload feature.
2. Deactivated for Apple compliance (OCR/Tesseract not available on Railway).
3. Force-hidden via `checkOCRAvailability()` + unconditional DOM removal on page load.

The old tile ID was `tileImageUpload`. The new tile ID is `tileQRScanner`.

### What Was Removed
- `checkOCRAvailability()` function — no longer needed.
- Force-hide/remove of `tileImageUpload` in `DOMContentLoaded`.
- Guest lock handler for `tileImageUpload` in `initializePage()`.

## Files Changed
- `templates/unified_menu.html` — tile HTML, QR scanner modal, JS logic.
- `coloring_book_api.py` — backend API (already existed, no changes needed).

## Testing Checklist
- [ ] Authenticated user sees "Scan Coloring Book" tile on main menu.
- [ ] Guest user sees locked tile with "Sign In to Unlock" overlay.
- [ ] Tapping tile opens camera modal.
- [ ] Scanning a valid QR code (e.g. `a-set-01`) creates a word list and shows success modal.
- [ ] Scanning the same QR code again shows "Already Saved" message.
- [ ] Invalid QR codes show an error and restart scanning.
- [ ] Camera permissions denied shows a clear error message.
- [ ] Close button (×) properly stops camera and closes modal.
- [ ] Works on iOS Safari (WebView/Capacitor).
- [ ] Works on Android Chrome (WebView/Capacitor).
