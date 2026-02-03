# 🏗️ SYSTEM ARCHITECTURE DEEP DIVE

## Overview Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  HTML5 UI                                              │  │
│  │  - Audio Upload Interface                              │  │
│  │  - Real-time Status Updates                            │  │
│  │  - Risk Visualization (Animated Progress Bar)          │  │
│  │  - Results Dashboard                                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                           ↓                                   │
│                   REST API (JSON/HTTP)                        │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI Server)                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  app.py - Main Entry Point                             │  │
│  │  - Route: POST /analyze-call                           │  │
│  │  - Orchestrates all services                           │  │
│  │  - Returns JSON response                               │  │
│  └────────────────────────────────────────────────────────┘  │
│            ↓              ↓              ↓                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Layer 1     │  │  Layer 2     │  │  Layer 3     │       │
│  │  AUDIO       │  │  SPEECH-TO   │  │  SCAM        │       │
│  │  PROCESSOR   │  │  TEXT        │  │  DETECTOR    │       │
│  │              │  │  (Whisper)   │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                              ↓               │
│                                      ┌──────────────────┐    │
│                                      │  Layer 4         │    │
│                                      │  RISK SCORER     │    │
│                                      │  & EXPLAINABILITY│    │
│                                      └──────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## LAYER 1: Audio Ingestion

**File**: `services/audio_processor.py`
**Responsibility**: Validate and normalize audio

### Process Flow

```
Raw Audio File (MP3, WAV, OGG, etc.)
         ↓
   ┌─────────────┐
   │  Validation │
   ├─────────────┤
   │ - Format    │
   │ - Size      │
   │ - Duration  │
   └─────────────┘
         ↓
  ┌──────────────┐
  │   Loading    │
  ├──────────────┤
  │ - Read bytes │
  │ - Parse      │
  │ - Mono conv  │
  └──────────────┘
         ↓
  ┌──────────────┐
  │ Resampling   │
  ├──────────────┤
  │ - Any rate → │
  │   16kHz      │
  │ (Whisper     │
  │  optimized)  │
  └──────────────┘
         ↓
  ┌──────────────┐
  │ Normalization│
  ├──────────────┤
  │ - Peak       │
  │   detect     │
  │ - Scale to   │
  │   0.95 max   │
  └──────────────┘
         ↓
  Output: Processed WAV (16kHz, mono, normalized)
```

### Key Functions

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `validate_audio_file()` | bytes, filename | bool/exception | Check format, size, duration |
| `process_audio()` | bytes, filename | bytes, duration | Convert to Whisper-ready format |
| `get_audio_metadata()` | bytes | dict | Quick validation without full processing |

### Constraints Enforced

- ✅ Max duration: 600 seconds (10 minutes)
- ✅ Min duration: 1 second
- ✅ Max file size: 50 MB
- ✅ Supported formats: WAV, MP3, OGG, FLAC, M4A

---

## LAYER 2: Speech-to-Text Service

**File**: `services/speech_to_text.py`
**Responsibility**: Transcribe audio using Whisper

### Process Flow

```
Processed Audio (WAV 16kHz)
         ↓
  ┌──────────────┐
  │ Load Whisper │
  │ Model        │
  │ (base size)  │
  └──────────────┘
         ↓
  ┌──────────────┐
  │ Transcribe   │
  │ with Whisper │
  │              │
  │ Features:    │
  │ - 99+ langs  │
  │ - Robust to  │
  │   noise      │
  │ - Punctuation│
  │   support    │
  └──────────────┘
         ↓
  ┌──────────────┐
  │ Extract:     │
  │ - Text       │
  │ - Language   │
  │ - Confidence │
  └──────────────┘
         ↓
Output: (transcription, language, confidence)
```

### Model Sizes

| Size | Parameters | Speed | Accuracy | RAM |
|------|-----------|-------|----------|-----|
| tiny | 39M | Fastest | Low | 1GB |
| base | 74M | Fast | Good | 2GB |
| small | 244M | Medium | Better | 3GB |
| medium | 769M | Slow | Excellent | 5GB |
| large | 1550M | Slowest | Best | 10GB |

**Hackathon Choice**: `base` (balanced for demo)

### Supported Languages

