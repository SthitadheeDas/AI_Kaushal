"""
backend/app/pipeline/s6_route.py
Stage 6: Config-Driven Routing Engine & 1-Hop Reassignment Lock
Stateless pure function.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import yaml

from app.schemas.pipeline import (
    ClassificationResult,
    DepartmentEnum,
    ReassignmentRequest,
    ReassignmentResponse,
    RoutingDecision
)

_ROUTING_RULES_CACHE: Optional[Dict[str, Any]] = None

def load_routing_rules() -> Dict[str, Any]:
    global _ROUTING_RULES_CACHE
    if _ROUTING_RULES_CACHE is None:
        cfg_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "routing_rules.yaml"
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                _ROUTING_RULES_CACHE = yaml.safe_load(f)
        else:
            _ROUTING_RULES_CACHE = {}
    return _ROUTING_RULES_CACHE


def stage6_route(
    ticket_id: str,
    classification: ClassificationResult
) -> RoutingDecision:
    """
    Applies config-driven routing rules and enforces confidence gating (<0.75 -> HUMAN_REVIEW).
    """
    cfg = load_routing_rules()
    threshold = cfg.get("routing_engine", {}).get("confidence_gate_threshold", 0.75)

    is_low_conf = classification.confidence_score < threshold

    nodal_ranks = {
        "pwd": "Executive Engineer (PWD)",
        "jal_nigam": "General Manager (Jal Sansthan)",
        "uppcl": "Sub-Divisional Officer (UPPCL)",
        "basic_education": "Basic Shiksha Adhikari (BSA)",
        "wcd": "District Programme Officer (DPO)",
        "health": "Chief Medical Officer (CMO)",
        "panchayati_raj": "District Panchayat Raj Officer (DPRO)",
        "nagar_nigam": "Municipal Commissioner / EO",
        "revenue": "Sub-Divisional Magistrate (SDM)",
        "police": "Circle Officer (Police)"
    }

    rank = nodal_ranks.get(classification.assigned_department, "District Nodal Officer")

    return RoutingDecision(
        ticket_id=ticket_id,
        final_department=classification.assigned_department,
        nodal_officer_rank=rank,
        is_human_review_required=is_low_conf,
        review_reason="Confidence score below threshold (0.75)" if is_low_conf else None,
        reassignment_count=0,
        reassignment_locked=False,
        routed_at=datetime.utcnow()
    )


def handle_reassignment_lock(
    current_reassignment_count: int,
    request: ReassignmentRequest
) -> ReassignmentResponse:
    """
    Enforces One-Hop Reassignment Lock ("Hot Potato" Breaker).
    A departmental officer can reassign at most ONCE with justification (>= 10 chars).
    Any 2nd attempt locks ticket and auto-escalates to the District Magistrate (DM) / CDO.
    """
    if len(request.justification.strip()) < 10:
        return ReassignmentResponse(
            success=False,
            ticket_id=request.ticket_id,
            new_department=request.from_department,
            reassignment_locked=(current_reassignment_count >= 1),
            is_dm_escalated=False,
            message="Reassignment rejected: Justification note must be at least 10 characters."
        )

    # Check 1-hop limit
    if current_reassignment_count >= 1:
        # HOT POTATO BREAKER TRIGGERED -> ESCALATE TO DM
        return ReassignmentResponse(
            success=False,
            ticket_id=request.ticket_id,
            new_department=request.from_department,
            reassignment_locked=True,
            is_dm_escalated=True,
            message="🚨 ONE-HOP REASSIGNMENT LOCKED: Ticket has already been reassigned once. Auto-escalated to District Magistrate (DM) for binding order."
        )

    # First reassignment permitted -> Now locked for further transfers
    return ReassignmentResponse(
        success=True,
        ticket_id=request.ticket_id,
        new_department=request.target_department,
        reassignment_locked=True,
        is_dm_escalated=False,
        message=f"Reassignment approved: Transferred to {request.target_department}. Reassignment allowance 1/1 used (Now Locked)."
    )
