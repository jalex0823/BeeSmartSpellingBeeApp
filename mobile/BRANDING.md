# Branding – Icons & Splash

Update native icons and splash screens to your BeeSmart branding.

## Android
- App name: set in `mobile/android/app/src/main/res/values/strings.xml` (already "BeeSmart Spelling Bee").
- App icons: replace images in `mobile/android/app/src/main/res/mipmap-*/` with your icon sets.
  - Prefer to generate via Android Studio: Image Asset Studio → Launcher Icons.
  - Use a 1024×1024 source PNG (no transparency if following Play guidance).
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
