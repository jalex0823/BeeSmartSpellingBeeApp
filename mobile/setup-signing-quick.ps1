# Quick non-interactive signing setup for Play Store
# Generates keystore and keystore.properties, saves password to KEYSTORE_PASSWORD.txt

$ErrorActionPreference = "Stop"
$androidPath = Join-Path $PSScriptRoot "android"
Set-Location $androidPath

$keystorePath = "upload-keystore.jks"
$propsPath = "keystore.properties"

# Generate random password (16 chars)
$password = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object { [char]$_ })

if (Test-Path $keystorePath) {
    Write-Host "Keystore already exists - using existing" -ForegroundColor Yellow
} else {
    Write-Host "Generating keystore..." -ForegroundColor Cyan
    $keytool = "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe"
    if (-not (Test-Path $keytool)) {
        $keytool = "keytool"  # fallback to PATH
    }
    & $keytool -genkey -v -keystore $keystorePath -keyalg RSA -keysize 2048 -validity 10000 `
        -alias upload -storepass $password -keypass $password `
        -dname "CN=BeeSmart, OU=Dev, O=BeeSmart, L=City, ST=State, C=US"
    if ($LASTEXITCODE -ne 0) { exit 1 }
    Write-Host "Keystore created" -ForegroundColor Green
}

# Create keystore.properties
$properties = @"
storePassword=$password
keyPassword=$password
keyAlias=upload
storeFile=upload-keystore.jks
"@
Set-Content -Path $propsPath -Value $properties -NoNewline

# Save password for user
$pwdFile = Join-Path $PSScriptRoot "KEYSTORE_PASSWORD.txt"
"Keystore and key password (save this for future releases):" | Out-File $pwdFile
$password | Out-File $pwdFile -Append
Write-Host "Password saved to: $pwdFile" -ForegroundColor Yellow
Write-Host "Signing configured - ready to build" -ForegroundColor Green
