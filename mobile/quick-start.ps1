# BeeSmart Spelling Bee - Quick Start Script
# Complete setup wizard for Android packaging

Write-Host ""
Write-Host "🐝 BeeSmart Spelling Bee - Android Packaging Setup Wizard" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

function Show-Menu {
    Write-Host "What would you like to do?" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. 🔐 Generate keystore (first-time setup)" -ForegroundColor White
    Write-Host "  2. ⚙️  Configure signing (after keystore creation)" -ForegroundColor White
    Write-Host "  3. 🔨 Build release AAB for Play Store" -ForegroundColor White
    Write-Host "  4. 📱 Build release APK for testing" -ForegroundColor White
    Write-Host "  5. 🔄 Sync Capacitor only" -ForegroundColor White
    Write-Host "  6. 🚀 Open Android Studio" -ForegroundColor White
    Write-Host "  7. 📊 Check build status" -ForegroundColor White
    Write-Host "  8. 📚 View documentation" -ForegroundColor White
    Write-Host "  9. ❌ Exit" -ForegroundColor White
    Write-Host ""
}

function Check-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
    $allGood = $true
    
    # Check if in mobile folder
    if (-not (Test-Path "capacitor.config.ts")) {
        Write-Host "❌ Not in mobile folder" -ForegroundColor Red
        Write-Host "   Run: cd mobile" -ForegroundColor Yellow
        $allGood = $false
    } else {
        Write-Host "✅ In mobile folder" -ForegroundColor Green
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version
        Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Node.js not found" -ForegroundColor Red
        $allGood = $false
    }
    
    # Check Java
    try {
        $javaVersion = java -version 2>&1 | Select-Object -First 1
        Write-Host "✅ Java: $javaVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Java not found (needed for keytool)" -ForegroundColor Yellow
    }
    
    # Check Android Studio / SDK
    $androidHome = $env:ANDROID_HOME
    if ($androidHome -and (Test-Path $androidHome)) {
        Write-Host "✅ Android SDK: $androidHome" -ForegroundColor Green
    } else {
        Write-Host "⚠️  ANDROID_HOME not set" -ForegroundColor Yellow
        Write-Host "   Install Android Studio first" -ForegroundColor Gray
    }
    
    # Check keystore
    if (Test-Path "android\upload-keystore.jks") {
        Write-Host "✅ Keystore exists" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Keystore not created yet" -ForegroundColor Yellow
    }
    
    # Check signing config
    if (Test-Path "android\keystore.properties") {
        Write-Host "✅ Signing configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Signing not configured yet" -ForegroundColor Yellow
    }
    
    Write-Host ""
    return $allGood
}

function Show-BuildStatus {
    Write-Host "📊 Build Status Check" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    
    $aabPath = "android\app\build\outputs\bundle\release\app-release.aab"
    $apkPath = "android\app\build\outputs\apk\release\app-release.apk"
    
    if (Test-Path $aabPath) {
        $aabSize = (Get-Item $aabPath).Length / 1MB
        $aabDate = (Get-Item $aabPath).LastWriteTime
        Write-Host "✅ Release AAB found:" -ForegroundColor Green
        Write-Host "   Size: $([math]::Round($aabSize, 2)) MB" -ForegroundColor White
        Write-Host "   Date: $aabDate" -ForegroundColor White
        Write-Host "   Path: $((Get-Item $aabPath).FullName)" -ForegroundColor Gray
    } else {
        Write-Host "❌ No release AAB found" -ForegroundColor Red
    }
    
    Write-Host ""
    
    if (Test-Path $apkPath) {
        $apkSize = (Get-Item $apkPath).Length / 1MB
        $apkDate = (Get-Item $apkPath).LastWriteTime
        Write-Host "✅ Release APK found:" -ForegroundColor Green
        Write-Host "   Size: $([math]::Round($apkSize, 2)) MB" -ForegroundColor White
        Write-Host "   Date: $apkDate" -ForegroundColor White
        Write-Host "   Path: $((Get-Item $apkPath).FullName)" -ForegroundColor Gray
    } else {
        Write-Host "❌ No release APK found" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Main loop
$continue = $true
Check-Prerequisites

while ($continue) {
    Show-Menu
    $choice = Read-Host "Enter choice (1-9)"
    Write-Host ""
    
    switch ($choice) {
        "1" {
            Write-Host "🔐 Launching keystore generation..." -ForegroundColor Cyan
            .\setup-keystore.ps1
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "2" {
            Write-Host "⚙️  Launching signing configuration..." -ForegroundColor Cyan
            .\setup-signing.ps1
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "3" {
            Write-Host "🔨 Building release AAB..." -ForegroundColor Cyan
            .\build-release.ps1
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "4" {
            Write-Host "📱 Building release APK..." -ForegroundColor Cyan
            .\build-release.ps1 -BuildAPK
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "5" {
            Write-Host "🔄 Syncing Capacitor..." -ForegroundColor Cyan
            npm run cap:sync
            Write-Host ""
            Write-Host "✅ Sync complete" -ForegroundColor Green
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "6" {
            Write-Host "🚀 Opening Android Studio..." -ForegroundColor Cyan
            npm run cap:open:android
        }
        "7" {
            Show-BuildStatus
            Read-Host "Press Enter to continue"
        }
        "8" {
            Write-Host "📚 Opening documentation..." -ForegroundColor Cyan
            $docPath = "..\ANDROID_PACKAGING_GUIDE.md"
            if (Test-Path $docPath) {
                code $docPath
            } else {
                Write-Host "❌ Documentation not found" -ForegroundColor Red
            }
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "9" {
            $continue = $false
            Write-Host "👋 Goodbye!" -ForegroundColor Cyan
        }
        default {
            Write-Host "❌ Invalid choice. Please enter 1-9." -ForegroundColor Red
            Write-Host ""
        }
    }
    
    Write-Host ""
}
