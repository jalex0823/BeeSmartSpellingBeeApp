# Manual Keystore Generation Instructions
# Use this if the automated script fails

## Prerequisites
- Android Studio installed
- Java/keytool in PATH

## Step 1: Add Java to PATH (if needed)

After Android Studio installation, add Java to your session:

```powershell
# Find Android Studio's Java
$androidHome = "$env:LOCALAPPDATA\Android\Sdk"
$javaPath = "$androidHome\jbr\bin"

# Add to current session
$env:PATH += ";$javaPath"

# Verify
keytool -help
```

## Step 2: Generate Keystore

```powershell
cd "c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile\android"

keytool -genkey -v `
    -keystore upload-keystore.jks `
    -keyalg RSA `
    -keysize 2048 `
    -validity 10000 `
    -alias upload
```

You'll be prompted for:
1. **Keystore password** - Choose a strong password and SAVE IT
2. **Key password** - Can be same as keystore password
3. **First and last name** - Your name
4. **Organizational unit** - e.g., "Development"
5. **Organization** - e.g., "BeeSmart"
6. **City or Locality** - Your city
7. **State or Province** - Your state
8. **Country code** - e.g., "US"

## Step 3: Create keystore.properties

Create file: `android/keystore.properties`

```properties
storePassword=YOUR_KEYSTORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=upload
storeFile=upload-keystore.jks
```

Replace `YOUR_KEYSTORE_PASSWORD` and `YOUR_KEY_PASSWORD` with the passwords you used in Step 2.

## Step 4: Verify

```powershell
# Check keystore exists
Test-Path android\upload-keystore.jks

# Check properties exist  
Test-Path android\keystore.properties

# List keystore contents
keytool -list -v -keystore android\upload-keystore.jks -alias upload
```

## Step 5: Build Release

```powershell
# Navigate to mobile folder
cd "c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile"

# Sync Capacitor
npm run cap:sync

# Build AAB
cd android
.\gradlew bundleRelease

# Output will be in:
# android\app\build\outputs\bundle\release\app-release.aab
```

## Security Reminder

NEVER commit these files:
- `android/upload-keystore.jks`
- `android/keystore.properties`

They are already in `.gitignore`.

## Troubleshooting

### "keytool not found"
Android Studio not fully installed yet. Wait for installation to complete.

### "JAVA_HOME not set"
```powershell
$env:JAVA_HOME = "C:\Users\jeff\AppData\Local\Android\Sdk\jbr"
$env:PATH += ";$env:JAVA_HOME\bin"
```

### Find Android Studio's Java
```powershell
Get-ChildItem -Path "C:\Program Files\Android\Android Studio" -Filter "keytool.exe" -Recurse -ErrorAction SilentlyContinue
```
