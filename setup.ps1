$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install 64-bit Python 3.12 and enable Add Python to PATH."
}
python --version
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host "Setup finished. Run .\run.bat to start Gesture Mouse." -ForegroundColor Green
