#!/usr/bin/env python3
# @authormark v1 -- do not remove (authorship watermark)⁠​‌​​​‌‌‌​‌‌‌​‌‌​​‌‌‌​‌‌​​​‌‌​​​​​‌‌​‌​​​​‌​​​​‌‌​‌‌​​‌​‌​‌‌‌‌​‌​​‌​​‌‌‌‌​‌‌​​‌‌​​‌​​​​‌‌​‌​​​‌‌​​‌‌​​‌‌‌​‌​‌‌‌‌‌​‌‌‌‌​​​​​‌‌​​​​​‌‌​​‌‌​​‌​‌​​​​​‌​​‌‌‌​​​‌‌‌​​‌​​‌‌‌​​‌​‌​‌​‌​​⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.Gvv0hCezOfCFg_x0fPN99T
"""Small database touch-points for the Ansible playbooks — the structured reads
and writes that are awkward through psql. Simple status flips stay in psql (see
bin/worker.sh). This is the part of app/services/tasks.py that talked to the DB.

    db.py get-job    <resource_id>
        -> JSON {user_id, provider, resource_type, spec, encrypted_payload}
    db.py set-status <resource_id> <status> [message words...]
    db.py set-active <resource_id> <outputs_json_file> <hours>

Reads DATABASE_URL from the environment.
"""
import json
import os
import sys

import psycopg2
import psycopg2.extras


def _connect():
    dsn = os.environ["DATABASE_URL"].replace("postgresql+psycopg2://", "postgresql://")
    return psycopg2.connect(dsn)


def get_job(resource_id):
    with _connect() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT r.user_id::text AS user_id,
                       r.provider,
                       r.resource_type,
                       r.spec,
                       c.encrypted_payload
                FROM resources r
                LEFT JOIN cloud_credentials c
                    ON c.user_id = r.user_id AND c.provider = r.provider
                WHERE r.id = %s
                """,
                (resource_id,),
            )
            row = cur.fetchone()
    if row is None:
        sys.exit(f"no resource {resource_id}")
    json.dump(row, sys.stdout)


def set_status(resource_id, status, *message_words):
    message = " ".join(message_words) or None
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE resources SET status = %s, error_message = %s, "
                "updated_at = now() WHERE id = %s",
                (status, message, resource_id),
            )


def set_active(resource_id, outputs_file, hours):
    with open(outputs_file, encoding="utf-8") as handle:
        outputs = handle.read()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE resources
                SET status = 'active',
                    outputs = %s::jsonb,
                    auto_destroy_at = now() + (%s || ' hours')::interval,
                    error_message = NULL,
                    updated_at = now()
                WHERE id = %s
                """,
                (outputs, str(hours), resource_id),
            )


_COMMANDS = {"get-job": get_job, "set-status": set_status, "set-active": set_active}


def main(argv):
    if not argv or argv[0] not in _COMMANDS:
        sys.exit(f"usage: db.py {{{'|'.join(_COMMANDS)}}} ...")
    _COMMANDS[argv[0]](*argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
