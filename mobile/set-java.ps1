# Set JAVA_HOME and PATH for this PowerShell session so Gradle/Java work.
# Run this once in your terminal, then run .\build-aab.ps1 in the same window.
# Usage: . .\set-java.ps1   (dot-source to keep env in current session)

$ErrorActionPreference = "Stop"

# Common JDK 17 install locations on Windows (adjust if your JDK is elsewhere)
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

$found = $null
foreach ($pattern in $searchPaths) {
    $dirs = Get-Item -Path $pattern -ErrorAction SilentlyContinue | Sort-Object -Property Name -Descending
    if ($dirs) {
        $found = $dirs[0].FullName
        break
    }
}

if (-not $found) {
    Write-Host "No JDK 17/11 found in common locations." -ForegroundColor Red
    Write-Host "Install JDK 17 from https://adoptium.net/ or set JAVA_HOME manually:" -ForegroundColor Yellow
    Write-Host '  $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.13.11-hotspot"' -ForegroundColor Gray
    Write-Host '  $env:Path = "$env:JAVA_HOME\bin;" + $env:Path' -ForegroundColor Gray
    exit 1
}

$env:JAVA_HOME = $found
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path

# Verify (java -version writes to stderr; capture and print so PowerShell doesn't show as error)
$version = & "$env:JAVA_HOME\bin\java.exe" -version 2>&1 | Out-String
Write-Host "JAVA_HOME set to: $env:JAVA_HOME" -ForegroundColor Green
Write-Host $version.Trim()
Write-Host "Run .\build-aab.ps1 in this same window to build the AAB." -ForegroundColor Cyan
