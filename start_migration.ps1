# BeeSmart Migration Quick Start
# Run this script to get started with the migration

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "BeeSmart Railway → DigitalOcean Migration" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10 or higher." -ForegroundColor Red
    exit 1
}

# Check required packages
Write-Host "`nChecking required packages..." -ForegroundColor Yellow
$requiredPackages = @("psycopg2-binary", "sqlalchemy", "python-dotenv")
foreach ($package in $requiredPackages) {
    $installed = python -c "import pkg_resources; pkg_resources.require('$package')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $package installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $package not installed - will install..." -ForegroundColor Yellow
        pip install $package
    }
}

# Guide user to set environment variables
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 1: Set Environment Variables" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "You need to set two environment variables:`n"

# Check Railway URL
if ($env:RAILWAY_DATABASE_URL -or $env:DATABASE_URL) {
    Write-Host "✅ Railway database URL is set" -ForegroundColor Green
} else {
    Write-Host "❌ Railway database URL not found`n" -ForegroundColor Red
    Write-Host "Get your Railway connection string:"
    Write-Host "1. Go to railway.app → Your Project → PostgreSQL"
    Write-Host "2. Click 'Connect' → Copy 'Postgres Connection URL'`n"
    Write-Host "Then run:" -ForegroundColor Yellow
    Write-Host '  $env:RAILWAY_DATABASE_URL="postgresql://..."' -ForegroundColor Cyan
    Write-Host "`n"
}

# Check DigitalOcean URL
if ($env:DIGITALOCEAN_DATABASE_URL) {
    Write-Host "✅ DigitalOcean database URL is set" -ForegroundColor Green
} else {
    Write-Host "❌ DigitalOcean database URL not found`n" -ForegroundColor Red
    Write-Host "Get your DigitalOcean connection string:"
    Write-Host "1. Go to cloud.digitalocean.com → Databases"
    Write-Host "2. Select your database → Connection Details"
    Write-Host "3. Copy the connection string`n"
    Write-Host "Then run:" -ForegroundColor Yellow
    Write-Host '  $env:DIGITALOCEAN_DATABASE_URL="postgresql://..."' -ForegroundColor Cyan
    Write-Host "`n"
}

# If both are set, offer to start migration
if (($env:RAILWAY_DATABASE_URL -or $env:DATABASE_URL) -and $env:DIGITALOCEAN_DATABASE_URL) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Ready to Migrate!" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "Before starting, make sure you have:" -ForegroundColor Yellow
    Write-Host "  ✓ Read the migration guide: RAILWAY_TO_DIGITALOCEAN_MIGRATION_GUIDE.md"
    Write-Host "  ✓ Created your DigitalOcean PostgreSQL database"
    Write-Host "  ✓ Have at least 2GB free disk space for backups"
    Write-Host "  ✓ Railway database is active and accessible`n"
    
    $response = Read-Host "Start migration now? (yes/no)"
    if ($response -eq "yes") {
        Write-Host "`nStarting migration...`n" -ForegroundColor Green
        python migrate_railway_to_digitalocean.py
    } else {
        Write-Host "`nMigration cancelled. Run this script again when ready." -ForegroundColor Yellow
        Write-Host "`nOr run directly:" -ForegroundColor Cyan
        Write-Host "  python migrate_railway_to_digitalocean.py`n"
    }
} else {
    Write-Host "`n========================================" -ForegroundColor Yellow
    Write-Host "Next Steps" -ForegroundColor Yellow
    Write-Host "========================================`n" -ForegroundColor Yellow
    
    Write-Host "1. Set the missing environment variables (see above)"
    Write-Host "2. Read the migration guide:"
    Write-Host "     RAILWAY_TO_DIGITALOCEAN_MIGRATION_GUIDE.md"
    Write-Host "3. Run this script again to start migration`n"
}

Write-Host "For help, see:" -ForegroundColor Cyan
Write-Host "  📖 RAILWAY_TO_DIGITALOCEAN_MIGRATION_GUIDE.md" -ForegroundColor White
Write-Host "  🐛 GitHub Issues: https://github.com/jalex0823/BeeSmartSpellingBeeApp/issues`n" -ForegroundColor White
