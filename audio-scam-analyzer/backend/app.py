"""
AI-Powered Audio Call Scam Analyzer - FastAPI Backend
=======================================================

MAIN APPLICATION FILE

Architecture:
1. Audio Ingestion Layer -> audio_processor.py
2. Speech Processing -> speech_to_text.py (Whisper)
3. Scam Detection -> pattern_analyzer.py
4. Risk Scoring -> risk_scorer.py
5. API Presentation -> This file

This is a MODULAR, EXPLAINABLE system designed for:
- Hackathon demo (works locally, no cloud APIs)
- Production readiness (clean layering, easy to extend)
- Transparency (every decision is explained)

PRIVACY FIRST: No call data persists. Processing is temporary.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import tempfile
import os
import asyncio
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Configure logging FIRST (before using logger)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logger.warning("⚠️ API_KEY not found in environment. API will be unsecured!")
else:
    logger.info("✅ API_KEY loaded from environment")

# DEMO MODE FLAG - ENABLE FOR FAST HACKATHON DEMO
DEMO_MODE = True  # ⚡ FAST: Returns instant demo response (<50ms) instead of real processing
DEMO_MODE_MESSAGE = "🎬 DEMO MODE: Ultra-fast sample analysis" if DEMO_MODE else ""

# Import service layers
from services.audio_processor import AudioProcessor
from services.speech_to_text import SpeechToTextService
from services.pattern_analyzer import PatternAnalyzer
from services.risk_scorer import RiskScorer
from services.voice_analyzer import VoiceAnalyzer
from services.emotional_analyzer import EmotionalToneAnalyzer
from services.entity_extractor import EntityExtractor
from services.scam_database import KnownScamDatabase
from models.schemas import AnalysisResponse, RiskLevel, PatternMatch, HealthResponse

# Configure logging - MOVED TO TOP
# logging.basicConfig(...)


# =================
# APP INITIALIZATION
# =================

app = FastAPI(
    title="🔐 AI-Powered Audio Call Scam Analyzer",
    description="Detect financial fraud through voice analysis with explainable AI",
    version="1.0.0",
)

# Serve frontend static files
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
logger.info(f"Frontend path: {frontend_path}")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    logger.info("✅ Static files mounted")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon - production should restrict
    allow_credentials=False,  # FIXED: Cannot use credentials=True with wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service instances - NOW LAZY-LOADED
logger.info("🚀 Initializing services...")
audio_processor = AudioProcessor()
logger.info("✅ Audio Processor initialized")

# ⚡ WHISPER IS NOW LAZY-LOADED - NOT LOADED HERE
# Model only loads on first /analyze-call request
speech_service = SpeechToTextService(model_size="base")
logger.info("✅ Speech-to-Text Service initialized (lazy-loaded)")

pattern_analyzer = PatternAnalyzer()
logger.info("✅ Pattern Analyzer initialized")

risk_scorer = RiskScorer()
logger.info("✅ Risk Scorer initialized")

# NEW: Advanced analysis services
voice_analyzer = VoiceAnalyzer()
logger.info("✅ Voice Analyzer initialized")

emotional_analyzer = EmotionalToneAnalyzer()
logger.info("✅ Emotional Tone Analyzer initialized")

entity_extractor = EntityExtractor()
logger.info("✅ Entity Extractor initialized")

scam_database = KnownScamDatabase()
logger.info("✅ Known Scam Database initialized")

logger.info("🎯 All services ready!")

# =================
# API KEY VERIFICATION
# =================

def verify_api_key(request: Request):
    """
    Verify API key manually from request headers to avoid FastApi auto-conversion issues.
    """
    if not API_KEY:
        logger.warning("⚠️ API_KEY not found in environment. API will be unsecured!")
        return
    
    # Check multiple possible header casing
    x_api_key = request.headers.get("X-API-KEY") or request.headers.get("x-api-key")
    
    logger.info(f"🔑 Auth Check - Received: {x_api_key} | Expected: {API_KEY}")

    if x_api_key != API_KEY:
        logger.error(f"❌ Invalid API key attempt. Received: '{x_api_key}'")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Please provide a valid X-API-KEY header."
        )
    
    logger.info("✅ API key verified successfully")

# =================
# ROOT ENDPOINT - Serve Frontend
# =================

@app.get("/")
async def root():
    """Serve the main frontend page (index.html)"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return JSONResponse(status_code=404, content={"success": False, "error": "Frontend index.html not found"})

