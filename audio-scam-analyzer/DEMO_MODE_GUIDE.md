# DEMO_MODE Configuration Guide

## What is DEMO_MODE?

DEMO_MODE is a feature flag that controls how the API responds:

### DEMO_MODE = True (Current Setting)
```python
DEMO_MODE = True
```

**Behavior**:
- Returns instant demo responses (<50ms)
- No Whisper model loads
- No actual audio processing
- Returns realistic sample scam analysis
- Perfect for: Hackathon demo, API testing, presentations

**Response example**:
```json
{
  "success": true,
  "risk_score": 82,
  "risk_level": "HIGH",
  "detected_patterns": [
    {
      "pattern_name": "Artificial Urgency",
      "confidence": 0.95,
      "risk_contribution": 15
    }
  ],
  "primary_threat": "High-risk credential harvesting with urgency manipulation"
}
```

---

### DEMO_MODE = False (Production Mode)
```python
DEMO_MODE = False
```

**Behavior**:
- Performs real audio transcription (Whisper)
- Analyzes for actual scam patterns
- Returns genuine risk assessment
- First request: 30-60s (model loads once)
- Subsequent requests: 2-5s (model cached)

**Use when**:
- You have real audio files to test
- Demonstrating actual detection capabilities
- Running in production environment

---

## How to Switch Modes

### File: `backend/app.py` (Line 33)

**Find this**:
```python
DEMO_MODE = True  # ⚡ FAST: Returns instant demo response (<50ms) instead of real processing
```

**To enable DEMO_MODE** (current):
```python
DEMO_MODE = True
```

**To enable real processing**:
```python
DEMO_MODE = False
```

---

## Environment Variable Configuration (Advanced)

For production/deployment, use environment variables:

### In your shell/terminal:
```bash
# Linux/Mac
export AUDIO_SCAM_DEMO_MODE=false
python app.py

# Windows PowerShell
$env:AUDIO_SCAM_DEMO_MODE="false"
python app.py

# Windows batch
set AUDIO_SCAM_DEMO_MODE=false
python app.py
```

### Modify app.py to support env vars:
```python
import os

DEMO_MODE = os.getenv("AUDIO_SCAM_DEMO_MODE", "true").lower() == "true"
```

---

## Performance Expectations

### With DEMO_MODE = True
```
Request → Response: <50ms
No dependencies: Model not loaded
Startup time: <500ms
Perfect for: Fast demo, testing
```

### With DEMO_MODE = False
```
App startup: <500ms (Whisper not loaded yet)
First /analyze-call: 30-60s (Whisper loads model)
Subsequent requests: 2-5s (model cached)
Perfect for: Real testing, production
```

---

## Recommended Settings for Hackathon

### For Demo/Pitch
```python
DEMO_MODE = True  # ← Keep this
```
- Ultra-fast responses
- Realistic sample data
- Impressive for live demo

### For Technical Judging
```python
DEMO_MODE = False  # ← Switch for real demo
```
- Show actual Whisper transcription
- Real scam pattern detection
- Full feature demonstration
- Note: First call takes 30-60s (model loading)

### Smart Hybrid (Best Practice)
```python
import os

# Allow env override, default to demo mode
DEMO_MODE = os.getenv("AUDIO_SCAM_DEMO_MODE", "true").lower() == "true"

# In app startup:
logger.info(f"🎬 DEMO_MODE = {DEMO_MODE}")
if not DEMO_MODE:
    logger.info("⚠️ Real processing enabled - Whisper will load on first request")
```

---

## Testing Different Modes

### Test with DEMO_MODE = True
```bash
cd backend
AUDIO_SCAM_DEMO_MODE=true python app.py

# In another terminal:
curl -X POST http://localhost:8000/analyze-call \
  -F "audio=@test_audio.wav"
```

### Test with DEMO_MODE = False
```bash
cd backend
AUDIO_SCAM_DEMO_MODE=false python app.py

# Wait for first request to load model (~60s)
# Then responses are fast
```

---

## What Gets Returned in Each Mode

### DEMO_MODE = True Response Structure
```json
{
  "success": true,
  "transcription": "Demo call detected...",
  "risk_score": 82,
  "risk_level": "HIGH",
  "detected_patterns": [
    {
      "pattern_name": "Artificial Urgency",
      "confidence": 0.95,
      "risk_contribution": 15,
      "explanation": "..."
    }
  ],
  "primary_threat": "High-risk credential harvesting...",
  "voice_analysis": {...},
  "emotional_analysis": {...},
  "entity_analysis": {...},
  "known_scam_match": {...}
}
```

**Same structure in both modes!** Only the data differs (sample vs. real)

---

## Troubleshooting

### "API is slow on first request"
→ Check `DEMO_MODE = False` is NOT set  
→ If False, first request loads Whisper (~60s is normal)

### "Want faster demo response"
→ Set `DEMO_MODE = True`

### "Want real audio analysis"
→ Set `DEMO_MODE = False`  
→ Be prepared for 30-60s first request

### "How do I know which mode is active?"
→ Check app startup logs:
```
🎬 DEMO_MODE = True        # ← Demo mode
🎬 DEMO_MODE = False       # ← Real processing
```

---

## Recommended Hackathon Strategy

**During Development & Testing**:
```python
DEMO_MODE = True  # Fast iteration
```

**Final Demo Pitch**:
```python
DEMO_MODE = True  # Impressive speed, real data
# Pre-record responses for backup
```

**Technical Evaluation**:
```python
DEMO_MODE = False  # Show real AI capabilities
# Have a test audio file ready
# Warn judges: "First request loads model, might take 30-60s"
```

---

## Questions?

The DEMO_MODE feature is in `backend/app.py` around line 33.  
Change it anytime to switch behavior without restarting.

Remember:
- ✅ DEMO_MODE = True for fast demo
- ✅ DEMO_MODE = False for real processing
- ✅ Both modes return the same response structure
- ✅ Only the data differs (sample vs. real)
