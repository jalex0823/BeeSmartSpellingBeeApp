# BeeSmart Mobile Wrapper (Capacitor)

> ⚠️ Status: legacy/experimental
>
> The actively maintained, store-bound wrapper in this repo is **`/mobile`**.
> That folder contains the current Android/iOS projects and the BeeSmart native IAP bridge.
> Keep this `mobile-wrapper/` folder only if you still need it for historical reference.

This folder contains the Capacitor wrapper to ship BeeSmart to Apple App Store and Google Play. It loads your deployed web app inside a secure native WebView.

## Prereqs

- macOS with Xcode 15+ (for iOS) and Android SDK/Android Studio (for Android)
- Node.js 18+
- Apple Developer and Google Play developer accounts
- Backend deployed over HTTPS (e.g., Railway)

The wrapper points to your production URL via `capacitor.config.json > server.url`.

## 1) Install deps

```zsh
cd mobile-wrapper
npm ci
```

## 2) Sync Capacitor and add platforms

```zsh
# Generate native projects from config
npx cap sync

# Add iOS project (if not present)
npx cap add ios

# Add Android project (already present but safe to re-sync)
npx cap add android
```

If you already have `android/`, just run `npx cap sync android`.

## 3) iOS build & publish

1. Open Xcode:

   ```zsh
   npx cap open ios
   ```

2. In Xcode, set:
   - Signing & Capabilities: your Team, Bundle ID `com.beesmart.spellingbee` (or your own), and build version.
   - Targets > Info: CFBundleShortVersionString (e.g., 1.7) and CFBundleVersion (build number).
   - App Icons and Launch Screen: drag your assets into the asset catalog.
   - App Transport Security: no exceptions needed for HTTPS Railway; ensure your production domain is HTTPS.
   - Privacy Manifest (iOS 17+): add a Privacy Manifest file and set “No tracking”. No Required‑Reason APIs are used.
3. Build: Product > Archive, then Distribute via Organizer to TestFlight/App Store.

Tip: You can override health version for production without code changes:

```zsh
# In your production env (Railway or similar)
export HEALTH_VERSION=1.7
```

## 4) Android build & publish

1. Open Android Studio:

   ```zsh
   npx cap open android
   ```

2. Verify in `android/app/build.gradle`:
   - `applicationId` matches your Play package (e.g., `com.beesmart.spellingbee`).
   - `versionCode` (e.g., 7) and `versionName` (e.g., "1.7").
3. Generate a Signed Bundle (.aab): Build > Generate Signed Bundle/APK…
4. Upload the .aab in Google Play Console (Internal testing → Production rollout).

## 5) Store listing & QA

- Screenshots: capture from device/simulator (home, quiz, avatar picker).
- Version notes: startup optimizations, UI polish, dictionary/quiz fixes.
- Reviewer notes: optional health endpoint URL and guest account steps.

## Troubleshooting

- White screen: ensure `capacitor.config.json` `server.url` points to a reachable HTTPS URL.
- External links stay in app: base.html includes logic to open external links in the native browser when running in Capacitor.
- CORS/auth: backend must send proper CORS/SameSite cookies; consider SameSite=None; Secure for production.

## Commands reference

```zsh
# Update web assets if you host locally in /www (optional)
npm run build  # if you have a frontend build step
npx cap copy

# Open platforms
npx cap open ios
npx cap open android
```
