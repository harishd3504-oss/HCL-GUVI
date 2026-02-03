"""
AI-Powered Audio Call Scam Analyzer - LIGHTWEIGHT DEMO VERSION
===============================================================

This is a fast demo version that doesn't require heavy ML dependencies.
Perfect for hackathon presentations and quick testing.

For production, use the full version with Whisper.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import logging
import random
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =================
# DATA MODELS
# =================

class RiskLevel(str, Enum):
    CRITICAL_SCAM = "CRITICAL_SCAM"
    HIGH_RISK = "HIGH_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    LOW_MEDIUM_RISK = "LOW_MEDIUM_RISK"
    LIKELY_SAFE = "LIKELY_SAFE"


class PatternMatch(BaseModel):
    pattern_name: str
    keywords: List[str]
    confidence: float
    risk_contribution: int
    explanation: str


class RiskTimeline(BaseModel):
    timestamp: float
    risk_score: int
    reason: str


class AnalysisResponse(BaseModel):
    success: bool
    transcription: str
    risk_score: int
    risk_level: RiskLevel
    detected_patterns: List[PatternMatch]
    primary_threat: str
    explanation: str
    risk_timeline: List[RiskTimeline]
    call_duration_seconds: float
    language_detected: str
    confidence: float


# =================
# DEMO DATA & PATTERNS
# =================

# Sample scam call transcriptions
DEMO_TRANSCRIPTIONS = {
    "high_risk": """
    Hello sir, this is calling from your bank RBI Cyber Cell. We have detected 
    suspicious activity in your account. Your account will be blocked immediately 
    if you don't verify within 24 hours. For verification, we need your OTP code 
    right now. This is urgent and time-sensitive. Please provide your OTP immediately.
    Your account balance is at risk. Tell me your one-time password now.
    """,
    
    "medium_risk": """
    Hi, I'm calling regarding your recent credit card transactions. We noticed 
    some unusual activity. Can you confirm if you made purchases at these stores?
    We may need to verify your account information for security purposes.
    """,
    
    "low_risk": """
    Hello, thank you for calling our customer service. My name is John. 
    How can I assist you today? We're here to help. Please take your time 
    explaining your concern. There's no rush at all.
    """,
}

SCAM_PATTERNS = {
    "high_risk": [
        {
            "pattern_name": "OTP/Credential Request",
            "keywords": ["otp", "password", "verify code"],
            "confidence": 0.99,
            "risk_contribution": 100,
            "explanation": "🚨 CRITICAL: OTP/Password request detected. Legitimate institutions NEVER ask for OTP via phone."
        },
        {
            "pattern_name": "Artificial Urgency",
            "keywords": ["immediately", "urgent", "24 hours", "right now"],
            "confidence": 0.92,
            "risk_contribution": 20,
            "explanation": "⚠️ HIGH PRESSURE: Artificial urgency detected with time-pressure language ('immediately', 'urgent', '24 hours')"
        },
        {
            "pattern_name": "Authority Impersonation",
            "keywords": ["bank", "rbi", "cyber cell"],
            "confidence": 0.88,
            "risk_contribution": 25,
            "explanation": "👤 IMPERSONATION: Caller claims to represent RBI without verification."
        },
        {
            "pattern_name": "Fear-Based Pressure",
            "keywords": ["blocked", "will be", "at risk"],
            "confidence": 0.85,
            "risk_contribution": 20,
            "explanation": "😨 FEAR TACTIC: Threat language detected ('will be blocked', 'at risk') designed to panic you into action."
        }
    ],
    
    "medium_risk": [
        {
            "pattern_name": "Financial Information Targeting",
            "keywords": ["credit card", "transactions", "account"],
            "confidence": 0.75,
            "risk_contribution": 15,
            "explanation": "💰 FINANCIAL TARGET: Multiple banking keywords detected - attempt to verify account information."
        }
    ],
    
    "low_risk": []
}

RISK_LEVELS = {
    "high_risk": 92,
    "medium_risk": 45,
    "low_risk": 8,
}

RECOMMENDATIONS = {
    "high_risk": "🔴 RECOMMENDATION: HANG UP IMMEDIATELY. This is almost certainly a scam. Do NOT provide any information.",
    "medium_risk": "🟡 RECOMMENDATION: BE CAUTIOUS. Verify independently before taking action.",
    "low_risk": "✅ RECOMMENDATION: APPEARS LEGITIMATE. No scam indicators detected."
}

# =================
# APP INITIALIZATION
# =================

app = FastAPI(
    title="🔐 AI-Powered Audio Call Scam Analyzer (DEMO)",
    description="Fast demo version - perfect for hackathon presentations",
    version="1.0.0-demo"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

logger.info("✅ Demo backend initialized (lightweight version)")

# =================
# ENDPOINTS
# =================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0-demo",
        "services": {
            "audio_processor": "ready",
            "transcription": "mock_demo",
            "pattern_analyzer": "ready",
            "risk_scorer": "ready",
        }
    }


@app.post("/analyze-call", response_model=AnalysisResponse)
async def analyze_call(
    file: UploadFile = File(...),
    language: Optional[str] = None,
):
    """
    Demo endpoint - analyzes audio call for scam indicators
    (Uses simulated data for instant response)
    """
    
    logger.info(f"📞 Analyzing call: {file.filename}")
    
    try:
        # Read file
        file_bytes = await file.read()
        
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Simulate analysis
        file_size = len(file_bytes) / 1024
        logger.info(f"📥 File received: {file_size:.1f} KB")
        
        # Randomly select risk level for demo variety
        risk_category = random.choice(["high_risk", "medium_risk", "low_risk"])
        
        transcription = DEMO_TRANSCRIPTIONS[risk_category]
        patterns = SCAM_PATTERNS[risk_category]
        risk_score = RISK_LEVELS[risk_category]
        recommendation = RECOMMENDATIONS[risk_category]
        
        # Determine risk level
        if risk_score >= 90:
            risk_level = RiskLevel.CRITICAL_SCAM
        elif risk_score >= 70:
            risk_level = RiskLevel.HIGH_RISK
        elif risk_score >= 50:
            risk_level = RiskLevel.MEDIUM_RISK
        elif risk_score >= 30:
            risk_level = RiskLevel.LOW_MEDIUM_RISK
        else:
            risk_level = RiskLevel.LIKELY_SAFE
        
        # Build explanation
        if patterns:
            pattern_list = "\n".join([f"  • {p['pattern_name']}: +{p['risk_contribution']} points" for p in patterns])
            explanation = f"""🔴 **RISK ASSESSMENT: {risk_level}** ({risk_score}/100)

