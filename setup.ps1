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
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed. Check the pip error above."
}
& ".\.venv\Scripts\python.exe" -c "import mediapipe as mp; assert hasattr(mp, 'solutions'), 'MediaPipe solutions API is missing'; import cv2, pyautogui, numpy; print('Dependency check passed. MediaPipe:', mp.__version__)"
if ($LASTEXITCODE -ne 0) {
    throw "Dependency check failed. Re-run setup after checking the error above."
}
Write-Host "Setup finished. Run .\run.bat to start Gesture Mouse." -ForegroundColor Green
