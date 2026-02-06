# Production URL & App Icons

## 1. Production URL (no localhost)

The app **must** point to **https://beesmartspelling.app/** for store builds. No localhost.

**Verified locations:**
- `mobile/capacitor.config.ts` → `server.url: 'https://beesmartspelling.app/'`
- `mobile/capacitor.config.js` → `server.url: 'https://beesmartspelling.app/'`
- `mobile/www/index.html` → `window.location.replace('https://beesmartspelling.app')`
- `mobile-wrapper/capacitor.config.json` → `"url": "https://beesmartspelling.app/"`
- `capacitor.config.json` (root) → `"url": "https://beesmartspelling.app/"`

**Before release:** Confirm no `localhost` or `127.0.0.1` in mobile app config or built assets.

---

## 2. App Icons (BeeSmart Spelling Bee Application logo)

Use the BeeSmart Spelling Bee Application logo (bee with glasses, crest, honeycomb, “BeeSmart SPELLING BEE Application” text).

**To update icons:**
1. Save your logo as a **512×512 PNG** at **`static/BeeSmart_AppIcon_512.png`** (repo root).
2. Run:
   ```bash
   python scripts/generate_android_icons_from_source.py
   ```
3. This updates launcher icons in `android/`, `mobile/android/`, and `mobile-wrapper/android/`.

**iOS:** Replace icons in `mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/` (use 1024×1024 master; Xcode can generate sizes).
