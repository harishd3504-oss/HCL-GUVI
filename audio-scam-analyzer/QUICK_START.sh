#!/usr/bin/env bash
# Quick Start - Audio Scam Analyzer
# For Windows: Use PowerShell or GitBash

# 1. START THE API
cd backend
python app.py

# 2. In a NEW terminal, test it:

# Option A: PowerShell (Windows)
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Option B: PowerShell Full Test
powershell -File ..\test_health.ps1

# Option C: Python Test (All platforms)
python test_api.py

# 3. Access the API documentation:
# Open in browser: http://localhost:8000/docs

# 4. Upload an audio file for analysis:
# POST http://localhost:8000/analyze-call
# With file: audio_file.wav / audio_file.mp3 / etc.

# IMPORTANT: DEMO_MODE = True by default
# - Returns instant results (<50ms)
# - Perfect for hackathon demo
# - Switch to False for real processing

echo "✅ API is ready at http://localhost:8000"
echo "📚 API docs at http://localhost:8000/docs"
echo "🎬 Running in DEMO_MODE for instant responses"
