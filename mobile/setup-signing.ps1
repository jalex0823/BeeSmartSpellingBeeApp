# BeeSmart Spelling Bee - Configure Android Signing
# Run this after creating your keystore with setup-keystore.ps1

Write-Host "🔐 BeeSmart Spelling Bee - Configure Android Signing" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$androidPath = Join-Path $PSScriptRoot "android"
$keystorePath = Join-Path $androidPath "upload-keystore.jks"
$keystorePropsPath = Join-Path $androidPath "keystore.properties"

# Check if keystore exists
if (-not (Test-Path $keystorePath)) {
    Write-Host "❌ Error: Keystore not found at:" -ForegroundColor Red
    Write-Host "   $keystorePath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "👉 Run setup-keystore.ps1 first to generate the keystore" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found keystore: upload-keystore.jks" -ForegroundColor Green
Write-Host ""

# Check if keystore.properties already exists
if (Test-Path $keystorePropsPath) {
    Write-Host "⚠️  Warning: keystore.properties already exists" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite it? (yes/no)"
    if ($overwrite -ne "yes") {
        Write-Host "❌ Aborted - keeping existing configuration" -ForegroundColor Red
        exit 0
    }
}

# Get passwords
Write-Host "📝 Enter your keystore credentials:" -ForegroundColor Cyan
Write-Host ""
$storePassword = Read-Host "Keystore password" -AsSecureString
$keyPassword = Read-Host "Key password" -AsSecureString

# Convert secure strings to plain text (needed for properties file)
$storePwd = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($storePassword))
$keyPwd = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($keyPassword))

# Create keystore.properties
$properties = @"
storePassword=$storePwd
keyPassword=$keyPwd
keyAlias=upload
storeFile=upload-keystore.jks
"@

Set-Content -Path $keystorePropsPath -Value $properties -NoNewline

Write-Host ""
Write-Host "✅ Created keystore.properties" -ForegroundColor Green
Write-Host ""

# Update .gitignore
$gitignorePath = Join-Path $androidPath ".gitignore"
$gitignoreEntries = @(
    "upload-keystore.jks",
    "keystore.properties"
)

if (Test-Path $gitignorePath) {
    $currentGitignore = Get-Content $gitignorePath -Raw
    $needsUpdate = $false
    
    foreach ($entry in $gitignoreEntries) {
        if ($currentGitignore -notmatch [regex]::Escape($entry)) {
            Add-Content -Path $gitignorePath -Value "`n$entry"
            $needsUpdate = $true
        }
    }
    
    if ($needsUpdate) {
        Write-Host "✅ Updated android/.gitignore" -ForegroundColor Green
    } else {
        Write-Host "✅ android/.gitignore already configured" -ForegroundColor Green
    }
} else {
    $gitignoreEntries | Set-Content -Path $gitignorePath
    Write-Host "✅ Created android/.gitignore" -ForegroundColor Green
}

# Update build.gradle
$buildGradlePath = Join-Path $androidPath "app\build.gradle"
if (Test-Path $buildGradlePath) {
    $buildGradle = Get-Content $buildGradlePath -Raw
    
    if ($buildGradle -notmatch "keystoreProperties") {
        Write-Host ""
        Write-Host "⚠️  build.gradle needs manual configuration" -ForegroundColor Yellow
        Write-Host "   See ANDROID_PACKAGING_GUIDE.md Step 6 for details" -ForegroundColor White
        Write-Host ""
        Write-Host "   Or run: code android\app\build.gradle" -ForegroundColor Cyan
    } else {
        Write-Host "✅ build.gradle already configured for signing" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🎉 Signing configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Run: npm run cap:sync" -ForegroundColor White
Write-Host "   2. Open Android Studio: npm run cap:open:android" -ForegroundColor White
Write-Host "   3. Build release: .\gradlew bundleRelease" -ForegroundColor White
Write-Host ""
Write-Host "   Or use the automated build script: .\build-release.ps1" -ForegroundColor Cyan
Write-Host ""
