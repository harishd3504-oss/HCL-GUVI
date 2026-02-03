@echo off
REM ============================================================================
REM AI-Powered Audio Call Scam Analyzer - Windows Startup Script
REM ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  🔐 AI-Powered Audio Call Scam Analyzer                   ║
echo ║  Hackathon-Ready Fraud Detection System                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python available
echo.

REM Install dependencies
echo 📦 Installing dependencies...
echo    This may take 2-5 minutes on first run (Whisper model download)

cd backend
pip install -q -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed
cd ..
echo.

REM Start backend in new window
echo 🚀 Starting Backend Server...
start cmd /k "cd backend && python app.py"

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start frontend in new window
echo 🎨 Starting Frontend Server...
start cmd /k "cd frontend && python -m http.server 8001"

REM Wait for frontend to start
timeout /t 2 /nobreak

REM Open browser
echo.
echo ✅ All services started!
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  YOUR SYSTEM IS READY                                      ║
echo ║                                                            ║
echo ║  📱 Frontend:  http://localhost:8001                      ║
echo ║  🔌 Backend:   http://localhost:8000                      ║
echo ║  📚 API Docs:  http://localhost:8000/docs                 ║
echo ║                                                            ║
echo ║  OPENING http://localhost:8001 IN YOUR BROWSER...        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

start http://localhost:8001

echo.
echo ✅ Ready! Upload an audio file and click 'Analyze Call'
echo.
pause
