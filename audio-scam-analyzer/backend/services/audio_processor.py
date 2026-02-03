"""
Audio Processing Service
=======================
Handles audio file ingestion, validation, and format conversion.
This is the first layer of the system - ensures audio is ready for Whisper.

PRIVACY POLICY: Audio files are processed in-memory only.
No files are persisted to disk. Processing is temporary.
"""

import os
import librosa
import soundfile as sf
from io import BytesIO
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Processes audio files for speech-to-text analysis.
    Supports WAV, MP3, OGG, and FLAC formats.
    """

    # Supported audio formats
    SUPPORTED_FORMATS = {"wav", "mp3", "m4a", "ogg", "flac", "opus"}

    # Audio constraints for analysis
    MAX_DURATION_SECONDS = 600  # 10 minutes max
    MIN_DURATION_SECONDS = 1  # 1 second minimum
    TARGET_SAMPLE_RATE = 16000  # Whisper-optimized sample rate

    def __init__(self):
        """Initialize audio processor"""
        self.sample_rate = self.TARGET_SAMPLE_RATE
        logger.info("AudioProcessor initialized")

    def validate_audio_file(self, file_bytes: bytes, filename: str) -> bool:
        """
        Validate audio file is not empty and has a supported format.
        """
        if not file_bytes or len(file_bytes) == 0:
            raise ValueError("Empty audio file")

        # Check extension
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext and ext not in self.SUPPORTED_FORMATS:
            logger.warning(f"Unsupported format: {ext}")
            # We still try to process it as librosa might handle it, 
            # but we log the warning.

        file_size_mb = len(file_bytes) / (1024 * 1024)
        if file_size_mb > 50:
            raise ValueError(f"File too large ({file_size_mb:.1f}MB). Max 50MB allowed.")

        logger.info(
            f"Audio validation passed: {filename} ({file_size_mb:.2f}MB)"
        )
        return True

    def process_audio(self, file_bytes: bytes, filename: str) -> Tuple[bytes, float]:
        """
        Convert audio to optimal format for Whisper.
        Handles format conversion, resampling, and normalization.

        Args:
            file_bytes: Raw audio bytes
            filename: Original filename

        Returns:
            Tuple of (processed_audio_bytes, duration_seconds)
        """
        # Validate first
        self.validate_audio_file(file_bytes, filename)

        try:
            # Load audio with automatic format detection
            audio_buffer = BytesIO(file_bytes)
            audio_data, sr = librosa.load(audio_buffer, sr=None, mono=True)

            # Get duration
            duration = librosa.get_duration(y=audio_data, sr=sr)
            
            if duration < self.MIN_DURATION_SECONDS:
                raise ValueError(f"Audio too short ({duration:.2f}s). Minimum 1 second required.")
            
            if duration > self.MAX_DURATION_SECONDS:
                raise ValueError(f"Audio too long ({duration:.2f}s). Maximum 10 minutes allowed.")

            logger.info(f"✅ Audio duration: {duration:.2f}s")
            logger.info(f"Audio shape: {audio_data.shape}, sample rate: {sr} Hz")

            # Resample to 16kHz (Whisper-optimized)
            if sr != self.TARGET_SAMPLE_RATE:
                audio_data = librosa.resample(
                    audio_data, orig_sr=sr, target_sr=self.TARGET_SAMPLE_RATE
                )

            # Normalize audio amplitude to prevent clipping
            # This helps with whisper's speech recognition
            max_amplitude = max(abs(audio_data.min()), abs(audio_data.max()))
            if max_amplitude > 0:
                audio_data = audio_data / max_amplitude * 0.95

            # Convert to WAV format for consistent processing
            output_buffer = BytesIO()
            sf.write(output_buffer, audio_data, self.TARGET_SAMPLE_RATE, format="WAV")
            output_buffer.seek(0)
            processed_bytes = output_buffer.read()

            logger.info(
                f"Audio processed: {duration:.2f}s, {len(processed_bytes)} bytes"
            )
            return processed_bytes, duration

        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            raise RuntimeError(f"Failed to process audio: {str(e)}")

    @staticmethod
    def get_audio_metadata(file_bytes: bytes) -> dict:
        """
        Extract metadata from audio file without full processing.
        Useful for quick validation.

        Args:
            file_bytes: Raw audio bytes

        Returns:
            Dictionary with file info
        """
        try:
            audio_buffer = BytesIO(file_bytes)
            audio_data, sr = librosa.load(audio_buffer, sr=None, mono=True)
            duration = librosa.get_duration(y=audio_data, sr=sr)

            return {
                "duration_seconds": duration,
                "sample_rate": sr,
                "channels": 1,  # We convert to mono
                "format": "wav",
            }
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {}
