# 🔐 AI-Powered Audio Call Scam Analyzer

## Hackathon-Ready Prototype for Financial Fraud Prevention

A **fully functional**, modular system that detects financial scams in recorded phone calls using AI-powered speech analysis and explainable pattern detection.

---

## 🎯 CORE OBJECTIVE

This system:
- ✅ Accepts recorded phone calls (WAV, MP3, OGG, FLAC, M4A)
- ✅ Converts speech to text using **Whisper AI** (99+ languages)
- ✅ Detects **social engineering patterns** (urgency, authority impersonation, fear tactics, OTP requests)
- ✅ Assigns a **transparent risk score** (0-100)
- ✅ Explains **WHY** a call is flagged with specific evidence
- ✅ Shows **risk timeline** (how risk evolved during call)
- ✅ Works **completely locally** (no cloud APIs required)

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│          FRONTEND (HTML/CSS/JS)                     │
│  - Audio Upload Interface                           │
│  - Results Dashboard                                │
│  - Risk Visualization                               │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│          FASTAPI BACKEND (app.py)                   │
│  - REST API Endpoints                               │
│  - Service Orchestration                            │
└─────────────────────────────────────────────────────┘
                         ↓
    ┌────────────────────┼────────────────────┐
    ↓                    ↓                    ↓
┌────────────┐  ┌──────────────────┐  ┌──────────────┐
│   LAYER 1  │  │     LAYER 2      │  │    LAYER 3   │
│   AUDIO    │  │  SPEECH-TO-TEXT  │  │   SCAM       │
│ INGESTION  │  │   (Whisper AI)   │  │  DETECTION   │
└────────────┘  └──────────────────┘  └──────────────┘
                                              ↓
                                      ┌──────────────────┐
                                      │    LAYER 4       │
                                      │ RISK SCORING &   │
                                      │ EXPLAINABILITY   │
                                      └──────────────────┘
```

### **Layers Explained**

| Layer | File | Responsibility |
|-------|------|-----------------|
| **1** | `audio_processor.py` | Validate, normalize audio. Convert to 16kHz WAV |
| **2** | `speech_to_text.py` | Use Whisper to transcribe. Multilingual support |
| **3** | `pattern_analyzer.py` | Detect scam patterns (urgency, authority, OTP, fear) |
| **4** | `risk_scorer.py` | Calculate risk score, generate explanations |

Each layer is **isolated and reusable**.

---

## 🚀 SETUP & RUNNING

### **Prerequisites**

- Python 3.8+
- FFmpeg (required by librosa for audio processing)
- 4GB+ RAM (for Whisper model)

### **Installation**

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# This will download Whisper model (takes ~1-2 minutes on first run)

# 3. Run FastAPI server
python app.py

# Server starts at: http://localhost:8000
```

### **Frontend**

```bash
# Option 1: Use Python's built-in server
python -m http.server 8001 --directory frontend

# Option 2: Use Node's http-server
npx http-server frontend --port 8001

# Access at: http://localhost:8001
```

---

## 💡 UNIQUE WINNING FEATURES

### **1. Explainable AI (XAI) - NOT JUST "SCAM/SAFE"**

Instead of binary classification, the system **explains WHY**:

```
🚨 CRITICAL THREAT: OTP Request
└─ Keywords: "otp", "verify", "confirm"
└─ Explanation: "Legitimate institutions NEVER ask for OTP via phone"
└─ Risk: +100 points (absolute red flag)

⚠️ ARTIFICIAL URGENCY DETECTED
└─ Keywords: "immediately", "urgent", "today"
└─ Explanation: "Time pressure designed to prevent thinking"
└─ Risk: +20 points

👤 AUTHORITY IMPERSONATION
└─ Keywords: "RBI", "bank", "official"
└─ Explanation: "Caller claims to represent bank without verification"
└─ Risk: +25 points
```

### **2. Risk Timeline Visualization**

Shows how risk evolved during the call:

```
⏱️ 0-10s:   Risk 15/100 - Initial contact, caller identifies
⏱️ 10-20s:  Risk 35/100 - Problem described, urgency mounting
⏱️ 20-30s:  Risk 85/100 - Request for account access/OTP
```

### **3. Social Engineering Pattern Detection**

Detects sophisticated attack vectors:

- **Artificial Urgency**: "Act now", "expires today"
- **Authority Impersonation**: Claims to be bank/RBI/police
- **Fear Tactics**: Threats of account closure, legal action
- **Trust Manipulation**: False reassurance, fake verification
- **OTP/Credential Requests**: CRITICAL RED FLAG
- **Financial Targeting**: Multiple banking keywords

### **4. Multilingual Ready**

- Whisper supports 99+ languages
- Architecture supports Hindi, Tamil, Telugu, Kannada, etc.
- Easy to add language-specific patterns

### **5. Privacy-First Design**

