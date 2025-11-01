# Mobile Wrapping – BeeSmart Spelling App

This folder contains the configuration and steps to wrap the Flask web app for the Apple App Store and Google Play using Capacitor.

## Approach
- Keep the Python/Flask app hosted (Railway in prod).
- Wrap the site in a high‑performance WebView using Capacitor.
- Add native integrations (camera/microphone permissions, file picker) via Web APIs or Capacitor plugins if needed.
- Leverage the PWA baseline (manifest + service worker) for installability and offline caching.

## Prerequisites
- Node.js 18+
- Xcode (for iOS build), CocoaPods installed
- Android Studio + Android SDK (for Android build)
- Apple Developer account + Play Console account

## IDs and Names
- App Name: BeeSmart Spelling Bee
- Bundle ID (suggested): app.beesmartspelling
- Android Application ID (suggested): app.beesmartspelling
- Website: https://beesmartspelling.app

## Steps

1) Initialize Capacitor

```bash
npm init -y
npm i -D @capacitor/cli @capacitor/core
npx cap init "BeeSmart Spelling Bee" app.beesmartspelling --web-dir=dist
```

You can keep `web-dir=dist` even though we point to a remote URL—Capacitor requires a folder. We won’t bundle web assets initially.

2) Configure Capacitor server to point to production

Edit `capacitor.config.ts` (created here for you). Ensure:

```ts
server: {
  url: 'https://beesmartspelling.app',
  cleartext: false,
  androidScheme: 'https'
}
```

3) Add platforms

```bash
npx cap add ios
npx cap add android
```

4) Permissions & entitlements
- iOS (Info.plist):
  - NSCameraUsageDescription = "Allow taking a photo to upload spelling words."
  - NSMicrophoneUsageDescription = "Enable voice spelling input."
  - NSPhotoLibraryAddUsageDescription / NSPhotoLibraryUsageDescription if saving/choosing photos.
- Android (AndroidManifest.xml):
  - <uses-permission android:name="android.permission.CAMERA" />
  - <uses-permission android:name="android.permission.RECORD_AUDIO" />
  - Add READ_MEDIA_IMAGES (API 33+) or READ_EXTERNAL_STORAGE (<33) if needed.

5) Handle external links
Make sure links to external sites open in the system browser. You can use a simple JS handler in your web app to `target="_blank"` or handle via Capacitor’s Browser plugin.

6) Build

```bash
npx cap sync
npx cap open ios
npx cap open android
```

Then build and run from Xcode/Android Studio.

7) Store listing checklist
- App Icon (1024×1024 PNG, no transparency)
- Screenshots (phone + tablet)
- Short & full description
- Privacy policy URL: https://beesmartspelling.app/privacy
- Support URL: https://beesmartspelling.app/support
- Terms of Use: https://beesmartspelling.app/terms
- Age rating questionnaire (COPPA friendly)
- Category: Education
- Sign-in demo account if needed for review

8) Policy considerations
- Kids content: ensure COPPA compliance, no third‑party tracking.
- Microphone/Camera: ask for permission only when used.
- Account deletion path (if accounts exist) documented and implemented.

9) Optional: Deep Links / Universal Links
- If you need `beesmartspelling.app` links to open the app, configure:
  - iOS: Associated Domains (`applinks:beesmartspelling.app`)
  - Android: Asset Links + intent filter for your domain

10) Optional: Publish as a PWA
- Your PWA can be installable directly in Chrome/Edge and on Android. The manifest and service worker are already added.

## Next steps
- [ ] Install Node deps and run `npx cap init`
- [ ] Add platforms and set permissions
- [ ] Test camera/microphone flows inside the wrapper
- [ ] Prepare store metadata and assets
- [ ] Submit internal testing builds (TestFlight/Closed Testing)
