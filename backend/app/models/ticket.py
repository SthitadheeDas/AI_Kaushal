"""
app/models/ticket.py
Pydantic + SQLAlchemy ORM models for GrievanceTicket
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Double, Enum as SAEnum,
    ForeignKey, Index, Integer, SmallInteger, String, Text, func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector


# ── Enumerations ────────────────────────────────────────────────────────────

class TicketStatus(str, enum.Enum):
    SUBMITTED                   = "SUBMITTED"
    PROOF_REQUESTED             = "PROOF_REQUESTED"
    VERIFIED_ASSIGNED           = "VERIFIED_ASSIGNED"
    IN_PROGRESS                 = "IN_PROGRESS"
    RESOLVED_PENDING_CITIZEN    = "RESOLVED_PENDING_CITIZEN"
    CLOSED                      = "CLOSED"
    REOPENED                    = "REOPENED"
    DUPLICATE_MERGED            = "DUPLICATE_MERGED"


class ProofTier(str, enum.Enum):
    UNVERIFIED              = "UNVERIFIED"
    SELF_REPORTED           = "SELF_REPORTED"
    PHOTO_DOC_VERIFIED      = "PHOTO_DOC_VERIFIED"
    COMMUNITY_DOC_VERIFIED  = "COMMUNITY_DOC_VERIFIED"
    OFFICER_VERIFIED        = "OFFICER_VERIFIED"


class GeoSource(str, enum.Enum):
    GPS_DEVICE          = "GPS_DEVICE"
    EXIF_METADATA       = "EXIF_METADATA"
    USER_ENTERED        = "USER_ENTERED"
    REVERSE_GEOCODED    = "REVERSE_GEOCODED"
    DEFAULT_DISTRICT    = "DEFAULT_DISTRICT"


class AuditStatus(str, enum.Enum):
    PENDING     = "PENDING"
    APPROVED    = "APPROVED"
    REJECTED    = "REJECTED"
    ESCALATED   = "ESCALATED"


class DialectCode(str, enum.Enum):
    HINDI       = "hi-IN"
    AWADHI      = "awa-IN"
    BHOJPURI    = "bho-IN"
    ENGLISH     = "en-IN"


class DepartmentCode(str, enum.Enum):
    ROADS_BRIDGES       = "ROADS_BRIDGES"
    WATER_SUPPLY        = "WATER_SUPPLY"
    ELECTRICITY_POWER   = "ELECTRICITY_POWER"
    SANITATION_WASTE    = "SANITATION_WASTE"
    HEALTH_MEDICAL      = "HEALTH_MEDICAL"
    EDUCATION           = "EDUCATION"
    REVENUE_LAND        = "REVENUE_LAND"
    POLICE_LAW          = "POLICE_LAW"
    HOUSING_URBAN       = "HOUSING_URBAN"
    AGRICULTURE         = "AGRICULTURE"
    SOCIAL_WELFARE      = "SOCIAL_WELFARE"
    OTHER               = "OTHER"


# ── Pydantic Sub-Models ─────────────────────────────────────────────────────

class CitizenInfo(BaseModel):
    phone_masked:           Optional[str]       = None
    preferred_dialect:      DialectCode         = DialectCode.HINDI
    voice_guidance_enabled: bool                = True


class LocationInfo(BaseModel):
    district:           Optional[str]   = None
    block_tehsil:       Optional[str]   = None
    village_ward:       Optional[str]   = None
    lat:                Optional[float] = None
    lng:                Optional[float] = None
    geo_source:         GeoSource       = GeoSource.GPS_DEVICE
    address_normalized: Optional[str]   = None


class MediaProof(BaseModel):
    url:            str
    media_type:     str         # 'image' | 'video' | 'audio' | 'document'
    file_size_kb:   Optional[int] = None
    mime_type:      Optional[str] = None
    phash:          Optional[str] = None
    dhash:          Optional[str] = None
    exif_lat:       Optional[float] = None
    exif_lng:       Optional[float] = None
    exif_timestamp: Optional[datetime] = None
    caption:        Optional[str] = None
    relevance_score: Optional[float] = None
    recycled_flag:  bool = False


class MultiModalInputs(BaseModel):
    raw_text:       Optional[str]       = None
    voice_notes:    List[MediaProof]    = Field(default_factory=list)
    media_proofs:   List[MediaProof]    = Field(default_factory=list)
    documents:      List[MediaProof]    = Field(default_factory=list)
    voice_transcript: Optional[str]     = None
    ocr_extracted:  dict                = Field(default_factory=dict)
    image_captions: List[str]           = Field(default_factory=list)


class AITriage(BaseModel):
    department:         DepartmentCode  = DepartmentCode.OTHER
    sub_category:       Optional[str]   = None
    urgency_score:      int             = Field(default=3, ge=1, le=5)
    predicted_sla_days: Optional[int]   = None
    cluster_id:         Optional[str]   = None
    corroboration_count: int            = 0
    dedup_ticket_ref:   Optional[str]   = None


class ProofVerification(BaseModel):
    tier:               ProofTier   = ProofTier.UNVERIFIED
    officer_audit_status: AuditStatus = AuditStatus.PENDING
    officer_id:         Optional[str] = None
    officer_notes:      Optional[str] = None
    image_relevance_score: Optional[float] = None
    recycled_image_flag: bool        = False
    gps_drift_meters:   Optional[float] = None


class ResolutionLoop(BaseModel):
    after_photo_url:    Optional[str]   = None
    after_gps_lat:      Optional[float] = None
    after_gps_lng:      Optional[float] = None
    after_gps_match:    Optional[bool]  = None
    citizen_feedback:   Optional[str]   = None   # 'satisfied' | 'reopen'
    reopen_reason:      Optional[str]   = None


# ── Canonical GrievanceTicket Pydantic Model ────────────────────────────────

class GrievanceTicket(BaseModel):
    """Full canonical shared schema – used by API responses and state sync."""
    ticket_id:          str
    uuid:               Optional[UUID]      = None
    status:             TicketStatus        = TicketStatus.SUBMITTED
    created_at:         datetime            = Field(default_factory=datetime.utcnow)
    updated_at:         datetime            = Field(default_factory=datetime.utcnow)
    submitted_at:       datetime            = Field(default_factory=datetime.utcnow)
    resolved_at:        Optional[datetime]  = None

    citizen:            CitizenInfo         = Field(default_factory=CitizenInfo)
    location:           LocationInfo        = Field(default_factory=LocationInfo)
    multi_modal_inputs: MultiModalInputs    = Field(default_factory=MultiModalInputs)
    ai_triage:          AITriage            = Field(default_factory=AITriage)
    proof_verification: ProofVerification   = Field(default_factory=ProofVerification)
    resolution_loop:    ResolutionLoop      = Field(default_factory=ResolutionLoop)

    class Config:
        from_attributes = True


# ── Request/Response Schemas ─────────────────────────────────────────────────

class SubmitTicketRequest(BaseModel):
    """Payload sent by Citizen Portal on complaint submission."""
    voice_transcript:   str
    preferred_dialect:  DialectCode         = DialectCode.HINDI
    voice_guidance_enabled: bool            = True
    citizen_phone_masked: Optional[str]     = None
    lat:                Optional[float]     = None
    lng:                Optional[float]     = None
    geo_source:         GeoSource           = GeoSource.GPS_DEVICE
    # media passed as multipart/form-data files alongside this JSON body


class UpdateStatusRequest(BaseModel):
    """Officer action payload."""
    new_status:         TicketStatus
    officer_id:         str
    officer_notes:      Optional[str]       = None
    after_photo_url:    Optional[str]       = None
    after_gps_lat:      Optional[float]     = None
    after_gps_lng:      Optional[float]     = None
    predicted_sla_days: Optional[int]       = None


class CitizenFeedbackRequest(BaseModel):
    """Citizen thumbs-up / thumbs-down after resolution."""
    ticket_id:          str
    feedback:           str                 # 'satisfied' | 'reopen'
    reopen_reason:      Optional[str]       = None


class CorroborationRequest(BaseModel):
    """'Me Too' tap by another citizen."""
    ticket_id:          str
    citizen_phone_masked: Optional[str]     = None
    lat:                Optional[float]     = None
    lng:                Optional[float]     = None


class TicketListResponse(BaseModel):
    items:  List[GrievanceTicket]
    total:  int
    page:   int
    size:   int


class TriageResult(BaseModel):
    """Internal AI triage output."""
    department:         DepartmentCode
    sub_category:       str
    urgency_score:      int
    predicted_sla_days: int
    entities:           dict            = Field(default_factory=dict)
    confidence:         float           = 0.0


class RealtimeEvent(BaseModel):
    """SSE / WebSocket push payload."""
    event_id:   str
    ticket_id:  Optional[str]  = None
    audience:   str            # 'citizen' | 'officer' | 'all'
    event_type: str
    payload:    dict           = Field(default_factory=dict)
    created_at: datetime       = Field(default_factory=datetime.utcnow)
