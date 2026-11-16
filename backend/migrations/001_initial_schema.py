"""
SamaadSetu Grievance Portal – PostgreSQL + PostGIS Schema
Migration: 001_initial_schema
Run: alembic upgrade head
"""

# ── migrations/001_initial_schema.sql ──────────────────────────────────────

UPGRADE_SQL = """
-- ============================================================
-- EXTENSIONS
-- ============================================================
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- trigram search on transcript

-- ============================================================
-- ENUM TYPES
-- ============================================================
CREATE TYPE ticket_status AS ENUM (
    'SUBMITTED',
    'PROOF_REQUESTED',
    'VERIFIED_ASSIGNED',
    'IN_PROGRESS',
    'RESOLVED_PENDING_CITIZEN',
    'CLOSED',
    'REOPENED',
    'DUPLICATE_MERGED'
);

CREATE TYPE proof_tier AS ENUM (
    'UNVERIFIED',
    'SELF_REPORTED',
    'PHOTO_DOC_VERIFIED',
    'COMMUNITY_DOC_VERIFIED',
    'OFFICER_VERIFIED'
);

CREATE TYPE geo_source AS ENUM (
    'GPS_DEVICE',
    'EXIF_METADATA',
    'USER_ENTERED',
    'REVERSE_GEOCODED',
    'DEFAULT_DISTRICT'
);

CREATE TYPE audit_status AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'ESCALATED'
);

CREATE TYPE dialect_code AS ENUM (
    'hi-IN',   -- Hindi
    'awa-IN',  -- Awadhi
    'bho-IN',  -- Bhojpuri
    'en-IN'    -- English (India)
);

CREATE TYPE department_code AS ENUM (
    'ROADS_BRIDGES',
    'WATER_SUPPLY',
    'ELECTRICITY_POWER',
    'SANITATION_WASTE',
    'HEALTH_MEDICAL',
    'EDUCATION',
    'REVENUE_LAND',
    'POLICE_LAW',
    'HOUSING_URBAN',
    'AGRICULTURE',
    'SOCIAL_WELFARE',
    'OTHER'
);

-- ============================================================
-- CORE TICKET TABLE
-- ============================================================
CREATE TABLE grievance_tickets (
    -- Identity
    ticket_id           VARCHAR(20)     PRIMARY KEY,   -- GRV-2024-XXXX
    uuid                UUID            NOT NULL DEFAULT uuid_generate_v4(),
    status              ticket_status   NOT NULL DEFAULT 'SUBMITTED',
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    submitted_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    resolved_at         TIMESTAMPTZ,

    -- Citizen Info (privacy-safe)
    citizen_phone_masked    VARCHAR(14),               -- +91-XXXXXXX890
    preferred_dialect       dialect_code    NOT NULL DEFAULT 'hi-IN',
    voice_guidance_enabled  BOOLEAN         NOT NULL DEFAULT TRUE,
    citizen_feedback        VARCHAR(20),               -- 'satisfied' | 'reopen'
    reopen_reason           TEXT,

    -- Location (PostGIS)
    district            VARCHAR(100),
    block_tehsil        VARCHAR(100),
    village_ward        VARCHAR(100),
    lat                 DOUBLE PRECISION,
    lng                 DOUBLE PRECISION,
    geom                GEOMETRY(POINT, 4326),         -- PostGIS spatial index
    geo_source          geo_source      NOT NULL DEFAULT 'GPS_DEVICE',
    address_normalized  TEXT,

    -- Raw Multi-Modal Inputs
    raw_text            TEXT,
    voice_note_urls     JSONB           NOT NULL DEFAULT '[]'::JSONB,
    media_proof_urls    JSONB           NOT NULL DEFAULT '[]'::JSONB,
    document_urls       JSONB           NOT NULL DEFAULT '[]'::JSONB,

    -- AI-Extracted / Transcribed
    voice_transcript    TEXT,
    ocr_extracted_fields JSONB          DEFAULT '{}'::JSONB,
    image_captions      JSONB           NOT NULL DEFAULT '[]'::JSONB,

    -- AI Triage Output
    department          department_code NOT NULL DEFAULT 'OTHER',
    sub_category        VARCHAR(100),
    urgency_score       SMALLINT        CHECK (urgency_score BETWEEN 1 AND 5),
    predicted_sla_days  SMALLINT,
    cluster_id          VARCHAR(50),                   -- Qdrant cluster ID
    corroboration_count INTEGER         NOT NULL DEFAULT 0,
    dedup_ticket_ref    VARCHAR(20),                   -- → parent if DUPLICATE_MERGED

    -- Vision Forensics
    phash_fingerprints  JSONB           NOT NULL DEFAULT '[]'::JSONB,
    exif_gps_lat        DOUBLE PRECISION,
    exif_gps_lng        DOUBLE PRECISION,
    exif_timestamp      TIMESTAMPTZ,
    gps_drift_meters    DOUBLE PRECISION,
    image_relevance_score FLOAT,
    recycled_image_flag BOOLEAN         NOT NULL DEFAULT FALSE,

    -- Proof Verification
    proof_tier          proof_tier      NOT NULL DEFAULT 'UNVERIFIED',
    officer_audit_status audit_status   DEFAULT 'PENDING',
    officer_id          VARCHAR(50),
    officer_notes       TEXT,
    assigned_at         TIMESTAMPTZ,

    -- Resolution Loop
    before_photo_url    TEXT,
    after_photo_url     TEXT,
    after_gps_lat       DOUBLE PRECISION,
    after_gps_lng       DOUBLE PRECISION,
    after_gps_match     BOOLEAN,
    officer_close_at    TIMESTAMPTZ,

    -- Embedding (pgvector)
    embedding           VECTOR(1024),

    -- Audit / Soft-delete
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          TIMESTAMPTZ,
    version             INTEGER         NOT NULL DEFAULT 1
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_tickets_status        ON grievance_tickets(status);
CREATE INDEX idx_tickets_department    ON grievance_tickets(department);
CREATE INDEX idx_tickets_district      ON grievance_tickets(district);
CREATE INDEX idx_tickets_urgency       ON grievance_tickets(urgency_score DESC);
CREATE INDEX idx_tickets_created       ON grievance_tickets(created_at DESC);
CREATE INDEX idx_tickets_updated       ON grievance_tickets(updated_at DESC);
CREATE INDEX idx_tickets_cluster       ON grievance_tickets(cluster_id) WHERE cluster_id IS NOT NULL;
CREATE INDEX idx_tickets_officer       ON grievance_tickets(officer_id) WHERE officer_id IS NOT NULL;
CREATE INDEX idx_tickets_geom          ON grievance_tickets USING GIST(geom);
CREATE INDEX idx_tickets_embedding     ON grievance_tickets USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_tickets_transcript_trgm ON grievance_tickets USING GIN (voice_transcript gin_trgm_ops);

-- ============================================================
-- STATUS CHANGE AUDIT LOG
-- ============================================================
CREATE TABLE ticket_audit_log (
    id              BIGSERIAL       PRIMARY KEY,
    ticket_id       VARCHAR(20)     NOT NULL REFERENCES grievance_tickets(ticket_id) ON DELETE CASCADE,
    changed_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    changed_by      VARCHAR(100),   -- officer_id or 'SYSTEM' or 'CITIZEN'
    from_status     ticket_status,
    to_status       ticket_status   NOT NULL,
    action          VARCHAR(100),
    metadata        JSONB           DEFAULT '{}'::JSONB
);

CREATE INDEX idx_audit_ticket ON ticket_audit_log(ticket_id, changed_at DESC);

-- ============================================================
-- COMMUNITY CORROBORATION TABLE
-- ============================================================
CREATE TABLE ticket_corroborations (
    id              BIGSERIAL       PRIMARY KEY,
    ticket_id       VARCHAR(20)     NOT NULL REFERENCES grievance_tickets(ticket_id) ON DELETE CASCADE,
    corroborated_at TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    citizen_phone_masked VARCHAR(14),
    lat             DOUBLE PRECISION,
    lng             DOUBLE PRECISION,
    UNIQUE(ticket_id, citizen_phone_masked)
);

CREATE INDEX idx_corroboration_ticket ON ticket_corroborations(ticket_id);

-- ============================================================
-- OFFICERS TABLE
-- ============================================================
CREATE TABLE officers (
    officer_id      VARCHAR(50)     PRIMARY KEY,
    name            VARCHAR(200)    NOT NULL,
    email           VARCHAR(200)    UNIQUE NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    department      department_code NOT NULL,
    district        VARCHAR(100),
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ
);

-- ============================================================
-- PHASH FINGERPRINT REGISTRY (recycled image detection)
-- ============================================================
CREATE TABLE image_phash_registry (
    id              BIGSERIAL       PRIMARY KEY,
    phash           VARCHAR(64)     NOT NULL,
    dhash           VARCHAR(64),
    source_url      TEXT,
    is_known_fake   BOOLEAN         NOT NULL DEFAULT FALSE,
    registered_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    ticket_id       VARCHAR(20)     REFERENCES grievance_tickets(ticket_id)
);

CREATE INDEX idx_phash ON image_phash_registry(phash);

-- ============================================================
-- REAL-TIME NOTIFICATION EVENTS (SSE event store)
-- ============================================================
CREATE TABLE realtime_events (
    id              BIGSERIAL       PRIMARY KEY,
    event_id        UUID            NOT NULL DEFAULT uuid_generate_v4(),
    ticket_id       VARCHAR(20),
    audience        VARCHAR(20)     NOT NULL,  -- 'citizen' | 'officer' | 'all'
    event_type      VARCHAR(80)     NOT NULL,
    payload         JSONB           NOT NULL DEFAULT '{}'::JSONB,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    delivered       BOOLEAN         NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_events_ticket ON realtime_events(ticket_id, created_at DESC);
CREATE INDEX idx_events_audience ON realtime_events(audience, delivered, created_at DESC);

-- ============================================================
-- AUTO-UPDATE updated_at TRIGGER
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.version    = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tickets_updated_at
    BEFORE UPDATE ON grievance_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- NOTIFY TRIGGER FOR LISTEN/NOTIFY (WebSocket sync)
-- ============================================================
CREATE OR REPLACE FUNCTION notify_ticket_change()
RETURNS TRIGGER AS $$
DECLARE
    payload JSONB;
BEGIN
    payload := jsonb_build_object(
        'ticket_id', NEW.ticket_id,
        'status',    NEW.status,
        'updated_at', NEW.updated_at,
        'urgency_score', NEW.urgency_score,
        'officer_id', NEW.officer_id
    );
    PERFORM pg_notify('ticket_updates', payload::TEXT);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ticket_notify
    AFTER INSERT OR UPDATE ON grievance_tickets
    FOR EACH ROW EXECUTE FUNCTION notify_ticket_change();
"""

DOWNGRADE_SQL = """
DROP TABLE IF EXISTS realtime_events CASCADE;
DROP TABLE IF EXISTS image_phash_registry CASCADE;
DROP TABLE IF EXISTS officers CASCADE;
DROP TABLE IF EXISTS ticket_corroborations CASCADE;
DROP TABLE IF EXISTS ticket_audit_log CASCADE;
DROP TABLE IF EXISTS grievance_tickets CASCADE;
DROP TYPE IF EXISTS department_code;
DROP TYPE IF EXISTS audit_status;
DROP TYPE IF EXISTS geo_source;
DROP TYPE IF EXISTS proof_tier;
DROP TYPE IF EXISTS ticket_status;
DROP TYPE IF EXISTS dialect_code;
"""

if __name__ == "__main__":
    print("Run via Alembic: alembic upgrade head")
    print("Or apply UPGRADE_SQL directly against your PostgreSQL instance.")
