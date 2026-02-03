# 🚀 GETTING STARTED GUIDE

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- 4GB RAM (for Whisper model)
- 2GB free disk space

### Windows Users
```batch
# 1. Open Command Prompt in project folder
cd audio-scam-analyzer

# 2. Run startup script
start.bat

# This automatically:
# - Installs dependencies
# - Starts backend server
# - Starts frontend server
# - Opens browser at http://localhost:8001
```

### Mac/Linux Users
```bash
# 1. Open Terminal in project folder
cd audio-scam-analyzer

# 2. Make script executable
chmod +x start.sh

# 3. Run startup script
./start.sh

# This automatically does everything (see Windows above)
```

### Manual Setup (All Platforms)

#### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

This will:
- Install FastAPI, Uvicorn, Pydantic
- Install Librosa, Soundfile, NumPy
- Download Whisper model (~1GB, only on first run)

#### Step 2: Start Backend
```bash
# Terminal 1
cd backend
python app.py

# Backend runs at http://localhost:8000
```

#### Step 3: Start Frontend
```bash
# Terminal 2
cd frontend
python -m http.server 8001

# Frontend runs at http://localhost:8001
```

#### Step 4: Open Browser
```
http://localhost:8001
```

---

## Usage

### 1. Upload Audio
- Click upload area or drag-and-drop
- Supported formats: WAV, MP3, OGG, FLAC, M4A
- Max size: 50MB

### 2. Select Language (Optional)
- Leave blank for auto-detect
- Choose language if you know it (faster)

### 3. Click Analyze
- System will analyze the call
- Takes 5-15 seconds depending on length

### 4. View Results
- Transcription of call
- Risk score (0-100)
- Detected scam patterns
- Detailed explanation
- Risk timeline
- Recommendation

---

## Testing with Demo Audio

### Create Test Scam Call Audio
```python
# Simple script to generate test audio with scam phrases

from pydub import AudioSegment
from pydub.generators import Sine
import os

# Using text-to-speech (optional)
# For demo: Use real recordings or AI voices

# Example command (if you have ffmpeg + espeak):
# espeak "Hello, this is your bank. We need to verify your account immediately. Please provide your OTP." -w test_scam.wav
```

### Recommended Test Files
Place in `test-audio/` folder:
1. `scam_high_risk.wav` - Should get 85-100 score
2. `scam_medium_risk.wav` - Should get 50-75 score
3. `legitimate.wav` - Should get 5-30 score

---

## Troubleshooting

### Issue: "Python command not found"

**Windows**:
```bash
# Use full path to Python
C:\Python39\python.exe backend\app.py

# Or add Python to PATH
```

**Mac/Linux**:
```bash
# Use python3 explicitly
python3 backend/app.py
```

### Issue: "ModuleNotFoundError"

```bash
# Make sure you're in backend directory
cd backend

# Install requirements
pip install -r requirements.txt

# Or upgrade pip
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "Port 8000/8001 already in use"

```bash
# Find process using port (Mac/Linux)
lsof -i :8000
lsof -i :8001

# Kill process
kill -9 <PID>

# Windows: Use Task Manager or
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "Whisper model takes forever to download"

```bash
# First run downloads ~1GB model
# This is normal, happens only once
# Model cached at ~/.cache/whisper/

# If interrupted:
# Just restart, it will continue
```

### Issue: "CORS error in browser"

```bash
# Frontend and backend must be on different ports:
# Frontend: http://localhost:8001
# Backend:  http://localhost:8000

# Check in app.py CORS configuration:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
)
```

### Issue: "API connection refused"

```
Check:
1. Backend is running: python app.py
2. Terminal shows "Uvicorn running on http://0.0.0.0:8000"
3. Try accessing http://localhost:8000/health in browser
4. Should see: {"status": "healthy"}
```

### Issue: "Audio format not supported"

**Windows**: Install FFmpeg
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**Mac**: Install FFmpeg
```bash
brew install ffmpeg
```

**Linux**: Install FFmpeg
```bash
sudo apt-get install ffmpeg
```

---

## Configuration

### Whisper Model Size
Edit `backend/services/speech_to_text.py`:
```python
MODEL_SIZE = "base"  # Change to: tiny, small, medium, large

# Performance vs Accuracy:
# tiny   → Fastest, 39M params, ~1s
# base   → Balanced, 74M params, ~5-10s (default)
# small  → Better, 244M params, ~10-20s
# medium → Very good, 769M params, ~30-50s
# large  → Best, 1550M params, ~60-120s
```

### Risk Scoring Thresholds
Edit `backend/utils/constants.py`:
```python
PATTERNS = {
    "urgency_count_threshold": 2,    # How many urgency keywords = flag?
    "banking_count_threshold": 3,    # How many banking keywords = flag?
    "otp_request": 100,              # OTP request risk
    "authority_impersonation": 80,   # Authority claim risk
    # ... etc
}
```

### Scam Keywords
Add more patterns in `backend/utils/constants.py`:
```python
URGENCY_KEYWORDS = [
    "urgent",
    "immediately",
    # Add your own keywords
]
```

