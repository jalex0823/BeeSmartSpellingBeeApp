# BeeSmart Spelling App — Release v1.7 Checklist

This checklist covers preparing and publishing v1.7 to Google Play and Apple App Store. It assumes the backend is deployed (e.g., Railway) and the mobile apps are wrappers pointing to your production URL.

## Backend
- [ ] Bump health version: GET /health → {"status":"ok","version":"1.7"}
- [ ] Set env flags for startup performance in production:
  - DEFER_HEAVY_INIT=1
  - RUN_GLB_SYNC_ON_STARTUP=0
  - ENABLE_BATTLES=0 (enable later if needed)
  - APP_DEBUG_STARTUP=0
- [ ] Verify key endpoints:
  - /health returns 200 with version 1.7
  - /api/avatars loads within 2s (cold) and <1s (warm)
  - /api/wordbank, /api/next, /api/answer OK

## PWA and Web
- [ ] Confirm service worker is served at /static/service-worker.js and registered from base.html
- [ ] Confirm manifest link in templates/base.html points to static/manifest.webmanifest (update if needed)
- [ ] Icons present under /static (192x192, 512x512, apple-touch-icon)

## Android (Google Play)
- Wrapper option A: Capacitor WebView
  - [ ] Sync content in mobile-wrapper/android (if used)
  - [ ] Update appId, appName, and server.url to production domain
  - [ ] Bump versionCode and versionName in app/build.gradle
  - [ ] Generate Signed Bundle (.aab)
  - [ ] Upload to Google Play Console → Internal testing → Review → Production

- Wrapper option B: Trusted Web Activity (TWA)
  - [ ] Verify PWA installation criteria: HTTPS, valid manifest, SW
  - [ ] Regenerate TWA via Bubblewrap with updated packageId and versionCode
  - [ ] Upload .aab to Google Play

## iOS (Apple App Store)
- [ ] Xcode project (Capacitor or WKWebView):
  - [ ] Bump CFBundleVersion (build) and CFBundleShortVersionString (1.7)
  - [ ] Set production URL allowlist (ATS/App Transport Security)
  - [ ] Update app icons and launch screen
  - [ ] Privacy Manifest (iOS 17+): declare APIs used; mark no tracking if applicable
  - [ ] App Privacy details in App Store Connect
  - [ ] Build for Any iOS Device (arm64), archive, upload via Xcode Organizer

## Store Listings
- [ ] Update screenshots if UI changed (avatar picker spacing, logo shimmer)
- [ ] Update version notes: performance improvements, startup optimizations, UI polish
- [ ] Reviewer notes: health endpoint URL and sample account, if needed

## Smoke Tests (Real Devices)
- [ ] Cold start under 3s to first content
- [ ] Avatar picker loads and previews 3D model
- [ ] Upload custom words → quiz flow works end-to-end
- [ ] Auth login/logout and password reset flows

## Rollout
- [ ] Stage rollout (Android) 10–20%, monitor ANRs/Crashes
- [ ] Phased release (iOS) if available
- [ ] Monitor server logs and /health for spike errors

Notes:
- v1.7 includes deferred initialization for dictionary and DB tasks, optional battles blueprint, and lighter startup logging.
- For further startup reductions, consider externalizing avatar catalog to JSON and lazy load.
