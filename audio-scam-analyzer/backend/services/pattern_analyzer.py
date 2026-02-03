"""
Pattern Analyzer Service
=======================
Detects social engineering and scam patterns in transcribed text.

This is the "intelligence" layer - where we identify:
- Artificial urgency
- Authority impersonation
- Fear-based manipulation
- OTP/credential requests
- Trust building attempts

Uses keyword matching + linguistic heuristics (no ML model needed for demo).
Production version could use fine-tuned transformers.
"""

import re
from typing import List, Dict, Tuple, Set
import logging

from utils.constants import (
    URGENCY_KEYWORDS,
    BANKING_KEYWORDS,
    AUTHORITY_KEYWORDS,
    FEAR_KEYWORDS,
    TRUST_KEYWORDS,
    OTP_KEYWORDS,
    SAFE_INDICATORS,
    HINDI_INDICATORS,
    TAMIL_INDICATORS,
    EXPLANATION_TEMPLATES,
)

logger = logging.getLogger(__name__)


class PatternMatch:
    """Represents a detected pattern"""

    def __init__(
        self,
        pattern_name: str,
        matched_keywords: List[str],
        risk_score: int,
        explanation: str,
        confidence: float = 0.8,
    ):
        self.pattern_name = pattern_name
        self.matched_keywords = matched_keywords
        self.risk_score = risk_score
        self.explanation = explanation
        self.confidence = confidence

    def to_dict(self) -> dict:
        return {
            "pattern_name": self.pattern_name,
            "keywords": self.matched_keywords,
            "risk_contribution": self.risk_score,
            "explanation": self.explanation,
            "confidence": self.confidence,
        }