---

## Development Tips

### Running Tests
```bash
# Unit tests (if you create them)
python -m pytest tests/

# Manual testing with curl
curl -X POST \
  -F "file=@call.wav" \
  http://localhost:8000/analyze-call
```

### Accessing API Documentation
```
http://localhost:8000/docs
```

This gives you:
- Interactive API explorer
- Try endpoints directly
- See request/response schemas

### Debugging
```python
# In backend/app.py, change logging level:
logging.basicConfig(level=logging.DEBUG)

# This shows detailed information about each step
```

### Checking API Health
```bash
curl http://localhost:8000/health

# Should return:
# {"status": "healthy", "version": "1.0.0", "services": {...}}
```

---

## Performance Tips

### Faster Analysis
```python
# Use smaller Whisper model
MODEL_SIZE = "tiny"  # Fastest

# Or use base model (already default)
MODEL_SIZE = "base"
```

### Reduce Memory Usage
```python
# Limit audio size
MAX_DURATION_SECONDS = 300  # 5 minutes instead of 10

# Reduce Whisper batch size in speech_to_text.py
```

### Parallel Processing (Advanced)
For production:
```python
# Use FastAPI's async features
@app.post("/analyze-call")
async def analyze_call(file: UploadFile):
    # Already optimized with async/await
    pass
```

---

## Deployment Options

### Option 1: Local Demo (What you have now)
- Backend on `localhost:8000`
- Frontend on `localhost:8001`
- Perfect for hackathon

### Option 2: Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "app.py"]
```

### Option 3: Cloud Deployment (AWS, GCP, Azure)
```bash
# Would require:
# 1. Remove localhost binding
# 2. Add authentication
# 3. Add HTTPS
# 4. Configure domain
# 5. Set up database
# (Out of scope for hackathon)
```

---

## API Response Examples

### Successful Analysis
```json
{
  "success": true,
  "transcription": "Hello, this is your bank calling...",
  "risk_score": 92,
  "risk_level": "CRITICAL_SCAM",
  "detected_patterns": [
    {
      "pattern_name": "OTP/Credential Request",
      "keywords": ["otp", "verify"],
      "risk_contribution": 100,
      "explanation": "🚨 CRITICAL: OTP request detected",
      "confidence": 0.99
    }
  ],
  "primary_threat": "OTP/Credential Request",
  "explanation": "🔴 RECOMMENDATION: HANG UP IMMEDIATELY",
  "risk_timeline": [...],
  "call_duration_seconds": 45.3,
  "language_detected": "en",
  "confidence": 0.92
}
```

### Error Response
```json
{
  "success": false,
  "error": "File too large: 75.3MB (max 50MB)"
}
```

---

## File Structure Quick Reference

```
audio-scam-analyzer/
├── README.md                    ← Start here
├── GETTING_STARTED.md          ← This file
├── ARCHITECTURE.md             ← Deep dive
├── PITCH.md                    ← Hackathon pitch
│
├── start.sh                    ← For Mac/Linux
├── start.bat                   ← For Windows
├── check_setup.py              ← Verify installation
│
├── backend/
│   ├── app.py                  ← Main FastAPI app (start here)
│   ├── requirements.txt        ← Python dependencies
│   ├── services/
│   │   ├── audio_processor.py      (Layer 1)
│   │   ├── speech_to_text.py       (Layer 2)
│   │   ├── pattern_analyzer.py     (Layer 3)
│   │   └── risk_scorer.py          (Layer 4)
│   ├── models/
│   │   └── schemas.py          ← Data models
│   └── utils/
│       └── constants.py        ← Scam patterns & keywords
│
└── frontend/
    ├── index.html              ← Main HTML file
    ├── app.js                  ← Frontend logic
    └── styles.css              ← Styling
```

---

## Next Steps

1. ✅ Install prerequisites
2. ✅ Run backend
3. ✅ Run frontend
4. ✅ Upload test audio
5. ✅ See results
6. 📊 Analyze with judges
7. 🎤 Give pitch
8. 🏆 Win hackathon!

---

## Support

**Getting Help**:
1. Check this guide first
2. Check `ARCHITECTURE.md` for technical details
3. Review code comments (every function has comments)
4. Check `README.md` for general info
5. Try `http://localhost:8000/docs` (interactive API)

**Still stuck?**:
- Run `python check_setup.py` to diagnose
- Check terminal output for error messages
- Verify ports 8000 and 8001 are available
- Ensure you're in the correct directory

---

## Pro Tips 🎯

1. **Keep Terminal Windows Open**: Backend and frontend need separate terminals
2. **Watch Logs**: Terminal output shows what's happening
3. **Test with Real Audio**: Demo with an actual call (or AI-generated voice)
4. **Focus on Explainability**: Judges love seeing WHICH patterns triggered detection
5. **Have a Backup**: Know manual steps if automation fails during demo
6. **Time Your Demo**: 2-3 minutes max = upload → analyze → explain

---

**You're all set! Happy analyzing! 🔐**
