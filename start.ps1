# NyayaLabel AI — One-Click Local Startup Script (PowerShell)
# Run this from the project root: E:\NAYALABELAI\
# Usage: Right-click -> "Run with PowerShell"  OR  in terminal: .\start.ps1

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython  = "$ProjectRoot\backend\venv\Scripts\python.exe"
$VenvPip     = "$ProjectRoot\backend\venv\Scripts\pip.exe"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NyayaLabel AI  -  Startup Script    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create venv if it doesn't exist
if (-Not (Test-Path $VenvPython)) {
    Write-Host "[1/3] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv "$ProjectRoot\backend\venv"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: 'python' not found. Install Python 3.10+ from https://python.org" -ForegroundColor Red
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
    Write-Host "    Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "[1/3] Virtual environment found. Skipping creation." -ForegroundColor Green
}

# Step 2: Install / upgrade dependencies
Write-Host ""
Write-Host "[2/3] Installing / verifying dependencies..." -ForegroundColor Yellow
& $VenvPip install -r "$ProjectRoot\backend\requirements.txt" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed. Check your internet connection." -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host "    All dependencies OK." -ForegroundColor Green

# Step 3: Start the server
Write-Host ""
Write-Host "[3/3] Starting NyayaLabel AI server on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  --> Open your browser and go to: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  --> Login: officer / officer123   (or manager / manager123)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press CTRL+C to stop the server." -ForegroundColor DarkGray
Write-Host ""

Set-Location $ProjectRoot
& $VenvPython -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
