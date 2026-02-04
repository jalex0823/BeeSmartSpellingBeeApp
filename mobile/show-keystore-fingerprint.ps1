# BeeSmart - Show SHA1 fingerprint of the keystore used for release signing
# Use this to verify your keystore matches what Google Play Console expects.
# Play expects: SHA1 EF:B0:34:20:AD:97:54:1B:C8:52:1C:13:4F:1B:08:68:11:CC:9B:13

$ErrorActionPreference = "Stop"
$mobileRoot = $PSScriptRoot
$androidDir = Join-Path $mobileRoot "android"
$propsPath = Join-Path $androidDir "keystore.properties"

if (-not (Test-Path $propsPath)) {
    Write-Host "keystore.properties not found at: $propsPath" -ForegroundColor Red
    Write-Host "Create it with .\setup-signing.ps1 or see MANUAL_KEYSTORE_SETUP.md" -ForegroundColor Yellow
    exit 1
}

$props = @{}
Get-Content $propsPath | ForEach-Object {
    if ($_ -match "^\s*([^#=]+)=(.*)$") {
        $props[$matches[1].Trim()] = $matches[2].Trim()
    }
}

$storeFile = $props["storeFile"]
$keyAlias = $props["keyAlias"]
if (-not $storeFile -or -not $keyAlias) {
    Write-Host "keystore.properties must set storeFile and keyAlias" -ForegroundColor Red
    exit 1
}

# storeFile in build.gradle is relative to android/
$keystorePath = Join-Path $androidDir $storeFile
if (-not (Test-Path $keystorePath)) {
    Write-Host "Keystore file not found: $keystorePath" -ForegroundColor Red
    exit 1
}

Write-Host "Keystore: $keystorePath" -ForegroundColor Cyan
Write-Host "Alias: $keyAlias" -ForegroundColor Cyan
Write-Host ""
Write-Host "Google Play expects this certificate SHA1:" -ForegroundColor Yellow
Write-Host "  EF:B0:34:20:AD:97:54:1B:C8:52:1C:13:4F:1B:08:68:11:CC:9B:13" -ForegroundColor White
Write-Host ""
Write-Host "Your keystore fingerprint (you will be prompted for keystore password):" -ForegroundColor Yellow
Write-Host ""

# Find keytool
$keytoolPaths = @(
    "$env:LOCALAPPDATA\Android\Sdk\jbr\bin\keytool.exe",
    "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe",
    "$env:JAVA_HOME\bin\keytool.exe"
)
$keytool = $null
foreach ($p in $keytoolPaths) {
    if ($p -and (Test-Path $p)) { $keytool = $p; break }
}
if (-not $keytool) {
    $keytool = "keytool"
}

& $keytool -list -v -keystore $keystorePath -alias $keyAlias 2>&1 | ForEach-Object {
    $line = $_
    Write-Host $line
    if ($line -match "SHA1:\s*([0-9A-F:]+)") {
        $sha1 = $matches[1]
        Write-Host ""
        if ($sha1 -eq "EF:B0:34:20:AD:97:54:1B:C8:52:1C:13:4F:1B:08:68:11:CC:9B:13") {
            Write-Host "MATCH: This keystore is the one Play expects. You can upload AABs signed with it." -ForegroundColor Green
        } else {
            Write-Host "MISMATCH: This keystore has a different fingerprint. Play will reject AABs signed with it." -ForegroundColor Red
            Write-Host "Use the keystore that has SHA1 EF:B0:34:20:... or see PLAY_STORE_WRONG_KEY.md" -ForegroundColor Yellow
        }
    }
}
