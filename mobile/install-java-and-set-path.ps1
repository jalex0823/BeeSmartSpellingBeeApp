# Install Java (JDK 17) via winget if missing, then set JAVA_HOME and PATH.
# Run in PowerShell (Admin not required for user install). Dot-source to keep env in session: . .\install-java-and-set-path.ps1

$ErrorActionPreference = "Stop"

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

# 1) Check if Java already works
$existing = Find-Jdk
if ($existing) {
    $env:JAVA_HOME = $existing
    $env:Path = "$env:JAVA_HOME\bin;" + $env:Path
    Write-Host "Java already installed. JAVA_HOME set to: $env:JAVA_HOME" -ForegroundColor Green
    $ver = & "$env:JAVA_HOME\bin\java.exe" -version 2>&1 | Out-String
    Write-Host $ver.Trim()
    Write-Host "Run .\build-aab.ps1 in this same window to build the AAB." -ForegroundColor Cyan
    return
}

# 2) Check for java in PATH
$javaExe = Get-Command java -ErrorAction SilentlyContinue
if ($javaExe) {
    Write-Host "Java found in PATH. Setting JAVA_HOME from java.exe path..." -ForegroundColor Yellow
    $javaDir = (Get-Item $javaExe.Source).Directory.Parent.FullName
    $env:JAVA_HOME = $javaDir
    $env:Path = "$env:JAVA_HOME\bin;" + $env:Path
    $ver = & java -version 2>&1 | Out-String
    Write-Host $ver.Trim()
    Write-Host "Run .\build-aab.ps1 in this same window to build the AAB." -ForegroundColor Cyan
    return
}

# 3) Install JDK via winget
Write-Host "No JDK found. Installing Eclipse Temurin JDK 17 via winget..." -ForegroundColor Yellow
$winget = Get-Command winget -ErrorAction SilentlyContinue
if (-not $winget) {
    Write-Host "ERROR: winget not found. Install Windows 10/11 App Installer (winget) or install JDK 17 manually from https://adoptium.net/" -ForegroundColor Red
    exit 1
}

& winget install EclipseAdoptium.Temurin.17.JDK --accept-package-agreements --accept-source-agreements
if ($LASTEXITCODE -ne 0) {
    Write-Host "winget install failed. Try: winget install Microsoft.OpenJDK.17 --accept-package-agreements" -ForegroundColor Yellow
    & winget install Microsoft.OpenJDK.17 --accept-package-agreements --accept-source-agreements
}

# Refresh env so we see the new install (winget may add to user PATH)
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

# 4) Find and set JAVA_HOME
$found = Find-Jdk
if (-not $found) {
    Write-Host "JDK may have been installed. Close and reopen PowerShell, then run: . .\set-java.ps1" -ForegroundColor Yellow
    Write-Host "Or set JAVA_HOME manually after finding the install folder under 'C:\Program Files\Eclipse Adoptium\' or 'C:\Program Files\Microsoft\'." -ForegroundColor Gray
    exit 1
}

$env:JAVA_HOME = $found
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path

# Optional: persist for current user (so new terminals have Java)
[Environment]::SetEnvironmentVariable("JAVA_HOME", $found, "User")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$env:JAVA_HOME\bin*") {
    [Environment]::SetEnvironmentVariable("Path", "$env:JAVA_HOME\bin;" + $userPath, "User")
}

Write-Host "JAVA_HOME set to: $env:JAVA_HOME (saved for your user)" -ForegroundColor Green
$ver = & "$env:JAVA_HOME\bin\java.exe" -version 2>&1 | Out-String
Write-Host $ver.Trim()
Write-Host "Run .\build-aab.ps1 in this same window to build the AAB. New terminals will also have Java in PATH." -ForegroundColor Cyan
