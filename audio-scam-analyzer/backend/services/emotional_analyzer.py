"""
Emotional Tone Analyzer
=======================
Analyzes emotional tone indicators from transcribed text.
Scammers exhibit patterns like:
- Excessive urgency language
- Artificial emotional appeals
- Fear-mongering tactics
- False authority tone
"""

import re
import logging
from typing import Dict, List, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class EmotionalToneAnalyzer:
    """Analyzes emotional tone and psychological tactics in text"""

    def __init__(self):
        """Initialize emotional tone analyzer"""
        logger.info("EmotionalToneAnalyzer initialized")
        self.emotion_keywords = {
            "urgency": [
                "immediately", "right now", "urgent", "emergency", "asap",
                "quickly", "fast", "rush", "hurry", "now", "quickly",
                "don't delay", "without delay", "instantly", "immediately"
            ],
            "fear": [
                "danger", "risk", "threat", "problem", "issue", "worry",
                "concerned", "afraid", "scared", "terrible", "horrible",
                "disastrous", "blocked", "frozen", "account suspended",
                "fraud alert", "unauthorized", "compromised", "hacked"
            ],
            "authority": [
                "police", "fbi", "tax", "government", "official",
                "representative", "authority", "director", "manager",
                "agent", "officer", "department", "agency", "investigation"
            ],
            "flattery": [
                "trust", "friend", "help", "support", "care", "protect",
                "ensure", "secure", "safe", "verified", "legitimate",
                "professional", "experienced", "reliable"
            ],
            "urgency_phrases": [
                "act now", "limited time", "deadline", "time sensitive",
                "expires", "expiring", "valid until", "before",
                "hurry", "last chance", "final notice"
            ]
        }

    def analyze_tone(self, text: str) -> Dict:
        """
        Analyze emotional tone and psychological tactics.
        
        Args:
            text: Transcribed call text
            
        Returns:
            Dict with emotional tone analysis
        """
        text_lower = text.lower()
        
        # Detect emotions
        emotions = {}
        for emotion_type, keywords in self.emotion_keywords.items():
            emotion_matches = self._detect_emotion_keywords(text_lower, keywords)
            emotions[emotion_type] = {
                "detected": len(emotion_matches) > 0,
                "count": len(emotion_matches),
                "keywords": emotion_matches[:5],  # Top 5
                "intensity": self._calculate_emotion_intensity(len(emotion_matches), text),
            }
        
        # Psychological tactics score
        tactics_score = self._analyze_psychological_tactics(text_lower)
        
        # Overall emotional tone assessment
        tone_assessment = self._assess_overall_tone(emotions, tactics_score)
        
        analysis = {
            "emotions": emotions,
            "psychological_tactics": tactics_score,
            "tone_assessment": tone_assessment,
            "manipulation_risk": self._calculate_manipulation_risk(emotions),
            "emotional_intensity": sum(e["intensity"] for e in emotions.values()) / len(emotions),
        }
        
        logger.info(f"Tone analysis completed: manipulation_risk={analysis['manipulation_risk']}")
        return analysis

    def _detect_emotion_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Detect emotion keywords in text"""
        detected = []
        for keyword in keywords:
            # Use word boundary matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text)
            detected.extend(matches)
        return list(set(detected))  # Remove duplicates

    def _calculate_emotion_intensity(self, match_count: int, text: str) -> float:
        """Calculate intensity of emotion (0-1)"""
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        # Density of emotion words
        intensity = min((match_count / word_count) * 100, 1.0)
        return float(intensity)

    def _analyze_psychological_tactics(self, text: str) -> Dict:
        """Analyze psychological manipulation tactics"""
        tactics = {
            "authority_appeal": self._detect_authority_appeal(text),
            "fear_appeal": self._detect_fear_appeal(text),
            "scarcity_appeal": self._detect_scarcity_appeal(text),
            "social_proof": self._detect_social_proof(text),
            "false_urgency": self._detect_false_urgency(text),
            "reciprocity_appeal": self._detect_reciprocity_appeal(text),
        }
        
        return tactics

    def _detect_authority_appeal(self, text: str) -> Dict:
        """Detect appeal to authority tactic"""
        authority_keywords = ["said", "told me", "reported", "confirmed", "verified",
                            "official", "department", "government"]
        count = sum(1 for keyword in authority_keywords if keyword in text)
        
        return {
            "detected": count > 2,
            "intensity": min(count / 10, 1.0),
            "risk_level": "HIGH" if count > 4 else "MEDIUM" if count > 2 else "LOW"
        }

    def _detect_fear_appeal(self, text: str) -> Dict:
        """Detect fear-based appeal"""
        fear_words = ["danger", "risk", "threat", "problem", "fraud", "blocked",
                     "suspended", "frozen", "unauthorized", "hacked"]
        count = sum(1 for word in fear_words if word in text)
        
        return {
            "detected": count > 2,
            "intensity": min(count / 8, 1.0),
            "risk_level": "CRITICAL" if count > 5 else "HIGH" if count > 2 else "LOW"
        }

    def _detect_scarcity_appeal(self, text: str) -> Dict:
        """Detect scarcity/urgency appeal"""
        scarcity_words = ["limited", "only", "last", "expires", "deadline",
                         "hurry", "immediately", "now", "don't wait"]
        count = sum(1 for word in scarcity_words if word in text)
        
        return {
            "detected": count > 1,
            "intensity": min(count / 8, 1.0),
            "risk_level": "HIGH" if count > 3 else "MEDIUM" if count > 1 else "LOW"
        }

    def _detect_social_proof(self, text: str) -> Dict:
        """Detect false social proof tactic"""
        proof_words = ["everyone", "many", "others", "others are", "like you",
                      "similar situation", "most people"]
        count = sum(1 for word in proof_words if word in text)
        
        return {
            "detected": count > 1,
            "intensity": min(count / 6, 1.0),
            "risk_level": "MEDIUM" if count > 2 else "LOW"
        }

    def _detect_false_urgency(self, text: str) -> Dict:
        """Detect false urgency tactic"""
        urgency_phrases = [
            "immediately", "right now", "urgently", "asap",
            "don't delay", "act now", "time-sensitive"
        ]
        count = sum(1 for phrase in urgency_phrases if phrase in text)
        
        return {
            "detected": count > 0,
            "intensity": min(count / 5, 1.0),
            "risk_level": "HIGH" if count > 2 else "MEDIUM" if count > 0 else "LOW"
        }

    def _detect_reciprocity_appeal(self, text: str) -> Dict:
        """Detect reciprocity/obligation appeal"""
        reciprocity_words = ["help", "favor", "need", "assist", "support",
                            "protect", "ensure", "secure"]
        count = sum(1 for word in reciprocity_words if word in text)
        
        return {
            "detected": count > 2,
            "intensity": min(count / 8, 1.0),
            "risk_level": "MEDIUM" if count > 3 else "LOW"
        }

    def _assess_overall_tone(self, emotions: Dict, tactics: Dict) -> Dict:
        """Assess overall tone quality"""
        
        # Count intense emotions
        intense_count = sum(1 for e in emotions.values() if e["intensity"] > 0.5)
        
        # Count dangerous tactics
        dangerous_tactics = sum(
            1 for t in tactics.values() 
            if t.get("detected") and t.get("risk_level") in ["HIGH", "CRITICAL"]
        )
        
        if dangerous_tactics >= 3 and intense_count >= 2:
            tone_type = "HIGHLY MANIPULATIVE"
            risk_level = "CRITICAL"
        elif dangerous_tactics >= 2:
            tone_type = "MANIPULATIVE"
            risk_level = "HIGH"
        elif intense_count >= 2:
            tone_type = "EMOTIONALLY CHARGED"
            risk_level = "MEDIUM"
        else:
            tone_type = "NEUTRAL"
            risk_level = "LOW"
        
        return {
            "tone_type": tone_type,
            "risk_level": risk_level,
            "intense_emotions": intense_count,
            "suspicious_tactics": dangerous_tactics
        }

    def _calculate_manipulation_risk(self, emotions: Dict) -> float:
        """Calculate overall manipulation risk (0-100)"""
        
        # Weight different emotions
        urgency_weight = emotions.get("urgency", {}).get("intensity", 0) * 25
        fear_weight = emotions.get("fear", {}).get("intensity", 0) * 30
        authority_weight = emotions.get("authority", {}).get("intensity", 0) * 25
        flattery_weight = emotions.get("flattery", {}).get("intensity", 0) * 20
        
        risk = min(urgency_weight + fear_weight + authority_weight + flattery_weight, 100)
        
        return float(risk)
