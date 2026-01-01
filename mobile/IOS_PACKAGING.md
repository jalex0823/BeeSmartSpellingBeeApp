# BeeSmart Spelling Bee — iOS Packaging (Capacitor Wrapper)

This app ships as a Capacitor wrapper that loads your hosted web app at <https://beesmartspelling.app> in a secure WKWebView. Follow these steps to produce a build for TestFlight/App Store.

## Prerequisites

- macOS with Xcode 15+ and Apple Developer Program access
- Node.js 18+ and npm
- CocoaPods (`sudo gem install cocoapods`)
- Your web app online at <https://beesmartspelling.app> (already configured in `mobile/capacitor.config.ts`)

## 1) Install dependencies

```bash
cd mobile
npm ci
```

## 2) Sync iOS platform

```bash
npx cap sync ios
```

This copies config and web assets into `ios/` and installs CocoaPods.

## 3) Open Xcode

```bash
npx cap open ios
```

Then select the "App" target.

## 4) Set signing + bundle metadata

In Xcode (targets → App → Signing & Capabilities):

- Team: your Apple Team
- Bundle Identifier: `com.beesmart.spelling`
- Version (Marketing Version): e.g. `1.0.0`
- Build (Current Project Version): increment (e.g. `1` → `2`)
- iOS Deployment Target: iOS 15.0 or newer (required for StoreKit 2 restore/purchase bridge)

## 4b) In-App Purchases (direct App Store / StoreKit 2)

This project includes an **app-local Capacitor plugin** (`BeeSmartIAPPlugin.swift`) that uses **StoreKit 2**.

In Xcode (targets → App → Signing & Capabilities):

- Add capability: **In-App Purchase**
- Confirm **iOS Deployment Target is 15.0+** (StoreKit 2)

### TestFlight sanity check

After installing a TestFlight build:

- Open the app and navigate to the **Subscription** page.
- Complete a purchase/restore test as needed.
- If purchases don’t work, confirm the Capacitor StoreKit 2 plugin is registered and that iOS 15+ is used.

## 5) Permissions (Info.plist)

Already set in `ios/App/App/Info.plist`:

- NSCameraUsageDescription
- NSMicrophoneUsageDescription
- NSPhotoLibraryUsageDescription
- NSPhotoLibraryAddUsageDescription

Adjust copy to match your App Store privacy descriptions if needed.

## 6) App icons and splash

Assets live in `ios/App/App/Assets.xcassets`.

- `AppIcon.appiconset`: ensure 1024×1024 source present (e.g., `AppIcon-512@2x.png`)
- `Splash.imageset`: update splash images if desired

## 7) Optional: Universal Links (Associated Domains)

If you want links like <https://beesmartspelling.app> to open the app:

- Backend: ensure `/.well-known/apple-app-site-association` is served (already present in backend routes)
- Xcode: add Signing & Capabilities → Associated Domains → `applinks:beesmartspelling.app`
- If missing, create `App.entitlements` in the iOS target and set `CODE_SIGN_ENTITLEMENTS`

## 8) Archive and upload

In Xcode:

- Product → Archive
- In Organizer, Validate App (optional) then Distribute App → App Store Connect → Upload
- Wait for processing (10–20 minutes), then create a TestFlight build

## 9) App Store Connect checklist

- Create app record with bundle ID `com.beesmart.spelling`
- Add screenshots (6.7" and 5.5" at minimum), description, keywords, support URL, and privacy policy URL
- Fill Data Safety/Privacy (tracks only required analytics; no child-sensitive tracking)
- Export Compliance: answer NO to cryptography if only TLS

## 10) Troubleshooting

- White screen on launch: confirm `server.url` in `capacitor.config.ts` points to a reachable HTTPS URL
- Camera/mic prompts not showing: verify permission usage strings and that your flows request via Capacitor plugins
- ATS errors: ensure all remote resources load over HTTPS
- Universal Links not working: validate the AASA file with `apple-app-site-association` validator and ensure Associated Domains entitlement is enabled

## Quick commands (reference)

```bash
# From project root
cd mobile
npm ci
npx cap sync ios
npx cap open ios
```

If you need help with any step, ping the packaging task — we can automate more of this in scripts if desired.
