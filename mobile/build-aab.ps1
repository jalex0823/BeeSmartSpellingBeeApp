# Build Android App Bundle (AAB) for Google Play
# Ensures Java is installed/set, syncs web assets (if npm available), then builds AAB.
# Run from repo root or from mobile folder: .\build-aab.ps1
#
# Version for this build (injected into app/build.gradle before building so AAB always has correct version)
$VersionCode = 29
$VersionName = "5.9.14"

$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = (Get-Location).Path }
$mobileDir = if (Test-Path (Join-Path $scriptDir "capacitor.config.ts")) { $scriptDir } else { Join-Path (Split-Path -Parent $scriptDir) "mobile" }
$androidDir = Join-Path $mobileDir "android"
# If path is wrong (e.g. run from system32), assume current directory is mobile
if (-not (Test-Path $androidDir)) {
    $cwd = (Get-Location).Path
    $altAndroid = Join-Path $cwd "android"
    if ((Test-Path (Join-Path $cwd "capacitor.config.ts")) -and (Test-Path $altAndroid)) {
        $mobileDir = $cwd
        $androidDir = $altAndroid
    } else {
        Write-Host "ERROR: Android folder not found. Run this script from the mobile folder:" -ForegroundColor Red
        Write-Host '  cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"' -ForegroundColor Yellow
        Write-Host "  .\build-aab.ps1" -ForegroundColor Yellow
        exit 1
    }
}

function Find-Jdk {
    $searchPaths = @(
        "C:\Program Files\Eclipse Adoptium\jdk-17*",
        "C:\Program Files\Microsoft\jdk-17*",
        "C:\Program Files\Java\jdk-17*",
        "C:\Program Files\Amazon Corretto\jdk17*",
        "C:\Program Files\Zulu\zulu-17*",
        "C:\Program Files\Eclipse Adoptium\jdk-11*",
        "C:\Program Files\Microsoft\jdk-11*",
        "C:\Program Files\Java\jdk-11*"
    )
    foreach ($pattern in $searchPaths) {
        $dirs = Get-Item -Path $pattern -ErrorAction SilentlyContinue | Sort-Object -Property Name -Descending
        if ($dirs) {
            return $dirs[0].FullName
        }
    }
    return $null
}

function Ensure-Java {
    # 1) Already have JAVA_HOME and java works
    if ($env:JAVA_HOME -and (Test-Path (Join-Path $env:JAVA_HOME "bin\java.exe"))) {
        $env:Path = "$env:JAVA_HOME\bin;" + $env:Path
        return $true
    }
    # 2) Find JDK in common locations
    $found = Find-Jdk
    if ($found) {
        $env:JAVA_HOME = $found
        $env:Path = "$env:JAVA_HOME\bin;" + $env:Path
        return $true
    }
    # 3) java in PATH
    $javaExe = Get-Command java -ErrorAction SilentlyContinue
    if ($javaExe) {
        $javaDir = (Get-Item $javaExe.Source).Directory.Parent.FullName
        $env:JAVA_HOME = $javaDir
        $env:Path = "$env:JAVA_HOME\bin;" + $env:Path
        return $true
    }
    # 4) Install via winget
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        Write-Host "ERROR: No JDK found and winget not available. Install JDK 17 from https://adoptium.net/ then run this script again." -ForegroundColor Red
        return $false
    }
    Write-Host "No JDK found. Installing Eclipse Temurin JDK 17 via winget..." -ForegroundColor Yellow
    & winget install EclipseAdoptium.Temurin.17.JDK --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        & winget install Microsoft.OpenJDK.17 --accept-package-agreements --accept-source-agreements
    }
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    $found = Find-Jdk
    if (-not $found) {
        Write-Host "JDK may have been installed. Close and reopen PowerShell, then run this script again." -ForegroundColor Yellow
        return $false
    }
    $env:JAVA_HOME = $found
    $env:Path = "$env:JAVA_HOME\bin;" + $env:Path
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $found, "User")
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$env:JAVA_HOME\bin*") {
        [Environment]::SetEnvironmentVariable("Path", "$env:JAVA_HOME\bin;" + $userPath, "User")
    }
    return $true
}

