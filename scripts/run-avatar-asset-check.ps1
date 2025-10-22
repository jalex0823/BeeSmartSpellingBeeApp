param(
  [string]$BaseUrl = $env:BASE_URL
)

if (-not $BaseUrl -or $BaseUrl -eq '') {
  $BaseUrl = 'http://localhost:5000'
}

Write-Host "🐝 Running avatar asset check against $BaseUrl" -ForegroundColor Yellow

try {
  $python = "python"
  & $python "$(Split-Path $MyInvocation.MyCommand.Path -Parent)\..\test_avatar_assets.py" --base $BaseUrl
  exit $LASTEXITCODE
}
catch {
  Write-Error "Failed to run test_avatar_assets.py: $_"
  exit 1
}