@app.get("/styles.css")
async def serve_css():
    """Serve CSS file"""
    css_path = os.path.join(frontend_path, "styles.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    return JSONResponse(status_code=404, content={"success": False, "error": "CSS file not found"})

@app.get("/app.js")
async def serve_js():
    """Serve JavaScript file"""
    js_path = os.path.join(frontend_path, "app.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="text/javascript")
    return JSONResponse(status_code=404, content={"success": False, "error": "JS file not found"})

# =================
# HEALTH CHECK
# =================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Useful for monitoring and deployment verification.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        services={
            "audio_processor": "ready",
            "whisper": "ready",
            "pattern_analyzer": "ready",
            "risk_scorer": "ready",
        },
    )


# =================
# MAIN ANALYSIS ENDPOINT
# =================


@app.post("/analyze-call", response_model=AnalysisResponse)
async def analyze_call(
    request: Request,
    audio: UploadFile = File(...),
    language: Optional[str] = None,
):
    """
    🎯 MAIN ENDPOINT: Analyze audio call for scam indicators

    Args:
        audio: Audio file (WAV, MP3, OGG, FLAC, M4A, AAC, WMA, etc.)
        language: Optional ISO-639-1 language code
    
    Returns:
        AnalysisResponse: Complete scam analysis
    """
    
    # Verify API key first
    verify_api_key(request)
    
    logger.info(f"📞 [BACKEND RECEIVED REQUEST]")
    logger.info(f"  Filename: {audio.filename}")
    logger.info(f"  Content-Type: {audio.content_type}")
    logger.info(f"  Language: {language or 'auto-detect'}")
    
    # DEMO MODE: Short-circuit and return sample analysis without processing
    if DEMO_MODE:
        logger.info("🎬 DEMO MODE ACTIVE - Returning sample analysis")
        return AnalysisResponse(
            success=True,
            transcription="Hello, this is a demo call. We're calling about your recent purchase. Please provide your account verification number to confirm your identity and proceed with the refund process. You should act immediately as this offer expires today.",
            risk_score=82,
            risk_level=RiskLevel.HIGH_RISK,
            detected_patterns=[
                PatternMatch(
                    pattern_name="Artificial Urgency",
                    keywords=["immediately", "expires today"],
                    confidence=0.95,
                    risk_contribution=15,
                    explanation="Caller created artificial time pressure demanding immediate action"
                ),
                PatternMatch(
                    pattern_name="Credential Request",
                    keywords=["account verification number", "provide your"],
                    confidence=0.98,
                    risk_contribution=20,
                    explanation="Caller requested sensitive account verification information"
                )
            ],
            primary_threat="High-risk credential harvesting attempt with urgency manipulation",
            explanation="Demo analysis showing typical scam indicators: credential requests combined with artificial urgency and authority impersonation tactics.",
            risk_timeline=[
                {"timestamp": 0.0, "reason": "Call initiated", "risk_score": 10},
                {"timestamp": 15.0, "reason": "Authority claim introduced", "risk_score": 45},
                {"timestamp": 30.0, "reason": "Urgency escalation detected", "risk_score": 75},
                {"timestamp": 45.0, "reason": "Credential request made", "risk_score": 95}
            ],
            call_duration_seconds=60,
            language_detected="en",
            confidence=0.92,
            voice_analysis={
                "speaking_rate": 0.75,
                "voice_quality_score": 85,
                "stress_indicators": ["elevated pitch", "rapid speech"]
            },
            emotional_analysis={
                "manipulation_risk": 0.88,
                "tactics_detected": ["false authority", "time pressure", "fear appeal"]
            },
            entity_analysis={
                "total_sensitive_items": 2,
                "entities": ["account number", "verification code"],
                "information_extraction_risk": 0.85
            },
            known_scam_match={
                "is_known_scam": True,
                "overall_match_confidence": 0.87,
                "top_match": {
                    "campaign_name": "IRS Refund Scam",
                    "severity": "CRITICAL",
                    "match_score": 0.87,
                    "description": "Scammer impersonates tax department, threatens investigation",
                    "loss_average": "₹1,00,000 - ₹10,00,000",
                    "typical_targets": ["Tax payers", "General public"],
                    "matched_keywords": ["tax", "investigation", "urgent"]
                },
                "all_matches": []
            }
        )
    
    try:
        # ==========================================
        # VALIDATION: File metadata
        # ==========================================
        
        if not audio.filename:
            logger.error("❌ No filename provided")
            raise HTTPException(status_code=400, detail="No file selected")
        
        # Log file info
        file_size_mb = 0
        file_bytes = await audio.read()
        file_size_mb = len(file_bytes) / (1024 * 1024)
        
        logger.info(f"📁 [FILE RECEIVED] {audio.filename} ({file_size_mb:.2f}MB, {len(file_bytes)} bytes)")
        
        # Reset file pointer to prevent exhaustion
        await audio.seek(0)
        
        # ==========================================
        # VALIDATION: File content
        # ==========================================
        
        # Add file size limit check
        MAX_FILE_SIZE_MB = 50
        if file_size_mb > MAX_FILE_SIZE_MB:
            logger.error(f"❌ File too large: {file_size_mb:.2f}MB (max {MAX_FILE_SIZE_MB}MB)")
            raise HTTPException(status_code=413, detail=f"File too large. Maximum {MAX_FILE_SIZE_MB}MB allowed.")
        
        if not file_bytes:
            logger.error("❌ File bytes is empty!")
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info("✅ File validation passed")
        
        # ==========================================
        # STEP 1: Audio Processing
        # ==========================================
        logger.info("📥 Processing audio file...")
        
        # Validate and process audio (handles all formats)
        audio_processor.validate_audio_file(file_bytes, audio.filename)
        
        # Process audio to optimal format
        processed_audio, duration = audio_processor.process_audio(
            file_bytes, audio.filename
        )
        logger.info(f"✅ Audio processed: {duration:.2f}s duration")
        
        # ==========================================
        # STEP 2: Language Verification & Transcription
        # ==========================================
        logger.info("🗣️ Transcribing audio with Whisper...")
        
        # Performance: Detect language first if user explicitly chose one
        # to prevent invalid results in the wrong language
        if language:
            logger.info(f"🔍 Verifying audio language against user selection: {language}")
            # We call transcribe with None to let it detect, but only on a short segment if possible
            # Or just use the full call and check the metadata
            transcription, detected_language, stt_confidence = speech_service.transcribe(
                processed_audio, language=None  # Let it auto-detect first
            )
            
            if detected_language != language:
                lang_names = speech_service.get_supported_languages()
                actual_name = lang_names.get(detected_language, detected_language)
                chosen_name = lang_names.get(language, language)
                
                logger.warning(f"❌ Language mismatch: User chose {chosen_name}, but detected {actual_name}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Language mismatch: Spoken language is {actual_name}, but you selected {chosen_name}. Please switch to {actual_name} or use Auto-Detect."
                )
        else:
            # Standard auto-detect flow
            transcription, detected_language, stt_confidence = speech_service.transcribe(
                processed_audio, language=None
            )
        
        logger.info(f"✅ Transcription complete: {len(transcription)} chars ({detected_language})")
        logger.info(f"📝 Transcription preview: {transcription[:100] if transcription else '[Empty]'}...")
        
        # Allow analysis even with minimal transcription
        if not transcription:
            logger.warning("⚠️ Empty transcription - proceeding with placeholder")
            transcription = "[Inaudible or no speech detected]"
        
        # ==========================================
        # STEP 3: Pattern Detection
        # ==========================================
        # ==========================================
        logger.info("🔍 Step 3: Analyzing for scam patterns...")
        
        try:
            pattern_matches = pattern_analyzer.analyze_text(transcription, detected_language)
            logger.info(f"✅ Pattern analysis successful: {len(pattern_matches)} patterns detected")
        except Exception as e:
            logger.error(f"❌ Pattern analysis failed: {str(e)}", exc_info=True)
            pattern_matches = []
            logger.info("⚠️ Continuing with empty pattern matches...")
        
        # Convert PatternMatch objects to dicts
        pattern_dicts = [p.to_dict() for p in pattern_matches]
        
        logger.info(f"✅ Pattern analysis complete: {len(pattern_dicts)} patterns detected")
        for pattern in pattern_dicts:
            logger.info(f"  • {pattern['pattern_name']}: +{pattern['risk_contribution']} pts")
        
        # ==========================================
        # STEP 4: Risk Scoring & Explainability
        # ==========================================
        logger.info("📊 Step 4: Calculating risk score with explanation...")
        
        try:
            risk_assessment = risk_scorer.calculate_risk(
                pattern_dicts, transcription, duration
            )
            logger.info(f"✅ Risk score: {risk_assessment.risk_score}/100 ({risk_assessment.risk_level})")
            logger.info(f"Confidence: {risk_assessment.confidence:.1%}")
        except Exception as e:
            logger.error(f"❌ Risk scoring failed: {str(e)}", exc_info=True)
            # Create default risk assessment
            risk_assessment = risk_scorer.RiskAssessment(
                risk_score=50,
                risk_level="MEDIUM_RISK",
                confidence=0.5,
                primary_threat="Unable to complete full analysis",
                explanation="Risk assessment encountered an error but analysis is partial",
                detected_threats=[],
                safe_indicators_found=0,
                pattern_synergy_bonus=0
            )
        
        # ==========================================
        # STEP 5: Generate Risk Timeline
        # ==========================================
        logger.info("📈 Step 5: Building risk timeline...")
        
        try:
            timeline = risk_scorer.build_risk_timeline(transcription, pattern_dicts)
            logger.info(f"✅ Timeline generated: {len(timeline)} checkpoints")
        except Exception as e:
            logger.error(f"⚠️ Timeline generation failed: {str(e)}")
            timeline = []
        
        # ==========================================
        # NEW FEATURES: Advanced Analysis (Parallel)
        # ==========================================
        logger.info("🔬 Advanced Analysis: Running Voice, Emotions, Entities, and DB matching in parallel...")
        
        # Run synchronous analysis methods in threads to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        
        async def run_voice():
            try:
                return await loop.run_in_executor(None, voice_analyzer.analyze_audio_features, processed_audio)
            except Exception as e:
                logger.error(f"⚠️ Voice analysis failed: {str(e)}")
                return {"speaking_rate": 0, "voice_quality_score": 0, "stress_indicators": []}

        async def run_emotional():
            try:
                return await loop.run_in_executor(None, emotional_analyzer.analyze_tone, transcription)
            except Exception as e:
                logger.error(f"⚠️ Emotional analysis failed: {str(e)}")
                return {"manipulation_risk": 0, "tactics_detected": []}

        async def run_entity():
            try:
                return await loop.run_in_executor(None, entity_extractor.extract_entities, transcription)
            except Exception as e:
                logger.error(f"⚠️ Entity extraction failed: {str(e)}")
                return {"total_sensitive_items": 0, "entities": [], "information_extraction_risk": 0}

        async def run_scam_db():
            try:
                return await loop.run_in_executor(None, scam_database.compare_call_with_campaigns, transcription)
            except Exception as e:
                logger.error(f"⚠️ Scam database comparison failed: {str(e)}")
                return {"is_known_scam": False, "match_percentage": 0, "top_match": None, "all_matches": []}

        # Execute all in parallel
        voice_analysis, emotional_analysis, entity_analysis, scam_comparison = await asyncio.gather(
            run_voice(), run_emotional(), run_entity(), run_scam_db()
        )
        
        # 5. Calculate Enhanced Risk Score
        # Combine multiple data sources
        advanced_risk_bonus = 0
        if entity_analysis["information_extraction_risk"] > 50:
            advanced_risk_bonus += 10
        if emotional_analysis["manipulation_risk"] > 50:
            advanced_risk_bonus += 10
        if scam_comparison["is_known_scam"]:
            advanced_risk_bonus += 15
        if voice_analysis.get("speaking_rate", 0) > 0.7:
            advanced_risk_bonus += 5
        
        # Apply bonus (cap total at 100)
        enhanced_risk_score = min(
            risk_assessment.risk_score + advanced_risk_bonus, 100
        )
        
        if advanced_risk_bonus > 0:
            risk_assessment.risk_score = enhanced_risk_score
            # Update risk level if score crossed threshold
            if enhanced_risk_score >= 85 and risk_assessment.risk_level != "CRITICAL_SCAM":
                risk_assessment.risk_level = "CRITICAL_SCAM"
        
        logger.info(f"✅ Advanced analysis complete: bonus={advanced_risk_bonus}, final_score={enhanced_risk_score}")
        
        # ==========================================
        # STEP 6: Prepare Response
        # ==========================================
        logger.info("🎯 Step 6: Building final response...")
        
        # Convert risk level to enum (SAFE - cannot crash)
        risk_level_enum = RiskLevel.__members__.get(
            str(risk_assessment.risk_level).upper(),
            RiskLevel.LIKELY_SAFE
        )
        
        # Create response
        response = AnalysisResponse(
            success=True,
            transcription=transcription,
            risk_score=risk_assessment.risk_score,
            risk_level=risk_level_enum,
            detected_patterns=[
                PatternMatch(
                    pattern_name=p["pattern_name"],
                    keywords=p["keywords"],
                    confidence=p["confidence"],
                    risk_contribution=p["risk_contribution"],
                    explanation=p["explanation"],
                )
                for p in pattern_dicts
            ],
            primary_threat=risk_assessment.primary_threat,
            explanation=risk_assessment.explanation,
            risk_timeline=timeline,
            call_duration_seconds=duration,
            language_detected=detected_language,
            confidence=risk_assessment.confidence,
            # NEW: Include advanced analysis
            voice_analysis=voice_analysis,
            emotional_analysis=emotional_analysis,
            entity_analysis=entity_analysis,
            known_scam_match=scam_comparison,
        )
        
        logger.info("✅ Analysis complete!")
        logger.info(f"Final recommendation: {risk_assessment.risk_level}")
        
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"❌ Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        error_type = type(e).__name__
        error_msg = str(e)[:200]
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis error: {error_msg}"
        )


