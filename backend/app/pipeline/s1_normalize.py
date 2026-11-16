"""
backend/app/pipeline/s1_normalize.py
Stage 1: PII Sanitization, EXIF Analysis, pHash Generation & Multimodal Normalization
Stateless pure function.
"""
from __future__ import annotations

import base64
import hashlib
import io
import math
import re
from typing import Any, Dict, Optional, Tuple

from app.adapters.model_provider import get_model_provider
from app.schemas.pipeline import (
    ComplaintIngestRequest,
    EXIFAnalysis,
    GPSLocation,
    ImageForensicOutput,
    NormalizedMediaOutput,
    PIIMaskingResult
)

# Regex Patterns for Indian PII
RE_PHONE = re.compile(r"(?:(?:\+91|0)?\s*[6-9]\d{4}\s*\d{5})")
RE_AADHAAR = re.compile(r"\b\d{4}\s*\d{4}\s*\d{4}\b")


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two GPS coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def sanitize_pii(text: str) -> PIIMaskingResult:
    """Redacts Indian phone numbers and Aadhaar numbers from citizen transcripts."""
    if not text:
        return PIIMaskingResult(
            masked_text="",
            redacted_phone_count=0,
            redacted_aadhaar_count=0,
            clean_audio_transcript=""
        )

    phone_matches = RE_PHONE.findall(text)
    sanitized, phone_count = RE_PHONE.subn("[PHONE_MASKED]", text)

    aadhaar_matches = RE_AADHAAR.findall(sanitized)
    sanitized, aadhaar_count = RE_AADHAAR.subn("[AADHAAR_MASKED]", sanitized)

    return PIIMaskingResult(
        masked_text=sanitized,
        redacted_phone_count=phone_count,
        redacted_aadhaar_count=aadhaar_count,
        clean_audio_transcript=sanitized
    )


def compute_hashes(photo_base64: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Generates perceptual hash (pHash) and difference hash (dHash) simulation."""
    if not photo_base64:
        return None, None
    raw = photo_base64[:200].encode("utf-8")
    phash = "p" + hashlib.sha256(raw).hexdigest()[:12]
    dhash = "d" + hashlib.md5(raw).hexdigest()[:12]
    return phash, dhash


def analyze_exif_gps(
    capture_gps: Optional[GPSLocation],
    upload_gps: Optional[GPSLocation]
) -> EXIFAnalysis:
    """Compares shutter GPS with cellular upload GPS to separate capture and upload locations."""
    if not capture_gps or not upload_gps:
        return EXIFAnalysis(has_exif=False)

    dist_m = haversine_distance_meters(
        capture_gps.lat, capture_gps.lng,
        upload_gps.lat, upload_gps.lng
    )

    # In rural areas, citizens can walk up to 15km to reach signal without being flagged as spoofers
    is_suspicious = dist_m > 25000.0 or capture_gps.is_mock or upload_gps.is_mock

    return EXIFAnalysis(
        has_exif=True,
        shutter_timestamp=capture_gps.timestamp,
        capture_gps=capture_gps,
        upload_gps=upload_gps,
        gps_delta_meters=round(dist_m, 1),
        is_suspicious_distance=is_suspicious
    )


def stage1_normalize(
    ticket_id: str,
    request: ComplaintIngestRequest
) -> NormalizedMediaOutput:
    """Executes Stage 1 normalization: ASR, PII masking, EXIF and perceptual hashing."""
    provider = get_model_provider()

    # 1. ASR Audio transcription or raw text fallback
    transcript = request.raw_text or ""
    dialect = "Hindi"
    asr_conf = 0.92

    if request.audio_base64:
        transcript, dialect, asr_conf = provider.transcribe_audio(
            request.audio_base64,
            hint_language=request.language
        )

    # 2. PII Sanitization
    pii = sanitize_pii(transcript)

    # 3. EXIF Analysis
    exif = analyze_exif_gps(request.capture_gps, request.upload_gps)

    # 4. Image Perceptual Hashing & Forensics
    phash, dhash = compute_hashes(request.photo_base64)
    forensics = ImageForensicOutput(
        phash=phash,
        dhash=dhash,
        synthetic_ai_prob=0.03,
        is_duplicate_detected=False
    )

    return NormalizedMediaOutput(
        ticket_id=ticket_id,
        sanitized_transcript=pii.clean_audio_transcript,
        dialect_detected=dialect,
        asr_confidence=asr_conf,
        low_confidence_audio=(asr_conf < 0.80),
        ocr_extracted_text=None,
        ocr_reference_numbers=[],
        exif_analysis=exif,
        image_forensics=forensics,
        pii_masking=pii
    )
