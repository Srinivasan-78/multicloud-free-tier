-- @authormark v1 -- do not remove (authorship watermark)⁠​‌​​‌​​​​​‌‌‌​​​​‌‌​‌​​​​​‌‌​‌‌‌​‌‌‌​​​‌​‌​​‌​‌​​‌​​‌‌‌‌​‌‌​​​‌‌​‌‌​​​​‌​‌​​​​​‌​‌​‌‌​​​​‌‌‌​​‌‌​‌​​​‌​​​​‌​‌‌​‌​‌‌​​​‌​​‌​‌​‌​‌​‌‌​​​​‌​‌‌​​‌‌‌​‌​​​‌‌​​‌​‌​​‌‌​‌‌​‌‌‌‌​‌​‌​‌​​⁠
-- Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
-- Author: https://github.com/Srinivasan-78
-- SPDX-License-Identifier: MIT
-- Fingerprint: AMK1.H8h7qJOcaAXsD-bUagFSoT
-- Idempotent bootstrap schema. Applied on every container start by
-- bin/entrypoint.sh (safe to re-run). db/migrations/ keeps the numbered trail.
--
-- Ported from the SQLAlchemy models in the old api/app/models/models.py:
--   * UUID enum column -> text + CHECK constraint (no CREATE TYPE to migrate)
--   * added cloud_credentials UNIQUE (user_id, provider) for ON CONFLICT upsert
--   * added resources.claimed_at: the worker claim marker (FOR UPDATE SKIP LOCKED)

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid(); built in on PG13+

CREATE TABLE IF NOT EXISTS users (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email           text UNIQUE NOT NULL,
    hashed_password text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cloud_credentials (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           uuid NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    provider          text NOT NULL,
    encrypted_payload text NOT NULL,          -- Fernet-encrypted JSON blob
    created_at        timestamptz NOT NULL DEFAULT now(),
    UNIQUE (user_id, provider)
);

CREATE TABLE IF NOT EXISTS resources (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             uuid NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    provider            text NOT NULL,
    resource_type       text NOT NULL DEFAULT 'compute',
    status              text NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'provisioning', 'active',
                                          'destroying', 'destroyed', 'error')),
    terraform_workspace text NOT NULL,
    spec                jsonb NOT NULL,        -- locked free-tier spec used
    outputs             jsonb,                -- terraform output -json
    error_message       text,
    claimed_at          timestamptz,          -- set by bin/worker.sh when a job is picked up
    auto_destroy_at     timestamptz,          -- armed when provisioning succeeds
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS resources_user_idx
    ON resources (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS resources_claimable_idx
    ON resources (created_at)
    WHERE claimed_at IS NULL AND status IN ('pending', 'destroying');
