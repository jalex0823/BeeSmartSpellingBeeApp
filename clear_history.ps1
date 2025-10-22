# Clear PowerShell history to fix emoji encoding issue
$historyPath = (Get-PSReadLineOption).HistorySavePath
Write-Host "History file: $historyPath"

if (Test-Path $historyPath) {
    Write-Host "Clearing history file..."
    Remove-Item $historyPath -Force
    Write-Host "History cleared! Please restart PowerShell."
} else {
    Write-Host "History file not found."
}
