# BeeSmart Spelling Bee - Keystore Generation Script
# Run this ONCE to create your Android signing keystore

Write-Host "BeeSmart Spelling Bee - Android Keystore Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to android folder
$androidPath = Join-Path $PSScriptRoot "android"
if (-not (Test-Path $androidPath)) {
    Write-Host "Error: android folder not found at $androidPath" -ForegroundColor Red
    Write-Host "   Make sure you are running this from the mobile folder" -ForegroundColor Yellow
    exit 1
}

Set-Location $androidPath

# Check if keystore already exists
$keystorePath = Join-Path $androidPath "upload-keystore.jks"
if (Test-Path $keystorePath) {
    Write-Host "Warning: Keystore already exists at:" -ForegroundColor Yellow
    Write-Host "   $keystorePath" -ForegroundColor Yellow
    Write-Host ""
    $overwrite = Read-Host "Do you want to overwrite it? (yes/no)"
    if ($overwrite -ne "yes") {
        Write-Host "Aborted - keeping existing keystore" -ForegroundColor Red
        exit 0
    }
    Remove-Item $keystorePath -Force
}

Write-Host "You will be prompted for the following information:" -ForegroundColor Green
Write-Host "   1. Keystore password (choose a strong password)" -ForegroundColor White
Write-Host "   2. Key password (can be same as keystore password)" -ForegroundColor White
Write-Host "   3. Your name" -ForegroundColor White
Write-Host "   4. Organization name (e.g., BeeSmart)" -ForegroundColor White
Write-Host "   5. City, State, Country" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Save these passwords in a secure location!" -ForegroundColor Yellow
Write-Host "   You will need them every time you build a release version." -ForegroundColor Yellow
Write-Host ""

$continue = Read-Host "Ready to generate keystore? (yes/no)"
if ($continue -ne "yes") {
    Write-Host "Aborted" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "Generating keystore..." -ForegroundColor Cyan

# Generate keystore
keytool -genkey -v `
    -keystore upload-keystore.jks `
    -keyalg RSA `
    -keysize 2048 `
    -validity 10000 `
    -alias upload

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Keystore generated successfully!" -ForegroundColor Green
    Write-Host "   Location: $keystorePath" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Create keystore.properties file" -ForegroundColor White
    Write-Host "   2. Add your passwords to keystore.properties" -ForegroundColor White
    Write-Host "   3. Run setup-signing.ps1 to configure signing" -ForegroundColor White
    Write-Host ""
    Write-Host "Security reminder:" -ForegroundColor Yellow
    Write-Host "   - NEVER commit upload-keystore.jks to git" -ForegroundColor White
    Write-Host "   - NEVER commit keystore.properties to git" -ForegroundColor White
    Write-Host "   - Store passwords in a password manager" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Error: Failed to generate keystore" -ForegroundColor Red
    Write-Host "   Make sure Java/keytool is installed and in PATH" -ForegroundColor Yellow
    exit 1
}