- ✅ Audio is processed **in-memory only**
- ✅ No files stored to disk
- ✅ No cloud APIs used
- ✅ Processing is temporary
- ✅ Clear privacy statements in code

---

## 📊 API REFERENCE

### **Main Endpoint: POST /analyze-call**

**Request:**
```bash
curl -X POST \
  -F "file=@call.wav" \
  -F "language=hi" \
  http://localhost:8000/analyze-call
```

**Response:**
```json
{
  "success": true,
  "transcription": "Hello, this is calling from your bank...",
  "risk_score": 92,
  "risk_level": "CRITICAL_SCAM",
  "detected_patterns": [
    {
      "pattern_name": "OTP/Credential Request",
      "keywords": ["otp", "verify"],
      "risk_contribution": 100,
      "explanation": "🚨 CRITICAL: OTP request detected..."
    }
  ],
  "primary_threat": "OTP/Credential Request",
  "explanation": "🔴 RECOMMENDATION: HANG UP IMMEDIATELY...",
  "risk_timeline": [
    {
      "timestamp": 10,
      "risk_score": 15,
      "reason": "Initial contact"
    }
  ],
  "call_duration_seconds": 45.3,
  "language_detected": "en",
  "confidence": 0.92
}
```

### **Health Check: GET /health**

```bash
curl http://localhost:8000/health
```

### **Supported Languages: GET /info/languages**

```bash
curl http://localhost:8000/info/languages
```

---

## 🧠 HOW IT WORKS (STEP-BY-STEP)

### **Example: Detecting a Financial Scam Call**

**Input:** Audio of scam call (45 seconds)

#### **Step 1: Audio Processing**
```
Audio File (MP3, 48kHz)
    ↓
Validate format & size
    ↓
Resample to 16kHz (Whisper optimized)
    ↓
Normalize amplitude
    ↓
Output: Processed WAV (ready for Whisper)
```

#### **Step 2: Speech-to-Text (Whisper)**
```
"Hello, this is your bank calling. Your account has suspicious activity.
We need you to verify your account immediately. Please provide your OTP
for verification. This is urgent - your account will be blocked."
```

#### **Step 3: Pattern Detection**
```
Scanning for scam patterns...

✓ URGENCY DETECTED: "immediately", "urgent"
✓ AUTHORITY CLAIM: "bank", "account verification"
✓ OTP REQUEST: "provide your OTP" ← CRITICAL
✓ FEAR TACTICS: "account will be blocked"
✓ BANKING KEYWORDS: "account", "verification"
```

#### **Step 4: Risk Scoring**
```
Base Score: 0
+ OTP Request: +100 (absolute maximum)
+ Urgency Pattern: +20
+ Authority Impersonation: +25
+ Fear Tactics: +20
+ Pattern Synergy Bonus: +10 (multiple coordinated attacks)
────────────────────
TOTAL RISK SCORE: 92/100

Risk Level: 🔴 CRITICAL_SCAM
Recommendation: HANG UP IMMEDIATELY
```

---

## 📋 CODE QUALITY

✅ **Modular Architecture**: Each service is independent and reusable
✅ **Clear Responsibility**: Functions have single, clear purposes
✅ **Readable Code**: Short functions with comments explaining WHY
✅ **No Overengineering**: Simple, Pythonic code suitable for hackathon
✅ **Explainable Logic**: Every decision is transparent and traceable

### **File Structure**
```
audio-scam-analyzer/
├── backend/
│   ├── app.py                    # Main FastAPI application
│   ├── requirements.txt          # Python dependencies
│   ├── services/
│   │   ├── audio_processor.py    # Audio validation & normalization
│   │   ├── speech_to_text.py     # Whisper transcription
│   │   ├── pattern_analyzer.py   # Scam pattern detection
│   │   └── risk_scorer.py        # Risk scoring & explainability
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models
│   └── utils/
│       └── constants.py          # Scam keywords, patterns, rules
├── frontend/
│   ├── index.html                # Main UI
│   ├── app.js                    # Frontend logic
│   └── styles.css                # Professional styling
├── README.md                     # This file
└── PITCH.md                      # Hackathon elevator pitch
```

---

## 🎮 DEMO WALKTHROUGH (2 MINUTES)

### **1. Launch (15 seconds)**
```bash
# Terminal 1: Start backend
cd backend
python app.py

# Terminal 2: Start frontend
python -m http.server 8001 --directory frontend
```

### **2. Upload Audio (15 seconds)**
- Click "Drag & Drop Your Audio File"
- Select a recorded scam call (or demo audio)
- Click "Analyze Call"

### **3. See Results (30 seconds)**
- Watch as system processes:
  - ✓ Uploads audio
  - ✓ Transcribes with Whisper
  - ✓ Analyzes for patterns
  - ✓ Generates risk score
