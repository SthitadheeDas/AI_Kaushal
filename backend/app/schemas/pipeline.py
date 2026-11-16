"""
backend/app/schemas/pipeline.py
Strict Pydantic v2 Input/Output Contracts for All 8 Pipeline Stages
Modeled on Uttar Pradesh's CM Helpline 1076 & Jansunwai
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ==============================================================================
# COMMON PRIMITIVES & ENUMS
# ==============================================================================

DistrictEnum = Literal[
    "Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya",
    "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki",
    "Bareilly", "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli",
    "Chitrakoot", "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad",
    "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur",
    "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat",
    "Kanpur Nagar", "Kasganj", "Kaushambi", "Kheri", "Kushinagar", "Lalitpur", "Lucknow",
    "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad",
    "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Raebareli", "Rampur",
    "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shrawasti",
    "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"
]

DepartmentEnum = Literal[
    "pwd", "jal_nigam", "uppcl", "basic_education", "wcd",
    "health", "panchayati_raj", "nagar_nigam", "revenue", "police"
]

TicketStatusEnum = Literal[
    "received", "needs_proof", "verified_assigned",
    "work_started", "completed", "reopened"
]

LanguageEnum = Literal["hindi", "awadhi", "bhojpuri", "english"]


class GPSLocation(BaseModel):
    lat: float = Field(..., ge=8.0, le=38.0, description="Latitude (India bounds)")
    lng: float = Field(..., ge=68.0, le=98.0, description="Longitude (India bounds)")
    provider: Optional[str] = "network"
    accuracy_m: Optional[float] = None
    is_mock: bool = False
    timestamp: Optional[str] = None


# ==============================================================================
# STAGE 1: INGEST (FastAPI + Idempotency)
# ==============================================================================

class ComplaintIngestRequest(BaseModel):
    idempotency_key: str = Field(..., description="Client-generated unique UUID to prevent double-filing")
    language: LanguageEnum = "hindi"
    proxy_mode: Literal["self", "csc_proxy"] = Field(
        default="self",
        description="Self-filing or CSC Village Operator proxy mode"
    )
    raw_text: Optional[str] = None
    audio_base64: Optional[str] = None
    photo_base64: Optional[str] = None
    slip_document_base64: Optional[str] = None
    citizen_phone: Optional[str] = Field(None, description="Optional raw phone number; masked immediately")
    capture_gps: Optional[GPSLocation] = None
    upload_gps: Optional[GPSLocation] = None
    device_signature: Optional[str] = None
    district: Optional[str] = "Lucknow"


class ComplaintIngestResponse(BaseModel):
    ticket_id: str
    status: str = "received"
    idempotency_key: str
    queued_at: datetime
    stream_message_id: Optional[str] = None
    message: str = "Complaint successfully accepted into intake stream"


# ==============================================================================
# STAGE 2: NORMALISE (ASR, Vision, OCR, EXIF/pHash, PII Masking)
# ==============================================================================

class PIIMaskingResult(BaseModel):
    masked_text: str
    redacted_phone_count: int = 0
    redacted_aadhaar_count: int = 0
    clean_audio_transcript: str


class EXIFAnalysis(BaseModel):
    has_exif: bool = False
    shutter_timestamp: Optional[str] = None
    capture_gps: Optional[GPSLocation] = None
    upload_gps: Optional[GPSLocation] = None
    gps_delta_meters: Optional[float] = None
    is_suspicious_distance: bool = False


class ImageForensicOutput(BaseModel):
    phash: Optional[str] = None
    dhash: Optional[str] = None
    synthetic_ai_prob: float = Field(default=0.03, ge=0.0, le=1.0)
    is_duplicate_detected: bool = False
    matched_prior_ticket_id: Optional[str] = None


class NormalizedMediaOutput(BaseModel):
    ticket_id: str
    sanitized_transcript: str
    dialect_detected: str
    asr_confidence: float = Field(..., ge=0.0, le=1.0)
    low_confidence_audio: bool = False
    ocr_extracted_text: Optional[str] = None
    ocr_reference_numbers: List[str] = Field(default_factory=list)
    exif_analysis: EXIFAnalysis
    image_forensics: ImageForensicOutput
    pii_masking: PIIMaskingResult


# ==============================================================================
# STAGE 3: EXTRACT (Strict JSON Schema + Dialect Summary)
# ==============================================================================

class ExtractedComplaintSchema(BaseModel):
    core_issue: str = Field(..., description="Concise statement of the core problem")
    location_clues: str = Field(..., description="Village, mohalla, landmark mentioned in speech")
    alleged_department: Optional[DepartmentEnum] = None
    is_recurring: bool = False
    estimated_affected_people: Optional[str] = "individual"


class DialectAudioSummary(BaseModel):
    hindi_readback: str
    dialect_readback: str
    estimated_days: int = 5
    summary_sentence: str


# ==============================================================================
# STAGE 4: CLASSIFY (pgvector Taxonomy Retrieval + LLM Judge)
# ==============================================================================

class TaxonomyCandidate(BaseModel):
    department: DepartmentEnum
    category_code: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str


class ClassificationResult(BaseModel):
    assigned_department: DepartmentEnum
    assigned_category_code: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    is_confident_route: bool
    top_candidates: List[TaxonomyCandidate] = Field(default_factory=list)


# ==============================================================================
# STAGE 5: SCORE (Urgency 1-5 + Hazard Split + SLA ETA)
# ==============================================================================

class HazardEvaluationResult(BaseModel):
    is_hazard_detected: bool = False
    hazard_type: Optional[str] = None
    hazard_alert_reason: Optional[str] = None
    requires_p1_subticket: bool = False


class UrgencyScoringResult(BaseModel):
    urgency_level: int = Field(..., ge=1, le=5) # 1=Routine, 5=Life Safety
    priority_label: Literal["P1", "P2", "P3", "P4", "P5"]
    calculated_sla_hours: int
    sla_deadline: datetime
    hazard_evaluation: HazardEvaluationResult
    emergency_subticket_id: Optional[str] = None


# ==============================================================================
# STAGE 6: DEDUP & CLUSTER (500m Geohash + 7d Temporal + Cosine Sim)
# ==============================================================================

class ClusterMatch(BaseModel):
    is_merged: bool = False
    master_cluster_id: str
    cluster_size: int = 1
    similarity_score: float = 0.0
    matched_root_ticket_id: Optional[str] = None


# ==============================================================================
# STAGE 7: ROUTE (Config-Driven YAML Rules + Confidence Gate)
# ==============================================================================

class RoutingDecision(BaseModel):
    ticket_id: str
    final_department: DepartmentEnum
    nodal_officer_rank: str
    is_human_review_required: bool = False
    review_reason: Optional[str] = None
    reassignment_count: int = 0
    reassignment_locked: bool = False
    routed_at: datetime


class ReassignmentRequest(BaseModel):
    ticket_id: str
    from_department: DepartmentEnum
    target_department: DepartmentEnum
    officer_id: str
    justification: str = Field(..., min_length=10, description="Mandatory official justification (min 10 chars)")


class ReassignmentResponse(BaseModel):
    success: bool
    ticket_id: str
    new_department: DepartmentEnum
    reassignment_locked: bool
    is_dm_escalated: bool = False
    message: str


# ==============================================================================
# STAGE 8: INSIGHT & RESOLUTION VERIFICATION
# ==============================================================================

class ResolutionVerificationRequest(BaseModel):
    ticket_id: str
    officer_id: str
    after_photo_base64: str
    resolution_notes: str


class ResolutionVerificationResponse(BaseModel):
    ticket_id: str
    verified: bool
    landmark_match_score: float = Field(..., ge=0.0, le=1.0)
    defect_resolution_score: float = Field(..., ge=0.0, le=1.0)
    ssim_score: float = Field(..., ge=0.0, le=1.0)
    closure_permitted: bool
    message: str


class RollupAnalyticsResponse(BaseModel):
    total_intake: int
    pending_audits: int
    active_clusters: int
    sla_breaches: int
    resolved_count: int
    department_distribution: Dict[str, int]
    district_top_spikes: List[Dict[str, Any]]
    active_hazard_count: int
