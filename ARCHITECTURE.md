# SamaadSetu System Architecture & Distributed Engineering Design

This document details the architectural specifications, state machines, vector indices, and queue semantics for **SamaadSetu: Universal Citizen Intake, Triage & Routing Engine**.

---

## 1. Architectural Philosophy: Decoupled & Resilient

The platform is designed to withstand real-world conditions across 75 Uttar Pradesh districts:
- **Zero Data Loss on 2G Networks:** Offline-first PWA with client-side progressive WebP/JPEG compression ($<150\text{ KB}$) and IndexedDB queuing.
- **Micro-batching & Asynchronous Decoupling:** Ingestion endpoints (`/v1/complaints`) perform zero heavy processing synchronously. They validate schemas, assign a UUIDv4 idempotency token, and append payloads to Redis Streams (`stream:complaints:raw`) in $<10\text{ ms}$.
- **Pure Stateless Workers:** Python worker pods pull from consumer group `triage_workers`, execute pure mathematical & model pipeline stages, update PostgreSQL, and acknowledge (`XACK`) messages.

---

## 2. Distributed Queue & Stream Lifecycle

```text
[Citizen Ingestion]
        │
        ▼ POST /v1/complaints
┌───────────────────────────────┐
│ FastAPI Gateway               │ ──> Generates Ticket UUID
│ (Validates Input Schema)       │ ──> Writes idempotency key in Redis (TTL 24h)
└───────────────────────────────┘
        │
        ▼ XADD stream:complaints:raw
┌────────────────────────────────────────────────────────┐
│ Redis Streams (stream:complaints:raw)                  │
│ Consumer Group: 'samaadsetu_workers'                   │
└────────────────────────────────────────────────────────┘
        │
        ▼ XREADGROUP (Prefetch: 10, Block: 2000ms)
┌────────────────────────────────────────────────────────┐
│ Stateless Pipeline Worker                              │
│ Stage 1: PII Mask + Normalise (EXIF / pHash / Gemini)  │
│ Stage 2: Extract (Strict JSON Schema + Dialect Read)   │
│ Stage 3: Classify (pgvector Cosine + LLM Judge)        │
│ Stage 4: Score (Urgency 1-5 + Hazard Split)            │
│ Stage 5: Dedupe & Cluster (500m Geohash + 7d Cosine)   │
│ Stage 6: Route (YAML Rules + Confidence Gate)          │
└────────────────────────────────────────────────────────┘
        │
   ┌────┴─────────────────────────────┐
   ▼ Success                          ▼ Failed (3 Retries)
┌────────────────────────┐   ┌──────────────────────────────┐
│ PostgreSQL 16 + vector │   │ Dead Letter Queue            │
│ (ACID Commit + Index)  │   │ XADD stream:complaints:dead  │
│ XACK stream:complaints │   └──────────────────────────────┘
└────────────────────────┘
```

---

## 3. Database Schema & Vector Indexing Design

### Primary Tables in PostgreSQL 16:
1. `departments` & `categories`: Hierarchical departmental taxonomies and SLAs.
2. `tickets`: Central grievance ledger tracking lifecycle status, assigned department, district, urgency, and citizen feedback.
3. `ticket_proofs`: Cryptographically signed captures with EXIF GPS, network upload GPS, pHash, dHash, and synthetic AI probabilities.
4. `clusters`: Master deduplicated clusters grouping corroborated complaints within a $500\text{ m}$ geohash bucket.
5. `reassignment_audit`: Immutable audit log recording departmental transfers, officer justifications, and DM escalations.

### Vector Search Indexing (`pgvector`):
- Embeddings are generated using Google's `text-embedding-004` (768-dimensional float vectors).
- **HNSW Index (Hierarchical Navigable Small World):**
  ```sql
  CREATE INDEX idx_tickets_embedding_hnsw 
  ON tickets 
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
  ```
- **Spatial Geohash Partitioning:**
  A spatial index on `geohash_7` ensures vector comparisons are only executed against tickets within the same geographical grid cell ($~150\text{ m} \times 150\text{ m}$):
  ```sql
  SELECT ticket_id, cluster_id, 1 - (embedding <=> :query_vec) AS similarity
  FROM tickets
  WHERE geohash_7 = :target_geohash
    AND created_at >= NOW() - INTERVAL '7 days'
    AND status != 'completed'
  ORDER BY similarity DESC
  LIMIT 5;
  ```

---

## 4. State Machines

### A. Ticket Lifecycle State Machine
```text
[RECEIVED]
   │
   ├── (Confidence < 0.75) ──────────────────────────► [NEEDS_PROOF / HUMAN_REVIEW]
   │                                                             │
   │                                                     (Officer Clarified)
   ▼                                                             ▼
[VERIFIED_ASSIGNED] ◄────────────────────────────────────────────┘
   │
   ├── (Field Officer Dispatched)
   ▼
[WORK_STARTED]
   │
   ├── (Officer Uploads Geo-Tagged "After" Photo)
   │   ├── Landmark Alignment fails (< 60%) ──────────► [BLOCKED / DM_ALERT]
   │   └── Landmark Match confirmed (>= 60%)
   ▼
[COMPLETED]
   │
   ├── Citizen Thumbs-Up (👍) ────────────────────────► [ARCHIVED_SATISFIED]
   └── Citizen Thumbs-Down (👎) ──────────────────────► [REOPENED_DM_ESCALATED]
```

### B. One-Hop Reassignment State Machine ("Hot Potato" Breaker)
```text
Ticket at Department A (reassignment_count = 0)
   │
   ▼ Officer submits transfer with justification (>= 10 chars)
Ticket transferred to Department B (reassignment_count = 1, reassignment_locked = true)
   │
   ▼ Officer at Department B attempts second transfer
[STATE-MACHINE REJECT: LOCKED]
   │
   ▼ Auto-Escalate
[DISTRICT_MAGISTRATE_BINDING_QUEUE]
(Binding Order Issued by DM / Chief Development Officer)
```