- Shows:
  - Risk score (0-100)
  - Transcription
  - Detected patterns with explanations
  - Risk timeline
  - Recommendation

---

## 🌍 MULTILINGUAL SUPPORT

### **Supported Languages**

Whisper supports 99+ languages. Key Indian languages:

| Code | Language |
|------|----------|
| hi | Hindi |
| ta | Tamil |
| te | Telugu |
| ml | Malayalam |
| kn | Kannada |
| bn | Bengali |
| gu | Gujarati |
| mr | Marathi |
| pa | Punjabi |
| ur | Urdu |

System auto-detects language if not specified.

---

## 🔒 PRIVACY & ETHICS

### **Privacy First**
- ✅ No call data persisted
- ✅ Audio processed in-memory only
- ✅ Temporary processing, nothing stored
- ✅ No external API calls
- ✅ All processing happens locally

### **Ethical Use**
- ✅ Designed for fraud prevention
- ✅ Transparent explainability (not a black box)
- ✅ User has full control
- ✅ No unauthorized recording

---

## 🔧 TECHNICAL SPECIFICATIONS

| Component | Technology | Notes |
|-----------|-----------|-------|
| Backend | FastAPI (Python) | High-performance, async-ready |
| Speech-to-Text | OpenAI Whisper | 99+ languages, robust |
| Audio Processing | Librosa + Soundfile | Professional quality |
| Frontend | Vanilla HTML/CSS/JS | No dependencies, lightweight |
| API Communication | REST + JSON | Simple, standards-based |
| Data Format | JSON | Easy to parse and extend |

---

## 🚀 PERFORMANCE METRICS

**For a typical 60-second call:**

| Stage | Time | Notes |
|-------|------|-------|
| Audio Processing | ~1s | Normalization, resampling |
| Whisper Transcription | ~5-10s | Depends on audio quality |
| Pattern Analysis | ~0.5s | Keyword matching |
| Risk Scoring | ~0.1s | Calculation |
| **Total** | **~6-12s** | Suitable for real-time demo |

---

## 💪 DIFFERENTIATOR: Why This Wins Hackathons

**Most teams will:**
- Build a simple binary classifier (Scam/Safe)
- Not explain WHY something is flagged
- Use cloud APIs (not local)
- Forget about UX

**This solution will:**
✅ Show EXACT phrases that triggered detection
✅ Explain social engineering techniques
✅ Work 100% locally (impressive for judges)
✅ Have professional, polished UI
✅ Be production-inspired (not just a demo)
✅ Support multiple languages
✅ Include risk timeline (unique visualization)
✅ Emphasize explainability (modern AI trend)

---

## 📈 FUTURE ENHANCEMENTS

1. **Fine-tuned ML Model**: Replace keyword matching with BERT/RoBERTa
2. **Caller Network Analysis**: Flag numbers linked to known scams
3. **Real-time Deployment**: Integrate with phone systems
4. **Mobile App**: iOS/Android integration
5. **Advanced NLP**: Intent detection, emotional analysis
6. **Cross-lingual Patterns**: Scam patterns that work across languages
7. **Feedback Loop**: Community-driven pattern updates

---

## 🐛 TROUBLESHOOTING

### **"Whisper model not found"**
```bash
# First-time setup takes a moment
# Models are cached in ~/.cache/whisper/
# Wait 1-2 minutes for download on first run
```

### **"Audio format not supported"**
```bash
# Install FFmpeg
# Windows: choco install ffmpeg
# Mac: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

### **"CORS error"**
```bash
# Frontend and backend must be on different ports
# Backend: http://localhost:8000
# Frontend: http://localhost:8001
```

### **"API connection refused"**
```bash
# Make sure backend is running
python app.py  # Terminal 1
# Then start frontend in Terminal 2
```

---

## 📝 LICENSE & ATTRIBUTION

- **Whisper**: OpenAI (open-source)
- **FastAPI**: High-performance async web framework
- **Librosa**: Audio processing library

---

## 👨‍💻 AUTHOR NOTES

This system is designed for **maximum impact in 2-3 minutes of demo time**:

1. **Real**: It actually works (not theoretical)
2. **Explainable**: Judges can understand every decision
3. **Local**: No cloud dependencies (impressive)
4. **Professional**: Production-quality code & UI
5. **Unique**: Risk timeline + explainability sets it apart

---

## 🎯 QUICK START

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Run backend
python app.py  # Starts at http://localhost:8000

# 3. In another terminal, run frontend
python -m http.server 8001 --directory frontend

# 4. Open browser
# http://localhost:8001

# 5. Upload a test audio file and analyze!
```

---

## 📞 Support

For issues or questions, check:
- Code comments (every function has comments)
- API docs at http://localhost:8000/docs
- This README

---

**Built with ❤️ for Fraud Prevention | Hackathon Ready 🚀**