✅ Major Indian: Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Gujarati, Marathi, Punjabi, Urdu
✅ Global: English, Spanish, French, German, Chinese, Japanese, Korean, Portuguese, Russian, Italian, Dutch, Arabic

---

## LAYER 3: Pattern Analyzer (Scam Intelligence Engine)

**File**: `services/pattern_analyzer.py`
**Responsibility**: Detect social engineering patterns

### Architecture

```
Transcribed Text
       ↓
   ┌─────────────────────┐
   │  Pattern Detector   │
   │  (Multi-pattern)    │
   └─────────────────────┘
       ↓ ↓ ↓ ↓ ↓ ↓ ↓
   ┌─┴┬─┴┬─┴┬─┴┬─┴┬─┴┬─┴┐
   │  1 2 3 4 5 6 7     │
   └──────────────────┬──┘
                      ↓
          Output: List[PatternMatch]
```

### 7 Detection Modules

| # | Pattern | Keywords | Risk | Example |
|---|---------|----------|------|---------|
| 1 | **OTP Request** | otp, code, verify | 100 | "Tell me your OTP" |
| 2 | **Urgency** | immediately, today, urgent | 20 | "Act within 24 hours" |
| 3 | **Authority** | bank, RBI, police, official | 25 | "I'm from your bank" |
| 4 | **Fear** | fraud, arrest, block, close | 20 | "Your account will close" |
| 5 | **Financial** | account, card, transfer, amount | 15 | "Verify your account" |
| 6 | **Info Request** | provide, share, tell, give | 30 | "Give your card number" |
| 7 | **Multilingual** | Language-specific patterns | Varies | Hindi: "jaldi", Tamil: "vali" |

### Detection Logic

```python
for pattern_detector in [otp, urgency, authority, fear, finance, info_request]:
    if pattern_detector.matches(text):
        yield PatternMatch(
            name=pattern_detector.name,
            keywords=pattern_detector.keywords_found,
            risk_score=pattern_detector.risk_points,
            explanation=pattern_detector.human_readable_reason,
            confidence=0.75-0.99
        )
```

### Special Cases

**OTP Request** (Critical):
- Must have OTP keyword
- Must have request context (tell, provide, give)
- Confidence: 0.99 (almost certain)

**Authority Impersonation**:
- Must have authority keyword
- Must have claim context (is, am, calling from)
- Confidence: 0.80

**Pattern Synergy**:
- 2 patterns: +5 risk bonus
- 3 patterns: +10 risk bonus
- 4+ patterns: +20 risk bonus
- Reason: Sophisticated coordinated attack

---

## LAYER 4: Risk Scoring & Explainability Engine

**File**: `services/risk_scorer.py`
**Responsibility**: Calculate transparent risk score and explain decisions

### Risk Calculation Algorithm

```python
base_score = 0

# Step 1: Sum all pattern contributions
for pattern in detected_patterns:
    base_score += pattern.risk_score

# Step 2: Apply synergy bonus (multi-pattern attacks)
synergy = calculate_synergy(len(detected_patterns))
base_score += synergy

# Step 3: Reduce risk for safe indicators
safe_count = count_safe_indicators(text)
base_score -= (safe_count * 5)  # Cap at 20

# Step 4: Heuristic adjustments
if call_duration < 30 and base_score > 30:
    base_score += 10  # Short calls are suspicious

# Step 5: Clamp to 0-100
final_score = max(0, min(100, base_score))
```

### Example Calculation

```
Input: Scam call with OTP request, urgency, authority claim

Step 1: Sum patterns
   OTP Request:              +100
   Urgency (2 keywords):     +20
   Authority Impersonation:  +25
   ──────────────────────────────
   Base Score:               145

Step 2: Synergy bonus (3 patterns)
   +10 (sophisticated attack)
   ──────────────────────────────
   With Synergy:             155

Step 3: Safe indicators
   Found: 0 safe indicators
   Reduction: 0
   ──────────────────────────────
   After Safety Check:       155

Step 4: Call duration heuristic
   Duration: 45 seconds > 30s
   No adjustment
   ──────────────────────────────
   After Heuristics:         155

Step 5: Clamp to 0-100
   Final: min(100, max(0, 155)) = 100
   ──────────────────────────────
   FINAL SCORE:              100/100 🔴

Risk Level: CRITICAL_SCAM
Confidence: 0.99 (99%)
```

