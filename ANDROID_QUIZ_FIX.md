# Android Quiz Fix – Announcer Not Heard & App Reset

## Why iOS/Desktop Work But Android Doesn’t

- **iOS / desktop:** The Web Speech API (`speechSynthesis`) works reliably, so the announcer and word pronunciation use it and you hear sound.
- **Android:** In the Android WebView (and often in Chrome on Android), `speechSynthesis` is unreliable and often produces **no sound** (no error, just silence). So the quiz uses **native TTS** on Android when the Capacitor Text-to-Speech plugin is present. If the plugin wasn’t included in the Android build, the app falls back to Web Speech and you get no announcer audio.

## Issues Addressed

1. **Cannot hear word being spelled** – Use native TTS on Android when the plugin is in the build; Web Speech is unreliable in Android WebView.
2. **Quiz resets the app** – Reload loops when errors occur.

---

## Fixes Applied (quiz.html)

### 1. Android Speech – Language Code
- **Change:** Use `lang: 'en'` instead of `'en-US'` for Android.
- **Reason:** Some Android devices reject `en-US` with "Not supported on this device".
- **Locations:** All `utterance.lang` assignments in Android blocks.

### 2. Reload Loop Prevention
- **Change:** Only allow one reload per 60 seconds for syntax errors.
- **Reason:** Prevents infinite reload loops when the same error recurs.
- **Implementation:** `sessionStorage.__quizErrorReloadTs` guard in global error handler.

---

## Native TTS Fallback (Recommended for Android)

The Web Speech API may be unavailable or unreliable in Android WebView. For reliable speech on Android, use the native Text-to-Speech plugin:

### Install Plugin

```bash
cd mobile
npm install @capacitor-community/text-to-speech
npx cap sync android
```

### Rebuild

```bash
# From mobile/
npx cap open android
# Then Build → Build Bundle(s) / APK(s) in Android Studio
```

The plugin is in `mobile/package.json`. The quiz uses native TTS on Android when the plugin is available (`BeeSmartTryNativeTTS`). The Android project has been updated to include the Text-to-Speech plugin:

- `mobile/android/app/src/main/assets/capacitor.plugins.json` – TTS plugin registered
- `mobile/android/capacitor.settings.gradle` – TTS module included
- `mobile/android/app/capacitor.build.gradle` – TTS dependency added

**Before building the Android app:** From repo root run `cd mobile && npm install` so `node_modules/@capacitor-community/text-to-speech` exists. Then build the AAB/APK (e.g. open Android Studio and build). The announcer should then use native TTS and play on device. If you run `npx cap sync android` later, it may regenerate these files; as long as the plugin is in `package.json` and installed, sync will keep the TTS plugin in the build.

---

## Testing

1. **Speech:** On Android, start the quiz with voice enabled. The announcer should speak the intro and each word. If not, try the "Speak again" (speaker) button.
2. **Reset:** If an error occurs, the page should reload at most once per minute.

---

## Date
February 2025