class PatternAnalyzer:
    """
    Detects scam patterns in transcribed text.
    Organized by social engineering attack type.
    """

    def __init__(self):
        """Initialize pattern analyzer"""
        logger.info("PatternAnalyzer initialized")

    def analyze_text(self, text: str, language: str = "en") -> List[PatternMatch]:
        """
        Analyze transcribed text for scam patterns.

        Args:
            text: Transcribed call text
            language: Language code for multilingual detection

        Returns:
            List of detected patterns with risk scores
        """
        text_lower = text.lower()
        patterns = []

        # 1. Check for OTP/credential requests (HIGHEST PRIORITY)
        otp_match = self._detect_otp_request(text_lower)
        if otp_match:
            patterns.append(otp_match)

        # 2. Check for artificial urgency
        urgency_match = self._detect_urgency(text_lower)
        if urgency_match:
            patterns.append(urgency_match)

        # 3. Check for authority impersonation
        authority_match = self._detect_authority_impersonation(text_lower)
        if authority_match:
            patterns.append(authority_match)

        # 4. Check for fear-based language
        fear_match = self._detect_fear_tactics(text_lower)
        if fear_match:
            patterns.append(fear_match)

        # 5. Check for financial exploitation
        finance_match = self._detect_financial_targeting(text_lower)
        if finance_match:
            patterns.append(finance_match)

        # 6. Check for info requests (combined with other patterns)
        info_match = self._detect_information_requests(text_lower)
        if info_match:
            patterns.append(info_match)

        # 7. Multilingual pattern detection
        if language != "en":
            multilingual_matches = self._detect_multilingual_patterns(
                text_lower, language
            )
            patterns.extend(multilingual_matches)

        logger.info(f"Pattern analysis complete: {len(patterns)} patterns detected")
        return patterns

    def _detect_otp_request(self, text: str) -> PatternMatch | None:
        """
        🚨 CRITICAL: Detect OTP or credential requests.
        Legitimate institutions NEVER request OTPs via phone.
        This is an absolute red flag.
        """
        keywords_found = self._find_keywords(text, OTP_KEYWORDS)

        if len(keywords_found) > 0:
            # Check if it's a request for the OTP (not just mention)
            if self._is_request_pattern(text, keywords_found):
                logger.warning("🚨 OTP request detected!")
                return PatternMatch(
                    pattern_name="OTP/Credential Request",
                    matched_keywords=keywords_found,
                    risk_score=100,  # Absolute maximum - game over
                    explanation=EXPLANATION_TEMPLATES["otp_request"],
                    confidence=0.99,
                )

        return None

    def _detect_urgency(self, text: str) -> PatternMatch | None:
        """
        Detect artificial urgency and time pressure.
        Scammers use urgency to prevent victims from thinking clearly.
        """
        keywords_found = self._find_keywords(text, URGENCY_KEYWORDS)

        if len(keywords_found) >= 2:  # Need multiple urgency markers
            logger.warning(f"⚠️ Urgency detected: {keywords_found}")
            explanation = EXPLANATION_TEMPLATES["urgency_pressure"].format(
                keywords=", ".join(keywords_found[:2])
            )
            return PatternMatch(
                pattern_name="Artificial Urgency",
                matched_keywords=keywords_found,
                risk_score=20,
                explanation=explanation,
                confidence=0.85,
            )

        return None

    def _detect_authority_impersonation(self, text: str) -> PatternMatch | None:
        """
        Detect impersonation of legitimate institutions.
        Scammers claim to be: banks, RBI, police, tax authorities, etc.
        """
        authority_keywords = self._find_keywords(text, AUTHORITY_KEYWORDS)

        if len(authority_keywords) > 0:
            # Check if it's a claim or statement (not just mention)
            if self._is_authority_claim(text, authority_keywords):
                logger.warning(f"👤 Authority impersonation detected: {authority_keywords}")
                authority = authority_keywords[0]
                explanation = EXPLANATION_TEMPLATES["authority_fake"].format(
                    authority=authority.capitalize()
                )
                return PatternMatch(
                    pattern_name="Authority Impersonation",
                    matched_keywords=authority_keywords,
                    risk_score=25,
                    explanation=explanation,
                    confidence=0.80,
                )

        return None

    def _detect_fear_tactics(self, text: str) -> PatternMatch | None:
        """
        Detect fear-based manipulation language.
        Scammers use threats: "your account will be closed", "you'll face legal action", etc.
        """
        fear_keywords = self._find_keywords(text, FEAR_KEYWORDS)

        if len(fear_keywords) >= 2:
            logger.warning(f"😨 Fear tactics detected: {fear_keywords}")
            explanation = EXPLANATION_TEMPLATES["fear_based"].format(
                keywords=", ".join(fear_keywords[:2])
            )
            return PatternMatch(
                pattern_name="Fear-Based Pressure",
                matched_keywords=fear_keywords,
                risk_score=20,
                explanation=explanation,
                confidence=0.75,
            )

        return None

    def _detect_financial_targeting(self, text: str) -> PatternMatch | None:
        """
        Detect targeting of financial information or money.
        Multiple banking keywords = exploitation attempt.
        """
        banking_keywords = self._find_keywords(text, BANKING_KEYWORDS)

        if len(banking_keywords) >= 3:
            logger.warning(f"💰 Financial targeting detected: {banking_keywords}")
            explanation = EXPLANATION_TEMPLATES["financial_exploitation"].format(
                keywords=", ".join(banking_keywords[:3])
            )
            return PatternMatch(
                pattern_name="Financial Information Targeting",
                matched_keywords=banking_keywords,
                risk_score=15,
                explanation=explanation,
                confidence=0.80,
            )

        return None

    def _detect_information_requests(self, text: str) -> PatternMatch | None:
        """
        Detect requests for sensitive personal or financial information.
        """
        request_phrases = [
            r"(can you|could you|would you)\s+(provide|share|tell|give).*(account|number|password|otp|card)",
            r"(provide|share|tell|give).*(account number|card number|password|otp|pin)",
            r"(verify|confirm)\s+(your|the)\s+(account|identity|password)",
        ]

        for pattern in request_phrases:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("Information request detected")
                return PatternMatch(
                    pattern_name="Information Request",
                    matched_keywords=["account/password request"],
                    risk_score=30,
                    explanation="🔑 Request for sensitive account or personal information detected",
                    confidence=0.85,
                )

        return None

    def _detect_multilingual_patterns(
        self, text: str, language: str
    ) -> List[PatternMatch]:
        """
        Detect patterns in non-English languages.
        Currently supports Hindi, Tamil, and others.
        """
        matches = []

        if language == "hi":  # Hindi
            hindi_urgency = self._find_keywords(text, HINDI_INDICATORS["urgency"])
            if len(hindi_urgency) > 0:
                matches.append(
                    PatternMatch(
                        pattern_name="Hindi Urgency (Translated)",
                        matched_keywords=hindi_urgency,
                        risk_score=15,
                        explanation="⚠️ Urgency detected in Hindi conversation",
                        confidence=0.70,
                    )
                )
        
        elif language == "ta":  # Tamil
            # 1. Tamil Urgency
            tamil_urgency = self._find_keywords(text, TAMIL_INDICATORS["urgency"])
            if len(tamil_urgency) >= 2:
                matches.append(PatternMatch(
                    pattern_name="Tamil Urgency",
                    matched_keywords=tamil_urgency,
                    risk_score=15,
                    explanation="⚠️ Artificial urgency detected in Tamil audio",
                    confidence=0.85
                ))
            
            # 2. Tamil Banking/Financial
            tamil_banking = self._find_keywords(text, TAMIL_INDICATORS["banking"])
            if len(tamil_banking) >= 2:
                matches.append(PatternMatch(
                    pattern_name="Tamil Financial Target",
                    matched_keywords=tamil_banking,
                    risk_score=15,
                    explanation="💰 Financial keywords detected in Tamil conversation",
                    confidence=0.80
                ))

            # 3. Tamil OTP Request
            tamil_otp = self._find_keywords(text, TAMIL_INDICATORS["otp"])
            if len(tamil_otp) >= 1:
                matches.append(PatternMatch(
                    pattern_name="Tamil OTP Request",
                    matched_keywords=tamil_otp,
                    risk_score=100,
                    explanation="🚨 CRITICAL: Request for OTP or secret code detected in Tamil",
                    confidence=0.95
                ))

        return matches

    # ==================
    # HELPER METHODS
    # ==================

    def _find_keywords(self, text: str, keyword_list: List[str]) -> List[str]:
        """
        Find all keywords from a list that appear in text.
        Returns unique keywords found (case-insensitive).
        """
        found = set()
        for keyword in keyword_list:
            # Use word boundary to avoid partial matches
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                found.add(keyword.lower())

        return list(found)

    def _is_request_pattern(self, text: str, keywords: List[str]) -> bool:
        """
        Check if keywords are used in a REQUEST context.
        E.g., "tell me your OTP" vs "I received an OTP"
        """
        request_indicators = [
            "tell",
            "provide",
            "share",
            "give",
            "send",
            "confirm",
            "verify",
            "please",
        ]

        # Look for request keywords near OTP keywords
        text_window = text  # Full text for hackathon (production: use context windows)

        for req_word in request_indicators:
            if req_word in text_window:
                # Found request pattern
                return True

        return False

    def _is_authority_claim(self, text: str, authority_keywords: List[str]) -> bool:
        """
        Check if the text contains a CLAIM of being an authority.
        E.g., "This is the bank calling" vs "I was contacting the bank"
        """
        claim_patterns = [
            r"(this is|i['\s]*am|calling from|from the)\s+",
            r"(official|representative of)",
        ]

        for pattern in claim_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def get_pattern_summary(self, patterns: List[PatternMatch]) -> str:
        """
        Generate human-readable summary of detected patterns.
        Used in explainability.
        """
        if not patterns:
            return "No scam patterns detected"

        summary_parts = []
        for pattern in patterns:
            summary_parts.append(f"• {pattern.pattern_name}: {pattern.explanation}")

        return "\n".join(summary_parts)