### Risk Level Classification

| Score Range | Level | Emoji | Action |
|------------|-------|-------|--------|
| 90-100 | CRITICAL_SCAM | 🔴 | HANG UP IMMEDIATELY |
| 70-89 | HIGH_RISK | 🟠 | END CALL |
| 50-69 | MEDIUM_RISK | 🟡 | BE CAUTIOUS |
| 30-49 | LOW_MEDIUM_RISK | 🟢 | LIKELY SAFE |
| 0-29 | LIKELY_SAFE | ✅ | APPEARS LEGITIMATE |

### Confidence Calculation

```
confidence = 0.5  # base

# More patterns = higher confidence
if num_patterns >= 3: confidence += 0.35
elif num_patterns == 2: confidence += 0.20
elif num_patterns == 1: confidence += 0.10

# Safe indicators reduce confidence
if safe_count > 2: confidence -= 0.15

# Extreme scores are more confident
if score >= 95 or score <= 5: confidence += 0.15
elif 40 <= score <= 60: confidence -= 0.10

# Clamp to reasonable range
final_confidence = max(0.30, min(0.99, confidence))
```

### Explainability Framework

**Every result includes**:

1. **Risk Score**: Numeric (0-100)
2. **Risk Level**: Classification (CRITICAL_SCAM, etc.)
3. **Detected Patterns**: List of what was found
   ```json
   {
     "pattern_name": "OTP Request",
     "keywords": ["otp", "tell me"],
     "risk_contribution": 100,
     "explanation": "🚨 CRITICAL: OTP/Password requested. Legitimate institutions NEVER ask for OTP."
   }
   ```
4. **Explanation Message**: Human-readable (multi-line)
   ```
   🔴 RECOMMENDATION: HANG UP IMMEDIATELY
   
   THREATS DETECTED:
   • OTP Request (+100): Caller explicitly requesting OTP
   • Urgency (+20): "immediately", "urgent" language
   • Authority Impersonation (+25): Claims to be from "your bank"
   • Synergy Bonus (+10): Multiple attack vectors
   
   EXPLANATION:
   This is almost certainly a scam. Legitimate banks NEVER ask for OTP.
   The caller is using classic social engineering: artificial urgency 
   + false authority + credential request = sophisticated attack.
   ```
5. **Risk Timeline**: How risk evolved during call
   ```json
   {
     "timestamp": 10,
     "risk_score": 15,
     "reason": "Initial contact - low risk"
   }
   ```
6. **Confidence**: How sure we are (0-1)

---

## DATA FLOW DIAGRAM

```
┌─────────────────────────────┐
│  USER UPLOADS AUDIO FILE    │
│  (Frontend)                 │
└──────────────┬──────────────┘
               │
               ↓
    ┌──────────────────────┐
    │  POST /analyze-call  │
    │  + file, language    │
    └──────────┬───────────┘
               │
               ↓
    ┌──────────────────────────────────┐
    │  FastAPI Router                  │
    │  (app.py)                        │
    └──────────┬───────────────────────┘
               │
        ┌──────┴──────┐
        ↓             ↓
    ┌───────────┐  ┌──────────────┐
    │ Layer 1   │  │ Validate     │
    │ Audio     │  │ file exists  │
    │ Processor │  │ not empty    │
    └───────────┘  └──────────────┘
        │
        ├─ validate_audio_file()
        ├─ process_audio()  ───→ (processed_audio, duration)
        │
        ↓
    ┌───────────────────────┐
    │ Layer 2               │
    │ Speech-to-Text        │
    │ (Whisper)             │
    └───────────────────────┘
        │
        ├─ load_model()  ───→ Whisper(base)
        ├─ transcribe()  ───→ (transcription, language, confidence)
        │
        ↓
    ┌───────────────────────┐
    │ Layer 3               │
    │ Pattern Analyzer      │
    └───────────────────────┘
        │
        ├─ analyze_text()
        │   ├─ detect_otp_request()
        │   ├─ detect_urgency()
        │   ├─ detect_authority_impersonation()
        │   ├─ detect_fear_tactics()
        │   ├─ detect_financial_targeting()
        │   ├─ detect_information_requests()
        │   └─ detect_multilingual_patterns()
        │
        ├─ returns: List[PatternMatch]
        │
        ↓
    ┌───────────────────────┐
    │ Layer 4               │
    │ Risk Scorer           │
    └───────────────────────┘
        │
        ├─ calculate_risk()
        │   ├─ sum_pattern_scores()
        │   ├─ calculate_synergy_bonus()
        │   ├─ count_safe_indicators()
        │   ├─ apply_heuristics()
        │   ├─ build_explanation()
        │   ├─ calculate_confidence()
        │   └─ build_risk_timeline()
        │
        ├─ returns: RiskAssessment
        │
        ↓
    ┌───────────────────────┐
    │ Build Response        │
    │ JSON AnalysisResponse │
    └───────────────────────┘
        │
        ↓
    ┌─────────────────────────────┐
    │  RETURN TO FRONTEND         │
    │  (JSON Response)            │
    └─────────────────────────────┘
        │
        ↓
    ┌──────────────────────────────────┐
    │  Display Results                 │
    │  - Risk score visualization      │
    │  - Transcription                 │
    │  - Detected patterns             │
    │  - Explanation                   │
    │  - Recommendation                │
    │  - Risk timeline                 │
    └──────────────────────────────────┘
```

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Audio Processing | O(n) | Linear with audio length |
| Whisper Transcription | O(n) | Linear with audio length |
| Pattern Matching | O(n*m) | n=text length, m=keyword count (small) |
| Risk Scoring | O(k) | k=number of patterns (typically <10) |

