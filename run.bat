@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. First run setup.ps1 from PowerShell:
  echo powershell -ExecutionPolicy Bypass -File .\setup.ps1
  pause
  exit /b 1
)
".venv\Scripts\python.exe" main.py
if errorlevel 1 (
  echo.
  echo Application exited with an error. Read the message above.
  pause
)
endlocal
