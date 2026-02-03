"""
Pydantic Models for Request/Response Validation
===============================================
Clean schemas for API inputs and outputs.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class RiskLevel(str, Enum):
    """Risk classification levels"""
    CRITICAL_SCAM = "CRITICAL_SCAM"
    HIGH_RISK = "HIGH_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    LOW_MEDIUM_RISK = "LOW_MEDIUM_RISK"
    LIKELY_SAFE = "LIKELY_SAFE"


class AnalysisRequest(BaseModel):
    """Request model for call analysis"""
    # Audio file will be sent as form-data, not JSON
    pass


class PatternMatch(BaseModel):
    """Individual pattern detection"""
    pattern_name: str = Field(..., description="Name of detected pattern")
    keywords: List[str] = Field(
        ..., description="Specific keywords that triggered detection"
    )
    confidence: float = Field(..., description="Confidence 0-1")
    risk_contribution: int = Field(..., description="How much this adds to risk score")
    explanation: str = Field(..., description="Human-readable explanation")


class RiskTimeline(BaseModel):
    """Track risk score progression over time"""
    timestamp: float = Field(..., description="Time in seconds from start")
    risk_score: int = Field(..., description="Risk score at this moment")
    reason: str = Field(..., description="What triggered the change")


class AnalysisResponse(BaseModel):
    """Response model for call analysis"""
    
    success: bool = Field(..., description="Whether analysis succeeded")
    transcription: str = Field(..., description="Full transcribed text from call")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    risk_level: RiskLevel = Field(..., description="Risk classification")
    
    # Explainability
    detected_patterns: List[PatternMatch] = Field(
        ..., description="All detected scam patterns with explanations"
    )
    primary_threat: str = Field(
        ..., description="Main reason for the flagging"
    )
    explanation: str = Field(
        ..., description="Natural language explanation for the user"
    )
    
    # Timeline of risk progression
    risk_timeline: List[RiskTimeline] = Field(
        default=[], description="How risk evolved during the call"
    )
    
    # Additional metadata
    call_duration_seconds: float = Field(
        ..., description="Length of audio analyzed"
    )
    language_detected: str = Field(
        default="en", description="Language detected in call"
    )
    confidence: float = Field(
        ..., description="Overall confidence in analysis (0-1)"
    )
    
    # NEW FEATURES: Advanced Analysis
    voice_analysis: Optional[Dict] = Field(
        default=None, description="Voice characteristics analysis (speaking rate, pitch, noise)"
    )
    emotional_analysis: Optional[Dict] = Field(
        default=None, description="Emotional tone and psychological tactics analysis"
    )
    entity_analysis: Optional[Dict] = Field(
        default=None, description="Extracted sensitive information (phones, accounts, names)"
    )
    known_scam_match: Optional[Dict] = Field(
        default=None, description="Match with known scam campaigns from database"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str = "1.0.0"
    services: Dict[str, str] = Field(
        default={
            "whisper": "ready",
            "scam_detector": "ready",
            "risk_scorer": "ready",
        }
    )
