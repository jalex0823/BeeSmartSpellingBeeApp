# Branding – Icons & Splash

Update native icons and splash screens to your BeeSmart branding.

## Android
- App name: set in `mobile/android/app/src/main/res/values/strings.xml` (already "BeeSmart Spelling Bee").
- **App icons (single source):** Use the BeeSmart Spelling Bee Application logo (bee with glasses, crest, honeycomb, “BeeSmart SPELLING BEE Application” text). Place a **512×512 PNG** at **`static/BeeSmart_AppIcon_512.png`** (repo root), then run:
  ```bash
  python scripts/generate_android_icons_from_source.py
  ```
  This updates launcher icons in `android/`, `mobile/android/`, and `mobile-wrapper/android/`.
- Splash images: replace drawables in `mobile/android/app/src/main/res/drawable*` (files named `splash.png`).

## iOS
- App name: already set in `Info.plist` (CFBundleDisplayName = BeeSmart Spelling Bee).
- Icons: open `mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/` and replace with your icon set.
  - Provide all required sizes (Xcode Asset Catalog).
- Splash: update images in `Assets.xcassets/Splash.imageset/` or customize LaunchScreen.storyboard.

## Tips
- Keep icons simple and readable at small sizes.
- Test on dark/light backgrounds.
- Validate with store preview tools (App Store Connect / Play Console).
