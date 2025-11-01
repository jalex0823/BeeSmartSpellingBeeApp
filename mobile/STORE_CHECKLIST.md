# Store Checklist – BeeSmart Spelling Bee

This checklist captures everything needed to submit to the Apple App Store and Google Play.

## Identity
- App Name: BeeSmart Spelling Bee
- iOS Bundle ID: app.beesmartspelling
- Android Application ID: app.beesmartspelling
- Category: Education (Kids-friendly)
- Website: https://beesmartspelling.app
- Support: https://beesmartspelling.app/support
- Privacy Policy: https://beesmartspelling.app/privacy
- Terms: https://beesmartspelling.app/terms

## Versioning
- Marketing version (e.g., 1.0.0) – set per release
- Build number (increment per store upload)

## App Icons
- Master source: 1024×1024 PNG (no transparency)
- iOS: AppIcon set (Xcode asset catalog)
- Android: mipmap-* (Android Studio will generate if provided master)

## Splash/Launch Assets (optional but recommended)
- iOS: LaunchScreen storyboard + images (Assets.xcassets/Splash)
- Android: drawable splash for portrait/landscape densities

## Screenshots
- iOS: 6.7", 6.5", 5.5" (and iPad if supported: 12.9")
- Android: Phone (5–7), 7-inch tablet, 10-inch tablet
- Suggest at least 3–5 per device with key flows: Home, Avatar, Quiz, Upload, Results

## Permissions (declared)
- Camera: take photo of worksheets/books to extract words
  - iOS: NSCameraUsageDescription
  - Android: android.permission.CAMERA
- Microphone: voice spelling input
  - iOS: NSMicrophoneUsageDescription
  - Android: android.permission.RECORD_AUDIO
- Photos/Storage: select/save images
  - iOS: NSPhotoLibraryUsageDescription / NSPhotoLibraryAddUsageDescription
  - Android: READ_MEDIA_IMAGES (API 33+), READ_EXTERNAL_STORAGE (<33)

## In-App Behavior for Review
- Ask permissions only at point-of-use (camera/mic)
- External links open in system browser (Capacitor Browser wired)
- Age-appropriate content, COPPA-friendly
- No third-party tracking SDKs (unless declared and compliant)

## Reviewer Notes (copy-paste into store notes)
- Test account (if sign-in is required):
  - Username: demo@beesmartspelling.app
  - Password: Provided in review notes (or not required if guest flow allowed)
- Steps to reach core features:
  1) Open app → Home
  2) Use Upload Text / Image to create a word list
  3) Start Quiz → Voice input optional (microphone prompt when used)
  4) Avatar visible on Home and Quiz (GLB-first rendering)

## Store Listing – Text
- Subtitle/Short Description: Fun, kid-friendly spelling practice with avatars and voice input.
- Full Description (bulleted):
  - Upload your spelling words (text, image with OCR)
  - Practice with definitions and hints
  - Voice input for hands-free practice
  - Friendly avatars and animations
  - Kid-safe content filtering
- Keywords (iOS) / Tags (Android): spelling, kids, education, learning, practice, quiz

## Compliance & Policies
- COPPA: App is designed for kids; avoids personal data collection beyond necessary app use
- Account Deletion: Provide an email or in-app mechanism if accounts are created
- Data Safety (Play Console): declare microphone/camera usage purpose, no background recording

## Technical
- iOS Signing: set Team, Provisioning Profile, Automatic signing
- Android Signing: configure keystore for release builds
- Build Targets: iOS deployment target (e.g., 13+), Android minSdk/targetSdk (Capacitor default OK)
- Networking: HTTPS only (androidScheme https; cleartext disabled)

## Pre-Submission QA
- Camera flow works on device
- Microphone flow works on device
- External links open in native browser
- Manifest & service worker present (installable as PWA)
- Performance: first interactive under target on mid-tier device

## Post-Submit
- Set up TestFlight / Internal Testing track
- Collect feedback and crash reports
- Prepare 1.0.1 patch plan