🚨 **Detected Threats:**
{pattern_list}

⚠️ **Pattern Combination:** Multiple attack vectors detected. This suggests a sophisticated, coordinated scam.

**Recommendation:**
{recommendation}"""
        else:
            explanation = f"""✅ **RISK ASSESSMENT: {risk_level}** ({risk_score}/100)

No scam patterns detected. This appears to be a legitimate call.

Recommendation:
{recommendation}"""
        
        # Build timeline
        timeline = [
            {"timestamp": 10, "risk_score": 15, "reason": "Initial contact - caller identifies themselves"},
            {"timestamp": 20, "risk_score": 45, "reason": "Problem description - urgency and pressure mounting"},
            {"timestamp": 30, "risk_score": risk_score, "reason": "Request phase - asking for sensitive information or urgent action"},
        ]
        
        response = AnalysisResponse(
            success=True,
            transcription=transcription.strip(),
            risk_score=risk_score,
            risk_level=risk_level,
            detected_patterns=[
                PatternMatch(
                    pattern_name=p["pattern_name"],
                    keywords=p["keywords"],
                    confidence=p["confidence"],
                    risk_contribution=p["risk_contribution"],
                    explanation=p["explanation"],
                )
                for p in patterns
            ],
            primary_threat=patterns[0]["pattern_name"] if patterns else "No threats detected",
            explanation=explanation,
            risk_timeline=timeline,
            call_duration_seconds=float(random.randint(30, 120)),
            language_detected=language or "en",
            confidence=0.92,
        )
        
        logger.info(f"✅ Analysis complete: {risk_level} ({risk_score}/100)")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.get("/info/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "supported_languages": {
            "hi": "Hindi",
            "ta": "Tamil",
            "te": "Telugu",
            "en": "English",
            "es": "Spanish",
        },
        "auto_detect": True,
    }


@app.get("/info/patterns")
async def get_pattern_info():
    """Get information about detected patterns"""
    return {
        "patterns_detected": [
            "OTP/Credential Requests",
            "Artificial Urgency",
            "Authority Impersonation",
            "Fear-Based Pressure",
            "Financial Information Targeting",
        ],
        "explanation": "System detects social engineering techniques commonly used in financial fraud",
    }


@app.get("/")
async def root():
    """API documentation"""
    return {
        "name": "🔐 AI-Powered Audio Call Scam Analyzer (DEMO)",
        "version": "1.0.0-demo",
        "description": "Fast lightweight demo version for hackathon presentations",
        "endpoints": {
            "health": "GET /health",
            "analyze": "POST /analyze-call",
            "languages": "GET /info/languages",
            "patterns": "GET /info/patterns",
        },
        "docs": "http://localhost:8000/docs",
        "note": "This is a demo version. For production, use full version with Whisper AI.",
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting demo backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
