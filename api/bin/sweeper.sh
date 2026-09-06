#!/usr/bin/env bash
# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌‌‌​​​​‌​​‌​‌‌​‌‌​‌​​‌​‌‌​‌‌‌​​‌‌‌​‌‌‌​‌​​‌​​‌​​‌‌​‌‌​​‌​​‌‌‌‌​‌​​‌​‌‌​‌‌​​‌​‌​‌​​‌​​​​‌‌​‌​​​​​‌‌‌​​​​‌​​‌‌‌​​​‌‌​‌​​​​‌‌​​‌‌​‌​​​‌​‌​​‌‌​​​​​​‌‌​‌‌​​‌​‌‌​​‌​‌​‌​‌​‌​‌​​‌‌‌​⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.xKinwI6OKeHh8N43E06YUN
# Hourly: flag every active resource past its 24h safety window for teardown.
# The worker then destroys them. Replaces Celery beat + sweep_expired_resources.
#
# Because this runs hourly, a resource lives 24-25h, not exactly 24 — well
# inside every provider's monthly free allowance.
set -uo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$here/pgenv.sh"

sweep_sql="
WITH expired AS (
    UPDATE resources
    SET status='destroying', claimed_at=NULL, updated_at=now()
    WHERE status='active'
      AND auto_destroy_at IS NOT NULL
      AND auto_destroy_at <= now()
    RETURNING 1
)
SELECT count(*) FROM expired;
"

echo "[sweeper] started"
while true; do
  n="$(psql -XqtAc "$sweep_sql" 2>/dev/null || echo '?')"
  echo "[sweeper] flagged ${n} expired resource(s) at $(date -u +%FT%TZ)"
  sleep 3600
done
