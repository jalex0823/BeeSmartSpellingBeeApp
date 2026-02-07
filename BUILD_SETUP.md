# BeeSmart Spelling Bee - Build Setup

## Installed Tools

The following have been installed for building the Android AAB:

| Tool | Status | Purpose |
|------|--------|---------|
| **JDK 17** (Eclipse Temurin) | Installed | Required for Gradle/Android build |
| **Node.js LTS** | Installed | Capacitor sync, npm |
| **Android Studio** | May need manual install | Provides Android SDK |

## Android SDK Required

The build needs the Android SDK. If you don't have it:

1. **Install Android Studio** (includes SDK):
   ```
   winget install Google.AndroidStudio --source winget --accept-package-agreements
   ```

2. **First launch**: Open Android Studio once. It will download the SDK (~2–3 GB).

3. **Default SDK location**: `C:\Users\jeff\AppData\Local\Android\Sdk`

The `mobile/android/local.properties` file points to this path.

## Build the AAB

Open a **new PowerShell window** (to pick up the new PATH), then:

```powershell
cd f:\GitHub\BeeSmartSpellingBeeApp\mobile

# Set Java 17 (if needed)
. .\set-java.ps1

# Build
.\build-release.ps1
```

Or run steps manually:

```powershell
cd f:\GitHub\BeeSmartSpellingBeeApp\mobile
npm run cap:sync
cd android
.\gradlew bundleRelease
```

Output: `mobile\android\app\build\outputs\bundle\release\app-release.aab`

## Troubleshooting

- **PowerShell execution policy**: If scripts are blocked, run:
  `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

- **npm not found**: Use the full path: `& "C:\Program Files\nodejs\npm.cmd" run cap:sync`

- **SDK not found**: Ensure Android Studio has been opened at least once to download the SDK.
