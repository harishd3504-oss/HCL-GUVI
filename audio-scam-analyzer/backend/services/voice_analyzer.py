"""
Advanced Voice Characteristics Analyzer
========================================
Analyzes audio features like speaking pace, pitch variation, stress levels,
and emotional tone - indicators of scam behavior.

Scammers tend to exhibit:
- Higher pitch variation (emotional intensity)
- Faster speaking pace (urgency, nervousness)
- Longer pauses (uncertainty)
- Background noise patterns (call centers)
"""

import numpy as np
import logging
from typing import Dict, Tuple, List
import librosa

logger = logging.getLogger(__name__)


class VoiceAnalyzer:
    """Analyzes voice characteristics from audio for scam indicators"""

    def __init__(self):
        """Initialize voice analyzer"""
        logger.info("VoiceAnalyzer initialized")

    def analyze_audio_features(self, audio_data: bytes) -> Dict:
        """
        Analyze voice characteristics from audio data.
        
        Args:
            audio_data: Audio file bytes
            
        Returns:
            Dict with voice analysis results
        """
        try:
            from io import BytesIO
            # Load audio from bytes buffer
            audio_buffer = BytesIO(audio_data)
            y, sr = librosa.load(audio_buffer, sr=None)
            
            # Guard against zero-length or silence
            if len(y) < 100:
                logger.warning("Audio too short for voice analysis")
                return self._get_default_analysis()

            # Extract features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            # Calculate speaking rate (energy changes per second)
            speaking_rate = self._calculate_speaking_rate(y, sr)
            
            # Calculate pitch variation
            pitch_variation = self._calculate_pitch_variation(y, sr)
            
            # Detect silence/pauses
            silence_ratio = self._calculate_silence_ratio(y, sr)
            
            # Background noise detection
            noise_level = self._detect_noise(y, sr)
            
            # Energy variation (stress indicator)
            energy_variation = self._calculate_energy_variation(y)
            
            # Confidence scoring based on voice features
            confidence_scores = self._calculate_voice_confidence(
                speaking_rate, pitch_variation, silence_ratio, noise_level
            )
            
            analysis = {
                "speaking_rate": speaking_rate,
                "pitch_variation": pitch_variation,
                "silence_ratio": silence_ratio,
                "noise_level": noise_level,
                "energy_variation": energy_variation,
                "spectral_centroid_mean": float(np.mean(spectral_centroid)),
                "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                "zero_crossing_rate_mean": float(np.mean(zero_crossing_rate)),
                "voice_quality_score": confidence_scores["voice_quality"],
                "authenticity_indicators": confidence_scores["authenticity"],
                "risk_indicators": self._assess_risk_from_voice(
                    speaking_rate, pitch_variation, silence_ratio, noise_level
                ),
            }
            
            logger.info(f"Voice analysis completed: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing voice features: {e}")
            return {
                "error": str(e),
                "speaking_rate": 0,
                "pitch_variation": 0,
                "silence_ratio": 0,
                "noise_level": 0,
                "energy_variation": 0,
            }

    def _get_default_analysis(self) -> Dict:
        """Return safe default analysis result"""
        return {
            "speaking_rate": 0,
            "pitch_variation": 0,
            "silence_ratio": 1.0,
            "noise_level": 0,
            "energy_variation": 0,
            "voice_quality_score": 0,
            "risk_indicators": ["Unable to analyze voice (audio issue)"]
        }

    def _calculate_speaking_rate(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate words per minute equivalent from audio energy.
        Returns normalized speaking rate (0-1 scale where 1 = very fast)
        """
        # Use RMS energy to detect speech segments
        frame_length = 2048
        hop_length = 512
        
        S = librosa.feature.melspectrogram(y=y, sr=sr, hop_length=hop_length)
        S_db = librosa.power_to_db(S, ref=np.max)
        
        # Count frames with significant energy (speech)
        speech_frames = np.sum(S_db > -40) / S_db.size
        
        # Normalize to 0-1 range
        speaking_rate = min(speech_frames * 2, 1.0)
        return float(speaking_rate)

    def _calculate_pitch_variation(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate pitch variation using spectral features.
        High variation = emotional intensity (scam indicator)
        """
        # Extract spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        # Calculate coefficient of variation
        variation = np.std(spectral_centroid) / (np.mean(spectral_centroid) + 1e-6)
        
        # Normalize to 0-1 range
        pitch_variation = min(variation / 2000, 1.0)
        return float(pitch_variation)

    def _calculate_silence_ratio(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate percentage of silence/pauses in audio.
        High ratio = uncertainty (scam indicator)
        """
        # Use energy threshold
        S = librosa.feature.melspectrogram(y=y, sr=sr)
        S_db = librosa.power_to_db(S, ref=np.max)
        
        # Frames below threshold are silence
        silence_frames = np.sum(S_db < -40)
        silence_ratio = silence_frames / S_db.size
        
        return float(min(silence_ratio, 1.0))

    def _detect_noise(self, y: np.ndarray, sr: int) -> float:
        """
        Detect background noise (call center indicator).
        Returns noise level 0-1 where 1 = very noisy
        """
        # Use spectral flatness to detect noise
        spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
        
        # Average flatness (higher = more noise-like)
        noise_level = np.mean(spectral_flatness)
        
        return float(min(noise_level * 2, 1.0))

    def _calculate_energy_variation(self, y: np.ndarray) -> float:
        """
        Calculate energy variation (stress indicator).
        Returns 0-1 where 1 = highly stressed/emotional
        """
        # Calculate frame energy
        frame_length = 2048
        hop_length = 512
        
        energy = np.array([
            np.sum(y[i:i + frame_length] ** 2)
            for i in range(0, len(y), hop_length)
        ])
        
        if len(energy) == 0:
            return 0.0
        
        # Coefficient of variation in energy
        energy_cv = np.std(energy) / (np.mean(energy) + 1e-6)
        
        return float(min(energy_cv / 10, 1.0))

    def _calculate_voice_confidence(
        self,
        speaking_rate: float,
        pitch_variation: float,
        silence_ratio: float,
        noise_level: float
    ) -> Dict:
        """Calculate confidence scores based on voice features"""
        
        # Voice quality score (0-100)
        # Lower noise = higher quality
        voice_quality = max(0, 100 - (noise_level * 50))
        
        # Authenticity indicators
        authenticity = {
            "natural_speaking_pattern": 0.8 if speaking_rate < 0.7 else 0.4,
            "consistent_tone": 0.7 if pitch_variation < 0.6 else 0.3,
            "minimal_hesitation": 0.8 if silence_ratio < 0.3 else 0.3,
            "clean_audio": 0.9 if noise_level < 0.3 else 0.4,
        }
        
        return {
            "voice_quality": voice_quality,
            "authenticity": authenticity,
        }

    def _assess_risk_from_voice(
        self,
        speaking_rate: float,
        pitch_variation: float,
        silence_ratio: float,
        noise_level: float
    ) -> List[str]:
        """Assess risk indicators from voice characteristics"""
        
        risk_indicators = []
        
        # High speaking rate = urgency (scam tactic)
        if speaking_rate > 0.7:
            risk_indicators.append("High speaking rate (urgency indicator)")
        
        # High pitch variation = emotional intensity
        if pitch_variation > 0.6:
            risk_indicators.append("High pitch variation (emotional intensity)")
        
        # High silence ratio = uncertainty/deception
        if silence_ratio > 0.4:
            risk_indicators.append("Frequent pauses and hesitation")
        
        # High noise = call center (common in scams)
        if noise_level > 0.4:
            risk_indicators.append("Background noise detected (possible call center)")
        
        return risk_indicators
