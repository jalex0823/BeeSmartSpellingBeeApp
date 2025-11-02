# BeeSmart - Find and Use Java keytool from Android Studio
# This script locates keytool from Android Studio installation

Write-Host "Searching for Java keytool..." -ForegroundColor Cyan
Write-Host ""

# Common Android Studio JDK locations
$possiblePaths = @(
    "$env:LOCALAPPDATA\Android\Sdk\jbr\bin\keytool.exe",
    "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe",
    "$env:ProgramFiles\Android\Android Studio\jbr\bin\keytool.exe",
    "$env:JAVA_HOME\bin\keytool.exe"
)

$keytoolPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $keytoolPath = $path
        Write-Host "Found keytool at: $path" -ForegroundColor Green
        break
    }
}

if (-not $keytoolPath) {
    Write-Host "keytool not found in common locations." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Android Studio may not be fully installed yet." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please complete Android Studio installation, then:" -ForegroundColor Cyan
    Write-Host "   1. Open Android Studio" -ForegroundColor White
    Write-Host "   2. Go to File > Settings > Build, Execution, Deployment > Build Tools > Gradle" -ForegroundColor White
    Write-Host "   3. Note the JDK location" -ForegroundColor White
    Write-Host "   4. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "Or manually add to PATH:" -ForegroundColor Cyan
    Write-Host "   `$env:PATH += ';C:\path\to\Android Studio\jbr\bin'" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Testing keytool..." -ForegroundColor Cyan
& $keytoolPath -help | Select-Object -First 3
Write-Host ""
Write-Host "keytool is working!" -ForegroundColor Green
Write-Host ""
Write-Host "Path to use: $keytoolPath" -ForegroundColor White
