"""
backend/app/pipeline/s2_extract.py
Stage 2: Structured Complaint Details & Dialect Readback Extraction
Stateless pure function.
"""
from __future__ import annotations

from typing import Tuple
from app.adapters.model_provider import get_model_provider
from app.schemas.pipeline import (
    DialectAudioSummary,
    ExtractedComplaintSchema,
    NormalizedMediaOutput
)


def stage2_extract(
    normalized: NormalizedMediaOutput
) -> Tuple[ExtractedComplaintSchema, DialectAudioSummary]:
    """
    Extracts structured schema (core_issue, location_clues, alleged_department)
    and generates spoken audio summary readbacks for the citizen.
    """
    provider = get_model_provider()

    raw_data = provider.extract_structured_json(
        sanitized_transcript=normalized.sanitized_transcript,
        ocr_text=normalized.ocr_extracted_text
    )

    schema = ExtractedComplaintSchema(
        core_issue=raw_data.get("core_issue", normalized.sanitized_transcript[:100]),
        location_clues=raw_data.get("location_clues", "Ward / Village, UP"),
        alleged_department=raw_data.get("alleged_department", "pwd"),
        is_recurring=bool(raw_data.get("is_recurring", False)),
        estimated_affected_people=raw_data.get("estimated_affected_people", "community")
    )

    summary = DialectAudioSummary(
        hindi_readback=raw_data.get("hindi_readback", "आपकी शिकायत दर्ज कर ली गई है।"),
        dialect_readback=raw_data.get("dialect_readback", "आपकी फरियाद सहेज लीन गई है।"),
        estimated_days=int(raw_data.get("estimated_days", 5)),
        summary_sentence=schema.core_issue
    )

    return schema, summary
