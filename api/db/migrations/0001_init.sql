-- @authormark v1 -- do not remove (authorship watermark)⁠​‌‌​‌‌‌‌​‌​‌​​‌​​‌​​‌‌‌‌​​‌​‌‌​‌​‌‌​​​​‌​‌‌‌​​‌‌​​‌‌​‌​‌​‌​​‌​​​​‌‌​‌‌‌‌​‌‌​‌‌‌​​​‌‌​‌​‌​‌‌​‌​‌​​‌‌‌​​​‌​‌​‌​‌‌​​‌​​​​‌​​‌​‌​‌‌​​‌​​‌‌‌​​‌‌​‌‌​​​‌‌​​‌​​​‌​‌​‌​‌​‌​​‌​‌​​‌​‌​‌​​⁠
-- Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
-- Author: https://github.com/Srinivasan-78
-- SPDX-License-Identifier: MIT
-- Fingerprint: AMK1.oRO-as5Hon5jqVBVNldUJT
-- 0001_init — initial schema.
--
-- Identical to db/schema.sql (which is the idempotent bootstrap applied on every
-- start). This numbered copy is the migration trail: later changes go in
-- 0002_*.sql, 0003_*.sql, ... and also get folded into schema.sql so a fresh
-- database and a migrated one converge.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

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
    encrypted_payload text NOT NULL,
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
    spec                jsonb NOT NULL,
    outputs             jsonb,
    error_message       text,
    claimed_at          timestamptz,
    auto_destroy_at     timestamptz,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS resources_user_idx
    ON resources (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS resources_claimable_idx
    ON resources (created_at)
    WHERE claimed_at IS NULL AND status IN ('pending', 'destroying');

CREATE TABLE IF NOT EXISTS usage_log (
    id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_id          uuid NOT NULL REFERENCES resources (id) ON DELETE CASCADE,
    provider             text NOT NULL,
    hours_active         numeric,
    theoretical_cost_usd numeric,
    logged_at            timestamptz NOT NULL DEFAULT now()
);