# --- Ensure Java ---
if (-not (Ensure-Java)) { exit 1 }
$javaSrc = if ($env:JAVA_HOME) { $env:JAVA_HOME } else { "from PATH" }
Write-Host "Java: $javaSrc" -ForegroundColor Green
$ver = cmd /c "`"$env:JAVA_HOME\bin\java.exe`" -version 2>&1"
Write-Host $ver

# --- Optional: sync web assets ---
# For production wrapper builds that load from server.url, a web build step may not exist/needed.
# Only run `npm run build` if the script exists; still allow `npx cap sync android` when available.
$npm = Get-Command npm -ErrorAction SilentlyContinue
if ($npm) {
    Set-Location $mobileDir
    $hasBuildScript = $false
    try {
        if (Test-Path (Join-Path $mobileDir "package.json")) {
            $pkg = Get-Content (Join-Path $mobileDir "package.json") -Raw | ConvertFrom-Json
            if ($pkg -and $pkg.scripts -and $pkg.scripts.build) { $hasBuildScript = $true }
        }
    } catch { $hasBuildScript = $false }

    if ($hasBuildScript) {
        Write-Host "Syncing web assets (npm run build + cap sync)..." -ForegroundColor Yellow
        npm run build 2>&1 | Out-Null
    } else {
        Write-Host "No npm build script found; skipping web build step." -ForegroundColor Yellow
    }

    try {
        npx cap sync android 2>&1 | Out-Null
    } catch {
        Write-Host "Skipping cap sync (npx/capacitor not available). Using existing android assets." -ForegroundColor Yellow
    }
} else {
    Write-Host "Skipping sync (npm not in PATH). Using existing android assets." -ForegroundColor Yellow
}

# --- Require Capacitor sync output (Gradle will fail without it) ---
$cordovaVars = Join-Path $androidDir "capacitor-cordova-android-plugins\cordova.variables.gradle"
if (-not (Test-Path $cordovaVars)) {
    Write-Host ""
    Write-Host "ERROR: Capacitor Android plugins not synced. Gradle needs files from 'npx cap sync android'." -ForegroundColor Red
    Write-Host "Run these commands in a terminal where Node/npm are in PATH:" -ForegroundColor Yellow
    Write-Host '  cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"' -ForegroundColor White
    Write-Host "  npm run build" -ForegroundColor White
    Write-Host "  npx cap sync android" -ForegroundColor White
    Write-Host "Then run .\build-aab.ps1 again." -ForegroundColor Yellow
    exit 1
}

# --- Windows/OneDrive fix: clear ReadOnly attribute under node_modules ---
# Some environments mark directories under node_modules as ReadOnly, which can cause Gradle tasks
# (e.g. processReleaseNavigationResources) to fail when trying to delete generated output dirs.
try {
    $capDir = Join-Path $mobileDir "node_modules\@capacitor"
    if (Test-Path $capDir) {
        Write-Host "Clearing ReadOnly attributes under node_modules\\@capacitor (Windows fix)..." -ForegroundColor Yellow
        cmd /c "attrib -R /S /D `"$capDir\*`"" 2>&1 | Out-Null
    }
} catch {}

# --- Inject version into app/build.gradle so AAB always has correct version ---
$buildGradlePath = Join-Path $androidDir "app\build.gradle"
$buildGradleContent = Get-Content $buildGradlePath -Raw -ErrorAction SilentlyContinue
$buildGradleContent = $buildGradleContent -replace "versionCode \d+", "versionCode $VersionCode"
$buildGradleContent = $buildGradleContent -replace 'versionName "[^"]+"', "versionName `"$VersionName`""
Set-Content -Path $buildGradlePath -Value $buildGradleContent -NoNewline
Write-Host "Version: versionCode $VersionCode, versionName `"$VersionName`"" -ForegroundColor Cyan

# --- Build AAB (clean so version/asset changes are picked up) ---
Write-Host "Building AAB (clean + bundleRelease)..." -ForegroundColor Yellow
Set-Location $androidDir
& .\gradlew.bat --no-daemon clean bundleRelease
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$aabPath = Join-Path $androidDir "app\build\outputs\bundle\release\app-release.aab"
if (Test-Path $aabPath) {
    Write-Host ""
    Write-Host "SUCCESS: AAB created (signed with upload keystore)" -ForegroundColor Green
    Write-Host "  $aabPath" -ForegroundColor White

    # Copy to a dedicated upload folder so you can upload directly from there
    $uploadDir = Join-Path $mobileDir "release-upload"
    if (-not (Test-Path $uploadDir)) { New-Item -ItemType Directory -Path $uploadDir -Force | Out-Null }
    $uploadAab = Join-Path $uploadDir "app-release.aab"
    Copy-Item -Path $aabPath -Destination $uploadAab -Force
    Write-Host ""
    Write-Host "Copy for upload:" -ForegroundColor Cyan
    Write-Host "  $uploadAab" -ForegroundColor White
    Write-Host "Upload this file in Google Play Console (Release > Create new release)." -ForegroundColor Gray
    # Open the folder so you can drag the AAB to Play Console
    Start-Process explorer.exe -ArgumentList "/select,`"$uploadAab`""
} else {
    Write-Host "AAB not found at expected path." -ForegroundColor Red
    exit 1
}
