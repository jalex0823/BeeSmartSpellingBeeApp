# BeeSmart App Quick Diagnostic
# PowerShell script to test all major routes

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  BeeSmart Spelling Bee - Quick Diagnostic" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$baseUrl = "http://127.0.0.1:5000"
$passed = 0
$failed = 0
$total = 0

function Test-Route {
    param(
        [string]$name,
        [string]$url,
        [int]$expectedStatus = 200
    )
    
    $script:total++
    Write-Host "Testing: $name... " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq $expectedStatus) {
            Write-Host "✅ PASS (Status: $($response.StatusCode))" -ForegroundColor Green
            $script:passed++
            return $true
        } else {
            Write-Host "❌ FAIL (Expected: $expectedStatus, Got: $($response.StatusCode))" -ForegroundColor Red
            $script:failed++
            return $false
        }
    } catch {
        Write-Host "❌ FAIL (Error: $($_.Exception.Message.Substring(0, [Math]::Min(50, $_.Exception.Message.Length))))" -ForegroundColor Red
        $script:failed++
        return $false
    }
}

# Test Health Check First
Write-Host "`n[Connectivity Check]" -ForegroundColor Yellow
if (-not (Test-Route "Health Check" "$baseUrl/health")) {
    Write-Host "`n❌ ERROR: Cannot connect to Flask app at $baseUrl" -ForegroundColor Red
    Write-Host "Please ensure Flask is running: python AjaSpellBApp.py`n" -ForegroundColor Yellow
    exit 1
}

# Section 1: Public Routes
Write-Host "`n[Public Routes]" -ForegroundColor Yellow
Test-Route "Homepage" "$baseUrl/"
Test-Route "Login Page" "$baseUrl/auth/login"
Test-Route "Register Page" "$baseUrl/auth/register"
Test-Route "Quiz Page" "$baseUrl/quiz"
Test-Route "Upload Page" "$baseUrl/upload"

# Section 2: Static Files
Write-Host "`n[Static Files]" -ForegroundColor Yellow
Test-Route "CSS File" "$baseUrl/static/css/BeeSmart.css"
Test-Route "JavaScript" "$baseUrl/static/js/smarty-bee-3d.js"
Test-Route "Logo Image" "$baseUrl/static/BeeSmartTitle.png"

# Section 3: API Endpoints
Write-Host "`n[API Endpoints - GET]" -ForegroundColor Yellow
Test-Route "Get Wordbank" "$baseUrl/api/wordbank"
Test-Route "Saved Lists" "$baseUrl/api/saved-lists"

# Section 4: File System
Write-Host "`n[Critical Files]" -ForegroundColor Yellow
$criticalFiles = @(
    "AjaSpellBApp.py",
    "models.py",
    "dictionary_api.py",
    "50Words_kidfriendly.txt",
    "data\dictionary.json",
    "templates\quiz.html",
    "static\css\BeeSmart.css"
)

foreach ($file in $criticalFiles) {
    $total++
    Write-Host "Checking: $file... " -NoNewline
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "✅ PASS (Size: $size bytes)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌ FAIL (Not found)" -ForegroundColor Red
        $failed++
    }
}

# Final Report
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "           DIAGNOSTIC REPORT" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`nTotal Tests: $total"
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

$successRate = [math]::Round(($passed / $total) * 100, 1)
Write-Host "`nSuccess Rate: $successRate%"

if ($successRate -ge 90) {
    Write-Host "`n🎉 EXCELLENT! App is functioning properly!" -ForegroundColor Green
} elseif ($successRate -ge 75) {
    Write-Host "`n⚠️  GOOD, but some issues detected" -ForegroundColor Yellow
} else {
    Write-Host "`n⚠️  CRITICAL: Multiple failures detected!" -ForegroundColor Red
}

Write-Host "`n============================================`n" -ForegroundColor Cyan
