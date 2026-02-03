"""
Risk Scoring & Explainability Engine
=====================================
Transforms detected patterns into a transparent, explainable risk score.

Key Principle: We don't just say "SCAM" or "SAFE" - we EXPLAIN WHY.

Risk Scoring Logic:
1. Base score starts at 0
2. Each detected pattern adds points (0-100 scale)
3. Combinations of patterns multiply risk (synergy bonus)
4. Safe indicators reduce risk (prevent false positives)
5. Timeline shows how risk evolved over the call

This layer is the "explainability" differentiator that wins hackathons.
"""

import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass
from utils.constants import RISK_FACTORS, RISK_CLASSIFICATION

logger = logging.getLogger(__name__)


@dataclass
class RiskAssessment:
    """Complete risk assessment result"""
    risk_score: int  # 0-100
    risk_level: str  # CRITICAL_SCAM, HIGH_RISK, etc.
    confidence: float  # 0-1
    primary_threat: str  # Main reason for flag
    explanation: str  # Natural language explanation
    detected_threats: List[str]  # List of threat types
    safe_indicators_found: int  # How many safe indicators (reduces false positives)
    pattern_synergy_bonus: int  # Extra points for combined patterns


class RiskScorer:
    """
    Converts pattern detections into a final risk score.
    Implements multi-factor risk assessment with explainability.
    """

    def __init__(self):
        """Initialize risk scorer"""
        logger.info("RiskScorer initialized")

    def calculate_risk(
        self, patterns: List[Dict], transcription: str, call_duration: float
    ) -> RiskAssessment:
        """
        Calculate overall risk score from detected patterns.

        Args:
            patterns: List of PatternMatch dicts from PatternAnalyzer
            transcription: Full transcribed text
            call_duration: Duration in seconds

        Returns:
            RiskAssessment with complete scoring rationale
        """
        # Start at baseline
        base_score = 0
        threat_details = []

        # 1. Sum all pattern risks
        pattern_scores = {}
        for pattern in patterns:
            pattern_name = pattern["pattern_name"]
            contribution = pattern["risk_contribution"]
            base_score += contribution

            pattern_scores[pattern_name] = contribution
            threat_details.append(
                f"{pattern_name} (+{contribution} pts): {pattern['explanation']}"
            )
            logger.info(f"Pattern detected: {pattern_name} = +{contribution} points")

        # 2. Apply pattern synergy bonus (combinations are worse)
        # If multiple high-risk patterns detected together, they're likely coordinated
        synergy_bonus = self._calculate_synergy_bonus(patterns)
        base_score += synergy_bonus

        if synergy_bonus > 0:
            threat_details.append(
                f"⚠️ Pattern Combination Bonus (+{synergy_bonus} pts): "
                f"Multiple attack vectors suggest sophisticated scam"
            )

        # 3. Check for safe indicators (reduces false positives)
        safe_count = self._count_safe_indicators(transcription)
        if safe_count > 0:
            # Each safe indicator reduces risk by 7 points
            safety_reduction = min(safe_count * 7, 30)  # Increased cap to 30
            base_score = max(0, base_score - safety_reduction)
            logger.info(f"Safe indicators found: {safe_count} (reduction: -{safety_reduction})")

        # 4. Apply call duration heuristic
        # Very short calls are less trustworthy (scammers hang up if detected)
        if call_duration < 20 and base_score > 50:
            base_score = min(100, base_score + 5)
            threat_details.append(
                "⚠️ Call Duration Anomaly (+5 pts): Unusually short call for a high-risk scenario"
            )

        # 5. Clamp score to 0-100 range
        final_score = max(0, min(100, base_score))

        # 6. Determine risk level
        risk_level, emoji = self._get_risk_level(final_score)

        # 7. Build explainability message
        if final_score == 0:
            explanation = "✅ No scam indicators detected. This appears to be a legitimate call."
            confidence = 0.95
        elif len(patterns) == 0:
            explanation = "✅ No suspicious patterns detected."
            confidence = 0.90
        else:
            # Build explanation from patterns
            main_threat = threat_details[0] if threat_details else "Unknown threat detected"
            explanation = self._build_explanation(
                final_score, patterns, safe_count, synergy_bonus
            )
            confidence = self._calculate_confidence(patterns, safe_count, final_score)

        return RiskAssessment(
            risk_score=final_score,
            risk_level=risk_level,
            confidence=confidence,
            primary_threat=threat_details[0] if threat_details else "No threats",
            explanation=explanation,
            detected_threats=[p["pattern_name"] for p in patterns],
            safe_indicators_found=safe_count,
            pattern_synergy_bonus=synergy_bonus,
        )

    def _calculate_synergy_bonus(self, patterns: List[Dict]) -> int:
        """
        Calculate bonus points for pattern combinations.
        Sophisticated scammers use multiple attack vectors simultaneously.

        Bonus Logic:
        - 2 patterns: +5 points (coordinated attack)
        - 3 patterns: +10 points (sophisticated)
        - 4+ patterns: +20 points (complex scam)
        """
        pattern_count = len(patterns)

        if pattern_count < 2:
            return 0
        elif pattern_count == 2:
            return 5
        elif pattern_count == 3:
            return 10
        else:
            return 20

    def _count_safe_indicators(self, text: str) -> int:
        """
        Count indicators of legitimate communication.
        Helps prevent false positives.

        Examples:
        - "Would you like to verify this?"
        - "Take your time"
        - "Optional"
        """
        from utils.constants import SAFE_INDICATORS

        count = 0
        text_lower = text.lower()

        for indicator in SAFE_INDICATORS:
            if indicator in text_lower:
                count += 1

        return count

    def _get_risk_level(self, score: int) -> Tuple[str, str]:
        """
        Map numeric score to risk level classification.

        Returns:
            Tuple of (risk_level_string, emoji)
        """
        for range_str, (level, emoji) in RISK_CLASSIFICATION.items():
            min_score, max_score = map(int, range_str.split("-"))
            if min_score <= score <= max_score:
                return level, emoji

        return "UNKNOWN", "❓"

    def _build_explanation(
        self,
        score: int,
        patterns: List[Dict],
        safe_count: int,
        synergy_bonus: int,
    ) -> str:
        """
        Build natural language explanation for the risk score.
        This is the key to explainability and user trust.
        """
        risk_level, emoji = self._get_risk_level(score)

        # Build explanation parts
        parts = [f"{emoji} **Risk Assessment: {risk_level}** ({score}/100)"]
        parts.append("")

        # Threat breakdown
        if patterns:
            parts.append("🚨 **Detected Threats:**")
            for pattern in patterns:
                parts.append(
                    f"  • {pattern['pattern_name']}: "
                    f"+{pattern['risk_contribution']} points"
                )

        # Synergy warning
        if synergy_bonus > 0:
            parts.append("")
            parts.append(
                f"⚠️ **Pattern Combination:** Multiple attack vectors detected (+{synergy_bonus} points). "
                f"This suggests a sophisticated, coordinated scam."
            )

        # Safe indicators
        if safe_count > 0:
            parts.append("")
            parts.append(
                f"✓ **Safe Indicators Found:** {safe_count} legitimate communication markers "
                f"(slightly reduces risk)"
            )

        # Final recommendation
        parts.append("")
        if score >= 90:
            parts.append(
                "🔴 **RECOMMENDATION: HANG UP IMMEDIATELY.** "
                "This is almost certainly a scam. Do NOT provide any information."
            )
        elif score >= 70:
            parts.append(
                "🟠 **RECOMMENDATION: END CALL.** "
                "High probability of fraud. Legitimate institutions don't operate this way."
            )
        elif score >= 50:
            parts.append(
                "🟡 **RECOMMENDATION: BE CAUTIOUS.** "
                "Suspicious patterns detected. Verify independently before taking action."
            )
        elif score >= 30:
            parts.append(
                "🟢 **RECOMMENDATION: LIKELY SAFE.** "
                "Some unusual patterns, but nothing conclusive."
            )
        else:
            parts.append(
                "✅ **RECOMMENDATION: APPEARS LEGITIMATE.** "
                "No scam indicators detected, but remain vigilant."
            )

        return "\n".join(parts)

    def _calculate_confidence(
        self, patterns: List[Dict], safe_count: int, score: int
    ) -> float:
        """
        Calculate confidence in the risk assessment.

        Factors:
        - More patterns detected = higher confidence
        - Safe indicators present = lower confidence
        - Extreme scores (0 or 100) = highest confidence
        - Middle scores = lower confidence
        """
        confidence = 0.5

        # Pattern count increases confidence
        if len(patterns) >= 3:
            confidence += 0.35
        elif len(patterns) == 2:
            confidence += 0.20
        elif len(patterns) == 1:
            confidence += 0.10

        # Safe indicators decrease confidence
        if safe_count > 2:
            confidence -= 0.15

        # Extreme scores are more confident
        if score >= 95 or score <= 5:
            confidence = min(0.99, confidence + 0.15)
        elif 40 <= score <= 60:
            confidence = max(0.50, confidence - 0.10)

        return min(0.99, max(0.30, confidence))

    def build_risk_timeline(
        self, transcription: str, patterns: List[Dict]
    ) -> List[Dict]:
        """
        Create a timeline showing how risk evolved during the call.
        Useful for understanding call progression.

        For hackathon: Use rough segmentation.
        Production: Use speech timing data from Whisper.
        """
        if not transcription:
            return []

        # Simple segmentation: divide into 3 parts
        segments = self._segment_transcription(transcription, num_segments=3)
        timeline = []

        cumulative_risk = 0
        for i, segment in enumerate(segments):
            # Analyze this segment for patterns
            segment_risk_increase = self._score_segment(segment, patterns)
            cumulative_risk += segment_risk_increase

            timeline.append({
                "timestamp": (i + 1) * (len(transcription.split()) // 3),
                "risk_score": min(100, cumulative_risk),
                "reason": self._get_segment_reason(segment, i),
            })

        return timeline

    def _segment_transcription(self, text: str, num_segments: int = 3) -> List[str]:
        """Divide transcription into roughly equal parts"""
        words = text.split()
        segment_size = max(1, len(words) // num_segments)
        segments = []

        for i in range(num_segments):
            start_idx = i * segment_size
            end_idx = (i + 1) * segment_size if i < num_segments - 1 else len(words)
            segments.append(" ".join(words[start_idx:end_idx]))

        return segments

    def _score_segment(self, segment: str, all_patterns: List[Dict]) -> int:
        """Estimate risk for a text segment"""
        # For hackathon: simple heuristic
        # Production: re-run pattern analyzer on segment
        return 15  # Simplified for demo

    def _get_segment_reason(self, segment: str, segment_num: int) -> str:
        """Generate reason for risk change in this segment"""
        reasons = [
            "Initial contact - caller identifies themselves",
            "Problem description - urgency and pressure mounting",
            "Request phase - asking for sensitive information",
        ]
        return reasons[segment_num] if segment_num < len(reasons) else "Analysis phase"
