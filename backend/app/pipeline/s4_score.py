"""
backend/app/pipeline/s4_score.py
Stage 4: Urgency Scoring (P1-P5), Life-Safety Hazard Splitting & SLA Computation
Stateless pure function.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from app.adapters.model_provider import get_model_provider
from app.schemas.pipeline import (
    ClassificationResult,
    ExtractedComplaintSchema,
    HazardEvaluationResult,
    UrgencyScoringResult
)


def stage4_score(
    parent_ticket_id: str,
    schema: ExtractedComplaintSchema,
    classification: ClassificationResult
) -> UrgencyScoringResult:
    """
    Evaluates urgency, checks life-safety hazards, computes SLA,
    and spawns an autonomous P1 Emergency Sub-Ticket if critical hazard detected.
    """
    provider = get_model_provider()

    # 1. Evaluate Life-Safety Hazard
    hazard_raw = provider.evaluate_hazard(schema.core_issue)
    is_hazard = bool(hazard_raw.get("is_hazard_detected", False))

    hazard_eval = HazardEvaluationResult(
        is_hazard_detected=is_hazard,
        hazard_type=hazard_raw.get("hazard_type"),
        hazard_alert_reason=hazard_raw.get("hazard_alert_reason"),
        requires_p1_subticket=is_hazard
    )

    emergency_id = None
    if is_hazard:
        urgency = 5
        priority = "P1"
        sla_hours = 4 # 4-hour urgent emergency SLA
        emergency_id = f"EMG-{parent_ticket_id.replace('GRV-', '')}"
    else:
        # Standard scoring based on department & category default
        urgency_map = {
            "uppcl": 4,
            "jal_nigam": 3,
            "health": 4,
            "pwd": 3,
            "nagar_nigam": 3,
            "police": 3,
            "basic_education": 3,
            "revenue": 2,
            "panchayati_raj": 2,
            "wcd": 2
        }
        urgency = urgency_map.get(classification.assigned_department, 3)
        priority_labels = {1: "P5", 2: "P4", 3: "P3", 4: "P2", 5: "P1"}
        priority = priority_labels[urgency]
        sla_hours = (6 - urgency) * 24 # e.g. Urgency 3 -> 72h (3 days)

    now = datetime.utcnow()
    deadline = now + timedelta(hours=sla_hours)

    return UrgencyScoringResult(
        urgency_level=urgency,
        priority_label=priority,
        calculated_sla_hours=sla_hours,
        sla_deadline=deadline,
        hazard_evaluation=hazard_eval,
        emergency_subticket_id=emergency_id
    )
