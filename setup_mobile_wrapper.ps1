# BeeSmart Spelling Bee - Mobile Wrapper Setup Script
# Run this script to initialize Capacitor wrapper for iOS and Android

Write-Host "🐝 BeeSmart Mobile Wrapper Setup" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Cyan

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version
    Write-Host "✅ npm installed: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install Node.js" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Installing Capacitor CLI globally..." -ForegroundColor Cyan
npm install -g @capacitor/cli

# Create mobile-wrapper directory
$wrapperDir = "C:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile-wrapper"
Write-Host ""
Write-Host "📁 Creating mobile-wrapper directory..." -ForegroundColor Cyan

if (Test-Path $wrapperDir) {
    Write-Host "⚠️  Directory already exists. Do you want to remove it? (y/n)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'y') {
        Remove-Item -Recurse -Force $wrapperDir
        Write-Host "✅ Old directory removed" -ForegroundColor Green
    } else {
        Write-Host "❌ Setup cancelled" -ForegroundColor Red
        exit 1
    }
}

New-Item -ItemType Directory -Force -Path $wrapperDir | Out-Null
Set-Location $wrapperDir

# Initialize npm project
Write-Host ""
Write-Host "🚀 Initializing Capacitor project..." -ForegroundColor Cyan

$packageJson = @"
{
  "name": "beesmart-mobile",
  "version": "1.0.0",
  "description": "BeeSmart Spelling Bee Mobile App",
  "main": "index.js",
  "scripts": {
    "sync": "npx cap sync",
    "open:ios": "npx cap open ios",
    "open:android": "npx cap open android",
    "build:ios": "npx cap copy ios && npx cap open ios",
    "build:android": "npx cap copy android && npx cap open android"
  },
  "keywords": ["capacitor", "mobile", "spelling", "education"],
  "author": "BeeSmart Team",
  "license": "MIT"
}
"@

$packageJson | Out-File -FilePath "package.json" -Encoding UTF8

# Install Capacitor core
Write-Host ""
Write-Host "📦 Installing Capacitor dependencies..." -ForegroundColor Cyan
npm install @capacitor/core @capacitor/cli

# Create www directory (placeholder)
Write-Host ""
Write-Host "📁 Creating www directory..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "www" | Out-Null

$indexHtml = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BeeSmart Spelling Bee</title>
</head>
<body>
    <h1>🐝 BeeSmart Spelling Bee</h1>
    <p>This is a placeholder. The app will load from Railway.</p>
</body>
</html>
"@

$indexHtml | Out-File -FilePath "www\index.html" -Encoding UTF8

# Create capacitor.config.json
Write-Host ""
Write-Host "⚙️  Creating Capacitor configuration..." -ForegroundColor Cyan

$capacitorConfig = @"
{
  "appId": "com.beesmart.spellingbee",
  "appName": "BeeSmart Spelling Bee",
  "webDir": "www",
  "bundledWebRuntime": false,
  "server": {
    "url": "https://beesmart.up.railway.app",
    "cleartext": false,
    "allowNavigation": [
      "beesmart.up.railway.app",
      "*.railway.app"
    ]
  },
  "ios": {
    "contentInset": "automatic",
    "scheme": "BeeSmart"
  },
  "android": {
    "allowMixedContent": false,
    "backgroundColor": "#FFD700"
  },
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 2000,
      "backgroundColor": "#FFD700",
      "androidScaleType": "CENTER_CROP",
      "showSpinner": true,
      "spinnerColor": "#000000"
    }
  }
}
"@

$capacitorConfig | Out-File -FilePath "capacitor.config.json" -Encoding UTF8

Write-Host ""
Write-Host "✅ Capacitor configuration created" -ForegroundColor Green

# Install platform packages
Write-Host ""
Write-Host "📱 Installing iOS and Android platforms..." -ForegroundColor Cyan
npm install @capacitor/ios @capacitor/android

# Add platforms
Write-Host ""
Write-Host "🍎 Adding iOS platform..." -ForegroundColor Cyan
npx cap add ios

Write-Host ""
Write-Host "🤖 Adding Android platform..." -ForegroundColor Cyan
npx cap add android

# Sync
Write-Host ""
Write-Host "🔄 Syncing platforms..." -ForegroundColor Cyan
npx cap sync

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ BeeSmart Mobile Wrapper Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open iOS project in Xcode:" -ForegroundColor White
Write-Host "   npm run open:ios" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Open Android project in Android Studio:" -ForegroundColor White
Write-Host "   npm run open:android" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Configure signing certificates:" -ForegroundColor White
Write-Host "   iOS: Import ios_distribution.cer and BeeSmartAppStoreProfile.mobileprovision" -ForegroundColor Cyan
Write-Host "   Android: Create keystore in Android Studio" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Build and test on simulators/emulators" -ForegroundColor White
Write-Host ""
Write-Host "5. Archive and submit to App Store / Play Store" -ForegroundColor White
Write-Host ""
Write-Host "📚 Full documentation: MOBILE_WRAPPER_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
