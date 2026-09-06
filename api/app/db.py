# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌​‌​‌​​‌​‌​‌‌​​‌​​​‌​​​‌​‌​‌‌​​‌‌‌‌​​​​​‌‌​‌​​​​‌‌‌​​​​‌‌​‌‌​‌​​‌‌​‌‌​​​‌​‌‌​‌​‌‌‌​‌​​​‌​‌​​‌​​‌‌‌​‌​‌​​‌‌​‌​‌​‌‌​‌‌‌​​‌‌‌​‌‌​​​‌‌‌​​‌​‌‌​‌‌‌‌​‌‌​​‌​​​​‌‌​​‌​​‌‌​‌​​‌​‌‌​‌​​​⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.jVDVx48m6-tRu5nv9od2ih
"""Thin psycopg2 access layer. Replaces SQLAlchemy, the ORM models and Alembic.

Hand-written SQL sits next to each route. The schema is ``db/schema.sql``,
applied idempotently on container start by ``bin/entrypoint.sh``; there is no
migration tool — ``db/migrations/`` keeps a plain numbered trail.
"""
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
import psycopg2.pool

from app import settings

# .env may still carry the SQLAlchemy-style scheme; psycopg2 wants plain.
_DSN = settings.DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
_POOL = psycopg2.pool.ThreadedConnectionPool(1, 10, dsn=_DSN)


@contextmanager
def _cursor(commit):
    conn = _POOL.getconn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
        conn.commit() if commit else conn.rollback()
    except Exception:
        conn.rollback()
        raise
    finally:
        _POOL.putconn(conn)


def query_all(sql, params=None):
    with _cursor(commit=False) as cur:
        cur.execute(sql, params or {})
        return cur.fetchall()


def query_one(sql, params=None):
    with _cursor(commit=False) as cur:
        cur.execute(sql, params or {})
        return cur.fetchone()


def execute(sql, params=None):
    """Run an INSERT/UPDATE/DELETE; return the affected row count."""
    with _cursor(commit=True) as cur:
        cur.execute(sql, params or {})
        return cur.rowcount


def execute_returning(sql, params=None):
    """Run a write with a RETURNING clause; commit and return the one row."""
    with _cursor(commit=True) as cur:
        cur.execute(sql, params or {})
        return cur.fetchone()
