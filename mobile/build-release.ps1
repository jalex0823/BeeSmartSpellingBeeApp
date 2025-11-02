# BeeSmart Spelling Bee - Automated Release Build Script
# This script handles the complete build process for Play Store submission

param(
    [switch]$SkipSync,
    [switch]$SkipClean,
    [switch]$BuildAPK,
    [string]$VersionName,
    [int]$VersionCode
)

Write-Host "🐝 BeeSmart Spelling Bee - Release Build" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$startLocation = Get-Location

try {
    # Check prerequisites
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
    
    # Check if in mobile folder
    if (-not (Test-Path "capacitor.config.ts")) {
        Write-Host "❌ Error: Must run from mobile folder" -ForegroundColor Red
        Write-Host "   cd mobile" -ForegroundColor Yellow
        exit 1
    }
    
    # Check if keystore exists
    $keystorePath = "android\upload-keystore.jks"
    $keystorePropsPath = "android\keystore.properties"
    
    if (-not (Test-Path $keystorePath)) {
        Write-Host "❌ Error: Keystore not found" -ForegroundColor Red
        Write-Host "   Run: .\setup-keystore.ps1" -ForegroundColor Yellow
        exit 1
    }
    
    if (-not (Test-Path $keystorePropsPath)) {
        Write-Host "❌ Error: keystore.properties not found" -ForegroundColor Red
        Write-Host "   Run: .\setup-signing.ps1" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ Prerequisites OK" -ForegroundColor Green
    Write-Host ""
    
    # Update version if specified
    if ($VersionName -or $VersionCode) {
        Write-Host "📝 Updating version information..." -ForegroundColor Yellow
        $buildGradlePath = "android\app\build.gradle"
        $buildGradle = Get-Content $buildGradlePath -Raw
        
        if ($VersionCode) {
            $buildGradle = $buildGradle -replace "versionCode \d+", "versionCode $VersionCode"
            Write-Host "   Version Code: $VersionCode" -ForegroundColor White
        }
        
        if ($VersionName) {
            $buildGradle = $buildGradle -replace 'versionName "[^"]+"', "versionName `"$VersionName`""
            Write-Host "   Version Name: $VersionName" -ForegroundColor White
        }
        
        Set-Content -Path $buildGradlePath -Value $buildGradle -NoNewline
        Write-Host "✅ Version updated" -ForegroundColor Green
        Write-Host ""
    }
    
    # Sync Capacitor
    if (-not $SkipSync) {
        Write-Host "🔄 Syncing Capacitor..." -ForegroundColor Yellow
        npm run cap:sync
        if ($LASTEXITCODE -ne 0) {
            throw "Capacitor sync failed"
        }
        Write-Host "✅ Sync complete" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "⏭️  Skipping Capacitor sync" -ForegroundColor Gray
        Write-Host ""
    }
    
    # Navigate to android folder
    Set-Location "android"
    
    # Clean build (optional)
    if (-not $SkipClean) {
        Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Yellow
        .\gradlew clean
        if ($LASTEXITCODE -ne 0) {
            throw "Clean failed"
        }
        Write-Host "✅ Clean complete" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "⏭️  Skipping clean" -ForegroundColor Gray
        Write-Host ""
    }
    
    # Build
    if ($BuildAPK) {
        Write-Host "🔨 Building Release APK..." -ForegroundColor Yellow
        Write-Host "   (This may take several minutes)" -ForegroundColor Gray
        Write-Host ""
        .\gradlew assembleRelease
        $outputPath = "app\build\outputs\apk\release\app-release.apk"
        $buildType = "APK"
    } else {
        Write-Host "🔨 Building Release AAB (Android App Bundle)..." -ForegroundColor Yellow
        Write-Host "   (This may take several minutes)" -ForegroundColor Gray
        Write-Host ""
        .\gradlew bundleRelease
        $outputPath = "app\build\outputs\bundle\release\app-release.aab"
        $buildType = "AAB"
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed"
    }
    
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host ""
    
    # Show output location
    $fullOutputPath = Join-Path (Get-Location) $outputPath
    if (Test-Path $outputPath) {
        $fileSize = (Get-Item $outputPath).Length / 1MB
        Write-Host "📦 Output file:" -ForegroundColor Cyan
        Write-Host "   Location: $fullOutputPath" -ForegroundColor White
        Write-Host "   Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor White
        Write-Host "   Type: $buildType" -ForegroundColor White
        Write-Host ""
        
        # Open output folder
        $openFolder = Read-Host "Open output folder? (yes/no)"
        if ($openFolder -eq "yes") {
            explorer (Split-Path $fullOutputPath)
        }
        
        # Install APK if built
        if ($BuildAPK) {
            Write-Host ""
            $install = Read-Host "Install on connected device? (yes/no)"
            if ($install -eq "yes") {
                Write-Host "📱 Installing..." -ForegroundColor Yellow
                adb install -r $outputPath
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Installed successfully!" -ForegroundColor Green
                } else {
                    Write-Host "❌ Installation failed" -ForegroundColor Red
                    Write-Host "   Make sure device is connected and USB debugging enabled" -ForegroundColor Yellow
                }
            }
        }
    } else {
        Write-Host "⚠️  Warning: Output file not found at expected location" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎉 Build process complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Test the $buildType thoroughly" -ForegroundColor White
    Write-Host "   2. Upload to Google Play Console" -ForegroundColor White
    Write-Host "   3. Submit for review" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "📚 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   - Check ANDROID_PACKAGING_GUIDE.md" -ForegroundColor White
    Write-Host "   - Verify keystore configuration" -ForegroundColor White
    Write-Host "   - Check build logs above" -ForegroundColor White
    Write-Host ""
    exit 1
} finally {
    Set-Location $startLocation
}
