"""
backend/app/pipeline/s3_classify.py
Stage 3: Department Taxonomy Classification & Semantic Matching
Stateless pure function.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List
import yaml

from app.adapters.model_provider import get_model_provider
from app.schemas.pipeline import (
    ClassificationResult,
    ExtractedComplaintSchema,
    TaxonomyCandidate
)

_TAXONOMY_CACHE: Optional[Dict[str, Any]] = None

def load_taxonomy_config() -> Dict[str, Any]:
    global _TAXONOMY_CACHE
    if _TAXONOMY_CACHE is None:
        cfg_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "taxonomy.yaml"
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                _TAXONOMY_CACHE = yaml.safe_load(f)
        else:
            _TAXONOMY_CACHE = {"departments": []}
    return _TAXONOMY_CACHE


def stage3_classify(
    schema: ExtractedComplaintSchema
) -> ClassificationResult:
    """Classifies grievance into 10 UP provincial departments with confidence gating."""
    provider = get_model_provider()
    cfg = load_taxonomy_config()
    depts = cfg.get("departments", [])

    candidates_list: List[Dict[str, Any]] = []
    for d in depts:
        for cat in d.get("categories", []):
            candidates_list.append({
                "department": d["id"],
                "category_code": cat["code"],
                "title": cat["title"],
                "keywords": cat.get("keywords", [])
            })

    result_raw = provider.classify_taxonomy(schema.core_issue, candidates_list)

    dept = result_raw.get("assigned_department", "pwd")
    cat_code = result_raw.get("assigned_category_code", "PWD_POTHOLE")
    conf = float(result_raw.get("confidence_score", 0.88))

    return ClassificationResult(
        assigned_department=dept,
        assigned_category_code=cat_code,
        confidence_score=conf,
        is_confident_route=(conf >= 0.75),
        top_candidates=[
            TaxonomyCandidate(
                department=dept,
                category_code=cat_code,
                confidence_score=conf,
                reasoning=result_raw.get("reasoning", "Semantic keyword and category match.")
            )
        ]
    )
