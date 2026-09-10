@echo off
title NyayaLabel AI - Starting Server...
color 0B

echo.
echo  ========================================
echo    NyayaLabel AI  -  Local Startup
echo  ========================================
echo.

cd /d "%~dp0"

:: Check if venv exists, create if not
if not exist "backend\venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv backend\venv
    if errorlevel 1 (
        echo.
        echo  ERROR: Python not found!
        echo  Install Python 3.10+ from https://python.org
        echo  Make sure to check "Add Python to PATH" during install.
        echo.
        pause
        exit /b 1
    )
    echo  Virtual environment created.
) else (
    echo [1/3] Virtual environment found.
)

:: Install dependencies
echo.
echo [2/3] Installing / verifying dependencies...
backend\venv\Scripts\pip.exe install -r backend\requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo  ERROR: Dependency installation failed.
    echo  Check your internet connection and try again.
    pause
    exit /b 1
)
echo  All dependencies OK.

:: Start server
echo.
echo [3/3] Starting server...
echo.
echo  ------------------------------------------
echo   Open browser:  http://127.0.0.1:8000
echo   Login:         officer / officer123
echo  ------------------------------------------
echo.
echo  Press CTRL+C to stop the server.
echo.

backend\venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
