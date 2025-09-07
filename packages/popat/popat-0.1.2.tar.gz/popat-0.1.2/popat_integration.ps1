# Popat Seamless Integration Script
# Source this file or add to your PowerShell profile for automatic error detection

# Get the Popat executable path
$PopatPath = Join-Path (Get-Location) "target\debug\popat.exe"

function Invoke-PopatWrapper {
    param(
        [string]$Command,
        [string]$Language,
        [string[]]$Arguments
    )
    
    $ErrorActionPreference = "Continue"
    $originalCommand = Get-Command $Command -CommandType Application -ErrorAction SilentlyContinue
    if (-not $originalCommand) {
        Write-Host "Command '$Command' not found" -ForegroundColor Red
        return
    }
    
    $output = & $originalCommand.Source @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        Write-Host "`n🦜 Oops! Popat detected an error. Let me help..." -ForegroundColor Cyan
        $errorText = ($output | Out-String).Trim()
        & $PopatPath analyze --error $errorText --language $Language
        Write-Host "`n--- Original Error ---" -ForegroundColor DarkGray
        Write-Host $output -ForegroundColor Red
    } else {
        Write-Host $output
    }
    
    $global:LASTEXITCODE = $exitCode
}

# Define wrapped functions for common programming commands
function python {
    param([Parameter(ValueFromRemainingArguments=$true)]$Args)
    Invoke-PopatWrapper -Command "python" -Language "python" -Arguments $Args
}

function node {
    param([Parameter(ValueFromRemainingArguments=$true)]$Args)
    Invoke-PopatWrapper -Command "node" -Language "javascript" -Arguments $Args
}

function cargo {
    param([Parameter(ValueFromRemainingArguments=$true)]$Args)
    Invoke-PopatWrapper -Command "cargo" -Language "rust" -Arguments $Args
}

function javac {
    param([Parameter(ValueFromRemainingArguments=$true)]$Args)
    Invoke-PopatWrapper -Command "javac" -Language "java" -Arguments $Args
}

function rustc {
    param([Parameter(ValueFromRemainingArguments=$true)]$Args)
    Invoke-PopatWrapper -Command "rustc" -Language "rust" -Arguments $Args
}

Write-Host "🦜 Popat integration loaded! Now run any code with errors and I'll help automatically!" -ForegroundColor Green
Write-Host "Try: python -c `"print('missing quote`"" -ForegroundColor Yellow
```

```
# Simple Popat Integration
# Run this after starting Popat daemon for automatic error detection

function Wrap-Command {
    param($Cmd, $Lang, $Args)
    
    try {
        $result = & $Cmd @Args 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -ne 0) {
            Write-Host "`n🦜 Popat detected an error! Let me help..." -ForegroundColor Cyan
            $errorText = $result | Out-String
            $popatPath = ".\target\debug\popat.exe"
            & $popatPath analyze --error $errorText --language $Lang
            Write-Host "`n--- Original Error ---" -ForegroundColor DarkRed
            Write-Host $result -ForegroundColor Red
        } else {
            Write-Host $result
        }
        return $exitCode
    } catch {
        Write-Host "Error running command: $_" -ForegroundColor Red
        return 1
    }
}

# Override common commands
Set-Alias -Name python_orig -Value python -Force
Set-Alias -Name node_orig -Value node -Force

function python { Wrap-Command "python_orig" "python" $args }
function node { Wrap-Command "node_orig" "javascript" $args }

Write-Host "🦜 Popat seamless integration activated!" -ForegroundColor Green
Write-Host "Now just run commands normally:" -ForegroundColor Yellow  
Write-Host "  python test_error.py" -ForegroundColor Cyan
Write-Host "  python -c `"print('missing quote`"" -ForegroundColor Cyan
