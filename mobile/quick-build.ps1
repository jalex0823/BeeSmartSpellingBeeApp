# Quick Build - Generate keystore and build in one go
# Run this AFTER opening project in Android Studio at least once

Write-Host "BeeSmart - Quick Build Setup" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right place
if (-not (Test-Path "android")) {
    Write-Host "Error: Run this from the mobile folder" -ForegroundColor Red
    exit 1
}

Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  1. Generate a keystore for signing" -ForegroundColor White
Write-Host "  2. Build a release AAB for Play Store" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Continue? (yes/no)"
if ($continue -ne "yes") {
    Write-Host "Aborted" -ForegroundColor Red
    exit 0
}

# Step 1: Generate keystore
Write-Host "`nStep 1: Generating keystore..." -ForegroundColor Cyan
cd android

# Try to find keytool
$keytoolPaths = @(
    "$env:LOCALAPPDATA\Android\Sdk\jbr\bin\keytool.exe",
    "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe",
    "C:\Program Files\Android\Android Studio1\jbr\bin\keytool.exe"
)

$keytool = $null
foreach ($path in $keytoolPaths) {
    if (Test-Path $path) {
        $keytool = $path
        break
    }
}

if (-not $keytool) {
    Write-Host "Error: keytool not found" -ForegroundColor Red
    Write-Host "Please complete Android Studio setup first" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found keytool: $keytool" -ForegroundColor Green
Write-Host ""
Write-Host "Enter keystore details (save these passwords!):" -ForegroundColor Yellow

# Generate keystore if it doesn't exist
if (-not (Test-Path "upload-keystore.jks")) {
    & $keytool -genkey -v `
        -keystore upload-keystore.jks `
        -keyalg RSA `
        -keysize 2048 `
        -validity 10000 `
        -alias upload
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Keystore generation failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "`nKeystore created!" -ForegroundColor Green
} else {
    Write-Host "Keystore already exists, skipping..." -ForegroundColor Yellow
}

# Step 2: Create keystore.properties
Write-Host "`nStep 2: Configure signing..." -ForegroundColor Cyan
if (-not (Test-Path "keystore.properties")) {
    Write-Host "Enter your keystore password:" -ForegroundColor Yellow
    $storePass = Read-Host -AsSecureString
    $storePassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($storePass))
    
    Write-Host "Enter your key password (can be same):" -ForegroundColor Yellow
    $keyPass = Read-Host -AsSecureString
    $keyPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($keyPass))
    
    @"
storePassword=$storePassPlain
keyPassword=$keyPassPlain
keyAlias=upload
storeFile=upload-keystore.jks
"@ | Set-Content keystore.properties
    
    Write-Host "Signing configured!" -ForegroundColor Green
} else {
    Write-Host "Signing already configured, skipping..." -ForegroundColor Yellow
}

# Step 3: Build
Write-Host "`nStep 3: Building release AAB..." -ForegroundColor Cyan
Write-Host "This may take several minutes..." -ForegroundColor Gray
Write-Host ""

.\gradlew bundleRelease

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==================================" -ForegroundColor Green
    Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your AAB is ready at:" -ForegroundColor Cyan
    Write-Host "  app\build\outputs\bundle\release\app-release.aab" -ForegroundColor White
    Write-Host ""
    Write-Host "Next: Upload to Google Play Console!" -ForegroundColor Yellow
} else {
    Write-Host "`nBuild failed. Check errors above." -ForegroundColor Red
}
