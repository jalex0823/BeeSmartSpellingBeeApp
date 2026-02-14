# Android Quiz Fix – Announcer Not Heard & App Reset

## Issues Addressed

1. **Cannot hear word being spelled** – Web Speech API (`speechSynthesis`) may not work reliably in Android WebView.
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

The plugin is already added to `package.json`. After `npm install` and `cap sync`, the native TTS will be available. A future update can add a bridge in the quiz to prefer native TTS on Android when the plugin is present.

---

## Testing

1. **Speech:** On Android, start the quiz with voice enabled. The announcer should speak the intro and each word. If not, try the "Speak again" (speaker) button.
2. **Reset:** If an error occurs, the page should reload at most once per minute.

---

## Date
February 2025