### Space Complexity

| Component | Memory | Notes |
|-----------|--------|-------|
| Whisper Model | ~500MB | Loaded once, cached |
| Audio Buffer | ~10MB | Max 50MB file = ~100MB in memory |
| Patterns | ~100KB | Fixed keyword lists |

### Real-World Performance

| Audio Length | Total Time | Bottleneck |
|--------------|-----------|-----------|
| 30 seconds | 5-8s | Whisper |
| 60 seconds | 8-15s | Whisper |
| 300 seconds | 30-50s | Whisper |

**Whisper times vary based on**:
- Audio quality (noise, clarity)
- Language (English is fastest)
- CPU capabilities
- Model size (using base for speed)

---

## Error Handling Strategy

```python
try:
    # Layer 1: Audio Ingestion
    processed_audio, duration = audio_processor.process_audio(file_bytes, filename)
except ValueError as e:
    → HTTPException(400, "Invalid audio format")
except RuntimeError as e:
    → HTTPException(500, "Processing failed")

try:
    # Layer 2: Speech-to-Text
    transcription, language, confidence = speech_service.transcribe(processed_audio)
except RuntimeError as e:
    → HTTPException(500, "Transcription failed")

# Layers 3-4: Unlikely to fail (keyword matching)
# But wrapped in outer try-catch for robustness

if not transcription or len(transcription) < 3:
    → HTTPException(400, "No speech detected")

# Build final response, convert to JSON
→ AnalysisResponse(...).json()
```

---

## Security Considerations

✅ **Input Validation**: File size, duration, format checked
✅ **No Storage**: Audio never saved to disk
✅ **No External APIs**: All processing local
✅ **CORS Enabled**: Frontend can call backend
✅ **No Authentication**: Fine for hackathon (add for production)
✅ **No Data Logging**: Call content not logged

---

## Scalability Notes

**Current Design**:
- Single-threaded (FastAPI default)
- In-memory processing
- Suitable for: Single user demo, presentations

**For Production**:
- Use `--workers 4` with Uvicorn
- Add async queue processing (Celery/RQ)
- Cache Whisper model
- Add database for historical analysis
- Implement user authentication
- Rate limiting

---

## Testing Strategy

```python
# Unit tests per layer
test_audio_processor.py
test_speech_to_text.py
test_pattern_analyzer.py
test_risk_scorer.py

# Integration tests
test_full_pipeline.py

# E2E tests (manual)
test_demo_audio_files/
  ├── scam_call_critical.wav      → Expected: 95-100
  ├── scam_call_high_risk.wav     → Expected: 75-85
  ├── legitimate_call.wav         → Expected: 5-15
  └── edge_case_false_alarm.wav   → Expected: 20-30
```

---

**This architecture is designed for clarity, modularity, and real-world effectiveness. 🚀**
