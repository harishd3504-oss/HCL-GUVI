@echo off
REM Fast API Health Check Test (Windows batch)
REM Works with native Windows curl command (Windows 10+)

echo.
echo ===================================================
echo  Audio Scam Analyzer - Health Check Test
echo ===================================================
echo.

setlocal enabledelayedexpansion

set URL=http://localhost:8000/health

echo [INFO] Testing API at: %URL%
echo.

REM Use native Windows curl (no dependencies needed)
curl -i %URL%

echo.
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] API is responding!
) else (
    echo [ERROR] Connection failed. Make sure API is running:
    echo.
    echo   cd backend
    echo   python app.py
)

pause
