#!/bin/bash
# =============================================================================
# AI-Powered Audio Call Scam Analyzer - QUICK START SCRIPT
# =============================================================================
# This script sets up and runs the entire hackathon project in one command
# Works on Windows (PowerShell), Mac, and Linux

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔐 AI-Powered Audio Call Scam Analyzer                   ║"
echo "║  Hackathon-Ready Fraud Detection System                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# =============================================================================
# STEP 1: CHECK PREREQUISITES
# =============================================================================

echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python $(python3 --version 2>&1 | awk '{print $2}')"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found"
    exit 1
fi

echo "✅ pip3 available"

# =============================================================================
# STEP 2: INSTALL DEPENDENCIES
# =============================================================================

echo ""
echo "📦 Installing Python dependencies..."
echo "   This may take 2-5 minutes on first run (Whisper model download)"

cd backend

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
    
    # Activate venv
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    fi
fi

# Install requirements
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

cd ..

# =============================================================================
# STEP 3: START BACKEND
# =============================================================================

echo ""
echo "🚀 Starting FastAPI Backend Server..."
echo "   http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"

cd backend
python3 app.py &
BACKEND_PID=$!

cd ..

# Give backend time to start
sleep 3

# =============================================================================
# STEP 4: START FRONTEND
# =============================================================================

echo ""
echo "🎨 Starting Frontend Server..."
echo "   http://localhost:8001"

# Try different server options
if command -v python3 &> /dev/null; then
    cd frontend
    python3 -m http.server 8001 &
    FRONTEND_PID=$!
    cd ..
elif command -v python &> /dev/null; then
    cd frontend
    python -m http.server 8001 &
    FRONTEND_PID=$!
    cd ..
elif command -v npx &> /dev/null; then
    npx http-server frontend --port 8001 &
    FRONTEND_PID=$!
else
    echo "❌ Could not start HTTP server"
    exit 1
fi

sleep 2

# =============================================================================
# STEP 5: OPEN BROWSER
# =============================================================================

echo ""
echo "✅ All services started!"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🎯 YOUR SYSTEM IS READY                                  ║"
echo "║                                                            ║"
echo "║  📱 Frontend:  http://localhost:8001                      ║"
echo "║  🔌 Backend:   http://localhost:8000                      ║"
echo "║  📚 API Docs:  http://localhost:8000/docs                 ║"
echo "║                                                            ║"
echo "║  👉 OPEN http://localhost:8001 IN YOUR BROWSER            ║"
echo "║                                                            ║"
echo "║  Then upload an audio file and click 'Analyze Call'       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Try to open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8001
elif command -v open &> /dev/null; then
    open http://localhost:8001
elif command -v start &> /dev/null; then
    start http://localhost:8001
fi

# =============================================================================
# CLEANUP ON EXIT
# =============================================================================

cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Goodbye!"
}

trap cleanup EXIT

# Keep script running
echo ""
echo "Press Ctrl+C to stop the servers..."
wait
