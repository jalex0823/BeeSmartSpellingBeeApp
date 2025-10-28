# Delete Broken Avatar Folders
# Removes non-working avatar folders from static/assets/avatars/

$avatarsPath = "static\assets\avatars"

# Broken avatar folders to remove
$brokenAvatars = @(
    "bee-diva",
    "doctor-bee"
)

Write-Host "🗑️  Deleting broken avatar folders..." -ForegroundColor Yellow
Write-Host ""

foreach ($folder in $brokenAvatars) {
    $fullPath = Join-Path $avatarsPath $folder
    
    if (Test-Path $fullPath) {
        Write-Host "Deleting: $fullPath" -ForegroundColor Red
        Remove-Item -Path $fullPath -Recurse -Force
        Write-Host "  ✅ Deleted" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Already removed: $folder" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "✨ Cleanup complete!" -ForegroundColor Green
Write-Host ""

# List remaining avatar folders
Write-Host "📋 Remaining avatar folders:" -ForegroundColor Cyan
Get-ChildItem -Path $avatarsPath -Directory | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor White
}
