# Popat Wrapper for node
param([Parameter(ValueFromRemainingArguments=$true)]$Args)

$ErrorActionPreference = "Continue"
$output = & node @Args 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "⚠️ Error detected! Calling Popat..." -ForegroundColor Yellow
    $errorText = ($output | Out-String).Trim()
    $errorText = $errorText -replace '"', '\"'
    & "C:\Users\aniru\OneDrive\Desktop\DSU\All Projects\Popat\target\debug\popat.exe" analyze --error "$errorText" --language "javascript"
    Write-Host "`nOriginal error:" -ForegroundColor Red
    Write-Host $output -ForegroundColor Red
} else {
    Write-Host $output
}

exit $exitCode
