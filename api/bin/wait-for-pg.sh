#!/usr/bin/env bash
# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌​‌‌​‌​‌‌​​‌​​​‌​​​​‌‌​‌‌​​‌‌‌​‌​​​‌‌‌​‌​​‌‌​​​‌​​‌‌‌​​‌​‌​‌​​​‌​‌‌​​‌​‌​‌‌‌‌‌​​‌‌​‌​‌​‌​​​‌​​​‌‌​​​‌‌​‌​​​​​‌​‌‌​​​‌​​‌​​​​‌​​‌‌​‌‌​‌​‌​​​​‌​​‌‌‌​‌‌‌​‌​​‌‌​‌​‌‌‌‌​​​​​‌‌​‌​‌⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.mdCgGLNTY_5DcAbBmBwMx5
# Block until Postgres answers, then exec the given command. Used by the worker
# and sweeper services (which must not apply the schema themselves).
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$here/pgenv.sh"

echo "[wait-for-pg] $PGHOST:$PGPORT/$PGDATABASE"
until psql -tAc 'SELECT 1' >/dev/null 2>&1; do
  sleep 1
done
echo "[wait-for-pg] up"

exec "$@"
