"""
app/pipeline/asr_tts.py
Multi-dialect ASR (Speech-to-Text) + TTS (Text-to-Speech) Engine

Supports: Hindi (hi-IN), Awadhi (awa-IN), Bhojpuri (bho-IN), English (en-IN)
Primary backend: OpenAI Whisper API
Fallback: Google Cloud Speech-to-Text
"""
from __future__ import annotations

import base64
import io
import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import httpx
import openai
from pydub import AudioSegment
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)

# Dialect → Whisper language code mapping
DIALECT_TO_WHISPER_LANG: dict[str, str] = {
    "hi-IN":  "hi",    # Hindi
    "awa-IN": "hi",    # Awadhi → treated as Hindi by Whisper (closest)
    "bho-IN": "hi",    # Bhojpuri → Hindi fallback
    "en-IN":  "en",    # English
}

# Dialect → Google TTS language code
DIALECT_TO_TTS_LANG: dict[str, str] = {
    "hi-IN":  "hi-IN",
    "awa-IN": "hi-IN",
    "bho-IN": "hi-IN",
    "en-IN":  "en-IN",
}

# Dialect tag injected into transcript for downstream models
DIALECT_TAGS: dict[str, str] = {
    "hi-IN":  "[HINDI]",
    "awa-IN": "[AWADHI]",
    "bho-IN": "[BHOJPURI]",
    "en-IN":  "[ENGLISH]",
}

# Prompt prefixes to bias Whisper toward regional vocabulary
WHISPER_PROMPTS: dict[str, str] = {
    "hi-IN":  "यह एक सरकारी शिकायत है। नागरिक की समस्या:",
    "awa-IN": "यह एक सरकारी फरियाद है। नागरिक की समस्या:",
    "bho-IN": "यह एक सरकारी शिकायत है। नागरिक के बात:",
    "en-IN":  "This is a government grievance complaint filed by a citizen:",
}


class ASREngine:
    """
    Multi-dialect Automatic Speech Recognition.

    Usage:
        asr = ASREngine()
        result = await asr.transcribe(audio_bytes, dialect="hi-IN", mime="audio/webm")
    """

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def transcribe(
        self,
        audio_bytes: bytes,
        dialect: str = "hi-IN",
        mime: str = "audio/webm",
    ) -> dict:
        """
        Transcribe audio bytes.

        Returns:
            {
                "transcript": str,         # raw transcript
                "normalized":  str,         # dialect-tagged normalized text
                "dialect":     str,
                "confidence":  float,
                "words":       list,        # word-level timestamps if available
                "language_detected": str
            }
        """
        lang    = DIALECT_TO_WHISPER_LANG.get(dialect, "hi")
        prompt  = WHISPER_PROMPTS.get(dialect, "")
        tag     = DIALECT_TAGS.get(dialect, "[HINDI]")
        ext     = self._mime_to_ext(mime)

        # Convert to MP3 for Whisper (smaller, universally supported)
        audio_mp3 = self._convert_to_mp3(audio_bytes, mime)

        try:
            response = await self.client.audio.transcriptions.create(
                model=settings.OPENAI_WHISPER_MODEL,
                file=(f"audio.{ext}", audio_mp3, "audio/mpeg"),
                language=lang,
                prompt=prompt,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )
            transcript = response.text.strip()
            normalized = f"{tag} {transcript}"
            return {
                "transcript":        transcript,
                "normalized":        normalized,
                "dialect":           dialect,
                "confidence":        getattr(response, "avg_logprob", 0.0),
                "words":             getattr(response, "words", []),
                "language_detected": getattr(response, "language", lang),
            }
        except openai.APIError as e:
            logger.warning(f"OpenAI Whisper error: {e}. Falling back to Google ASR.")
            return await self._google_asr_fallback(audio_bytes, dialect)

    async def _google_asr_fallback(self, audio_bytes: bytes, dialect: str) -> dict:
        """Google Cloud Speech-to-Text fallback."""
        try:
            from google.cloud import speech
            client = speech.SpeechClient()
            lang = DIALECT_TO_TTS_LANG.get(dialect, "hi-IN")
            audio = speech.RecognitionAudio(content=audio_bytes)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=lang,
                alternative_language_codes=["hi-IN", "en-IN"],
                enable_word_time_offsets=True,
            )
            response = client.recognize(config=config, audio=audio)
            transcript = " ".join(r.alternatives[0].transcript for r in response.results)
            tag = DIALECT_TAGS.get(dialect, "[HINDI]")
            return {
                "transcript":        transcript,
                "normalized":        f"{tag} {transcript}",
                "dialect":           dialect,
                "confidence":        0.7,
                "words":             [],
                "language_detected": dialect,
            }
        except Exception as e:
            logger.error(f"Google ASR fallback also failed: {e}")
            return {
                "transcript":        "",
                "normalized":        "",
                "dialect":           dialect,
                "confidence":        0.0,
                "words":             [],
                "language_detected": dialect,
            }

    @staticmethod
    def _convert_to_mp3(audio_bytes: bytes, mime: str) -> bytes:
        """Convert audio to MP3 using pydub."""
        try:
            fmt = mime.split("/")[-1].replace("webm", "webm").replace("ogg", "ogg")
            segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=fmt)
            buf = io.BytesIO()
            segment.export(buf, format="mp3", bitrate="128k")
            return buf.getvalue()
        except Exception:
            return audio_bytes  # Pass through if conversion fails

    @staticmethod
    def _mime_to_ext(mime: str) -> str:
        mapping = {
            "audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a",
            "audio/mpeg": "mp3",  "audio/wav": "wav", "audio/flac": "flac",
        }
        return mapping.get(mime, "webm")


