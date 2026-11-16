"""
backend/app/workers/stream_consumer.py
Stateless Redis Stream Consumer Worker for SamaadSetu Pipeline
Processes stages 1 through 6 asynchronously.
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime

from app.schemas.pipeline import ComplaintIngestRequest, GPSLocation
from app.pipeline.s1_normalize import stage1_normalize
from app.pipeline.s2_extract import stage2_extract
from app.pipeline.s3_classify import stage3_classify
from app.pipeline.s4_score import stage4_score
from app.pipeline.s5_dedupe import stage5_dedupe
from app.pipeline.s6_route import stage6_route

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stream_consumer")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
STREAM_KEY = "stream:complaints:raw"
GROUP_NAME = "samaadsetu_workers"
CONSUMER_NAME = f"worker_{os.getpid()}"


def process_complaint_pipeline(ticket_id: str, payload: dict) -> dict:
    """
    Executes pure stateless pipeline stages:
    Ingest -> Normalize -> Extract -> Classify -> Score -> Dedupe -> Route
    """
    logger.info(f"Processing ticket {ticket_id}...")

    # Reconstruct request
    req = ComplaintIngestRequest(
        idempotency_key=payload.get("idempotency_key", ticket_id),
        language=payload.get("language", "hindi"),
        proxy_mode=payload.get("proxy_mode", "self"),
        raw_text=payload.get("raw_text"),
        audio_base64=payload.get("audio_base64"),
        photo_base64=payload.get("photo_base64"),
        citizen_phone=payload.get("citizen_phone"),
        capture_gps=GPSLocation(**payload["capture_gps"]) if payload.get("capture_gps") else None,
        upload_gps=GPSLocation(**payload["upload_gps"]) if payload.get("upload_gps") else None,
        district=payload.get("district", "Lucknow")
    )

    # 1. Normalize (PII, EXIF, ASR, pHash)
    s1_out = stage1_normalize(ticket_id, req)

    # 2. Extract (JSON Schema & Dialect readback)
    schema, dialect_summary = stage2_extract(s1_out)

    # 3. Classify (10 UP Departments)
    classification = stage3_classify(schema)

    # 4. Score (P1-P5 Urgency, Hazard splitting, SLA)
    scoring = stage4_score(ticket_id, schema, classification)

    # 5. Dedupe & Cluster (500m geohash + 7d window)
    dedupe = stage5_dedupe(ticket_id, schema, classification, req.capture_gps)

    # 6. Route (YAML engine + confidence gate + 1-hop lock)
    routing = stage6_route(ticket_id, classification)

    result = {
        "ticket_id": ticket_id,
        "status": "needs_proof" if routing.is_human_review_required else "verified_assigned",
        "district": req.district,
        "department": routing.final_department,
        "priority": scoring.priority_label,
        "urgency_score": scoring.urgency_level,
        "sla_deadline": scoring.sla_deadline.isoformat(),
        "is_hazard": scoring.hazard_evaluation.is_hazard_detected,
        "hazard_type": scoring.hazard_evaluation.hazard_type,
        "emergency_subticket_id": scoring.emergency_subticket_id,
        "cluster_id": dedupe.master_cluster_id,
        "is_merged": dedupe.is_merged,
        "reassignment_count": 0,
        "reassignment_locked": False,
        "voice_transcript": s1_out.sanitized_transcript,
        "dialect_label": s1_out.dialect_detected,
        "processed_at": datetime.utcnow().isoformat()
    }

    logger.info(f"Ticket {ticket_id} triaged successfully -> Dept: {routing.final_department}, Urgency: {scoring.priority_label}")
    return result


def run_consumer():
    """Main worker loop reading from Redis stream."""
    try:
        import redis
        r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
        logger.info(f"Connected to Redis at {REDIS_URL}")

        # Ensure stream and group exist
        try:
            r.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
            logger.info(f"Created consumer group {GROUP_NAME} on {STREAM_KEY}")
        except Exception:
            pass  # Group already exists

        while True:
            try:
                # Read 5 messages from group
                entries = r.xreadgroup(
                    GROUP_NAME, CONSUMER_NAME,
                    {STREAM_KEY: ">"},
                    count=5, block=3000
                )
                if not entries:
                    continue

                for stream_name, messages in entries:
                    for msg_id, data in messages:
                        ticket_id = data.get("ticket_id", f"GRV-{msg_id}")
                        payload = json.loads(data.get("payload", "{}"))
                        
                        # Process through stages
                        process_complaint_pipeline(ticket_id, payload)
                        
                        # Acknowledge
                        r.xack(STREAM_KEY, GROUP_NAME, msg_id)
            except Exception as e:
                logger.error(f"Error in stream loop: {e}")
                time.sleep(2)
    except Exception as e:
        logger.warning(f"Redis not available ({e}). Worker running in mock polling mode.")
        while True:
            time.sleep(5)


if __name__ == "__main__":
    run_consumer()