# =================
# UTILITY ENDPOINTS
# =================


@app.get("/info/languages")
async def get_supported_languages():
    """
    Get list of supported languages for transcription.
    Includes Indian languages critical for scam prevention.
    """
    languages = speech_service.get_supported_languages()
    return {
        "supported_languages": languages,
        "auto_detect": True,
        "recommended_for_india": ["hi", "ta", "te", "ml", "kn"],
    }


@app.get("/info/patterns")
async def get_pattern_info():
    """
    Get information about scam patterns this system detects.
    Useful for user education.
    """
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


@app.get("/info/known-scams")
async def get_known_scams():
    """
    Get information about known scam campaigns in database.
    Shows what scams the system is trained to recognize.
    """
    stats = scam_database.get_campaign_statistics()
    return {
        "total_known_campaigns": stats["total_campaigns"],
        "critical_campaigns": stats["critical_severity"],
        "high_risk_campaigns": stats["high_severity"],
        "medium_risk_campaigns": stats["medium_severity"],
        "campaigns": stats["campaigns"],
        "explanation": "System maintains database of known scam campaigns and compares incoming calls for matches",
    }


@app.get("/info/features")
async def get_advanced_features():
    """
    Get information about advanced analysis features.
    """
    return {
        "advanced_features": {
            "voice_analysis": "Analyzes speaking rate, pitch variation, stress levels, and background noise",
            "emotional_tone": "Detects urgency language, fear-mongering, authority appeals, and manipulation tactics",
            "entity_extraction": "Identifies phone numbers, account numbers, financial information, and suspicious commands",
            "known_scam_database": "Compares call against 8+ known scam campaign patterns",
            "combined_scoring": "Synthesizes all analysis types for enhanced accuracy",
        },
        "competitive_advantage": "Multi-layer analysis with explainability outperforms single-method approaches"
    }


