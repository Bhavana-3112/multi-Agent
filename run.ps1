# Usage:
#   .\run.ps1 "Create a palindrome checker function"
#   .\run.ps1                    # interactive prompt

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

function Find-Python310Plus {
    $candidates = @("py -3.12", "py -3.11", "py -3.10", "python")
    foreach ($cmd in $candidates) {
        try {
            $version = Invoke-Expression "$cmd --version 2>&1" | Out-String
            if ($version -match "Python (\d+)\.(\d+)") {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                    return $cmd
                }
            }
        } catch {
            continue
        }
    }
    return $null
}

function Test-EnvHasApiKey {
    param([string]$EnvPath)
    if (-not (Test-Path $EnvPath)) { return $false }
    $content = Get-Content $EnvPath -Raw
    if ($content -match 'OPENAI_API_KEY\s*=\s*(.+)' ) {
        $key = $Matches[1].Trim().Trim('"').Trim("'")
        return ($key -and $key -ne "sk-your-key-here")
    }
    return $false
}

$pythonCmd = Find-Python310Plus
if (-not $pythonCmd) {
    Write-Host "Error: Python 3.10+ is required but was not found." -ForegroundColor Red
    Write-Host "Install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
}

Write-Host "Using: $pythonCmd" -ForegroundColor Cyan

$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    Invoke-Expression "$pythonCmd -m venv .venv"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$envFile = Join-Path $ProjectRoot ".env"
$envExample = Join-Path $ProjectRoot ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "Created .env from .env.example" -ForegroundColor Yellow
    }
}

if (-not (Test-EnvHasApiKey $envFile)) {
    Write-Host ""
    Write-Host "Error: OPENAI_API_KEY is not set." -ForegroundColor Red
    Write-Host "Edit .env and add your key:"
    Write-Host "  OPENAI_API_KEY=sk-your-key-here"
    Write-Host ""
    Write-Host "Get a key at: https://platform.openai.com/api-keys"
    exit 1
}

Write-Host "Running pipeline..." -ForegroundColor Green
& $venvPython main.py @args
exit $LASTEXITCODE