class TTSEngine:
    """
    Multi-dialect Text-to-Speech Engine.

    Generates natural voice readbacks for non-literate citizens.
    Primary: OpenAI TTS (alloy / shimmer voices)
    Fallback: Google Cloud TTS with WaveNet neural voices
    """

    VOICE_MAP = {
        "hi-IN":  "alloy",    # neutral voice
        "awa-IN": "alloy",
        "bho-IN": "alloy",
        "en-IN":  "shimmer",  # warmer voice for English
    }

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=4))
    async def synthesize(
        self,
        text: str,
        dialect: str = "hi-IN",
        speed: float = 0.9,
    ) -> bytes:
        """
        Synthesize text to speech audio (MP3 bytes).

        Args:
            text:    Text to speak (Hindi / Awadhi / Bhojpuri / English)
            dialect: Dialect code
            speed:   Speaking rate (0.25–4.0, default 0.9 for clarity)

        Returns:
            MP3 audio bytes
        """
        voice = self.VOICE_MAP.get(dialect, "alloy")
        try:
            response = await self.client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3",
            )
            return response.content
        except Exception as e:
            logger.warning(f"OpenAI TTS failed: {e}. Trying Google TTS.")
            return await self._google_tts_fallback(text, dialect)

    async def _google_tts_fallback(self, text: str, dialect: str) -> bytes:
        """Google Cloud TTS WaveNet fallback."""
        try:
            from google.cloud import texttospeech
            client = texttospeech.TextToSpeechClient()
            lang = DIALECT_TO_TTS_LANG.get(dialect, "hi-IN")
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=lang,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
                name=f"{lang}-Wavenet-A",
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.9,
            )
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            return response.audio_content
        except Exception as e:
            logger.error(f"Google TTS fallback failed: {e}")
            return b""

    async def build_complaint_readback(
        self, ticket_data: dict, dialect: str = "hi-IN"
    ) -> Tuple[str, bytes]:
        """
        Build natural-language summary readback for confirmation screen.

        Returns (text, mp3_bytes)
        """
        dept_map = {
            "ROADS_BRIDGES":    {"hi": "सड़क विभाग",    "en": "Roads Department"},
            "WATER_SUPPLY":     {"hi": "जल विभाग",      "en": "Water Department"},
            "ELECTRICITY_POWER":{"hi": "विद्युत विभाग", "en": "Electricity Department"},
            "SANITATION_WASTE": {"hi": "सफाई विभाग",    "en": "Sanitation Department"},
        }
        dept_key    = ticket_data.get("department", "OTHER")
        dept        = dept_map.get(dept_key, {"hi": "संबंधित विभाग", "en": "Relevant Department"})
        transcript  = ticket_data.get("voice_transcript", "")
        location    = ticket_data.get("location", {})
        district    = location.get("district", "")
        sla         = ticket_data.get("predicted_sla_days", 7)
        urgency     = ticket_data.get("urgency_score", 3)

        if dialect in ("hi-IN", "awa-IN", "bho-IN"):
            text = (
                f"आपकी शिकायत दर्ज की जा रही है। "
                f"समस्या: {transcript}। "
                f"विभाग: {dept['hi']}। "
                f"{'जिला: ' + district + '।' if district else ''} "
                f"अनुमानित समाधान: {sla} दिन। "
                f"क्या आप पुष्टि करना चाहते हैं?"
            )
        else:
            text = (
                f"Your complaint is being recorded. "
                f"Issue: {transcript}. "
                f"Department: {dept['en']}. "
                f"{'District: ' + district + '.' if district else ''} "
                f"Estimated resolution: {sla} days. "
                f"Do you confirm?"
            )

        audio_bytes = await self.synthesize(text, dialect)
        return text, audio_bytes