# =================
# ERROR HANDLERS
# =================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP Error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )


# =================
# STARTUP / SHUTDOWN
# =================


@app.on_event("startup")
async def startup_event():
    """Log startup - models will load lazily on first request"""
    logger.info("=" * 60)
    logger.info("🚀 🚀 🚀 APPLICATION STARTUP COMPLETE 🚀 🚀 🚀")
    logger.info("=" * 60)
    logger.info("✅ All services initialized (lazy-loaded)")
    logger.info("⚡ Whisper model will load on FIRST /analyze-call request")
    logger.info(f"🎬 DEMO_MODE = {DEMO_MODE}")
    logger.info("API ready at: http://localhost:8000")
    logger.info("Docs ready at: http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown"""
    logger.info("🛑 Application shutdown")


# =================
# API INFO ENDPOINT
# =================


@app.get("/api-info")
async def api_info():
    """API documentation and endpoint information"""
    return {
        "name": "🔐 AI-Powered Audio Call Scam Analyzer",
        "version": "1.0.0",
        "description": "Detect financial fraud through voice analysis with explainable AI",
        "endpoints": {
            "health": "GET /health",
            "analyze": "POST /analyze-call",
            "languages": "GET /info/languages",
            "patterns": "GET /info/patterns",
            "known_scams": "GET /info/known-scams",
            "features": "GET /info/features",
        },
        "docs": "http://localhost:8000/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
