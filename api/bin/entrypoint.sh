#!/usr/bin/env bash
# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌​​‌‌​​‌​​​​‌​​‌​​​​​‌​‌​​‌​‌​​‌‌​​​‌​​‌‌‌‌​​​​​‌‌​‌‌​​​‌​‌‌​‌​‌‌​‌​‌‌​‌‌​‌‌‌‌​‌​‌​‌​‌​‌​​‌‌​‌​‌​​‌‌​​​‌‌‌​‌‌‌​‌​‌‌‌‌‌​‌‌​​‌​‌​‌​​​‌​‌​‌​‌‌​​‌​‌‌​​​‌​​‌​​​‌‌​​‌‌​​‌​​​‌‌‌‌​‌​⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.fBAJbx6-koUMLw_eEYbFdz
# Web service entrypoint: wait for Postgres, apply the idempotent schema, then
# exec the given command (normally `flask run`).
set -euo pipefail

: "${SECRET_KEY:?}" "${FERNET_KEY:?}"

here="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$here/pgenv.sh"

echo "[entrypoint] waiting for $PGHOST:$PGPORT/$PGDATABASE"
until psql -tAc 'SELECT 1' >/dev/null 2>&1; do
  sleep 1
done

echo "[entrypoint] applying schema (idempotent)"
psql -v ON_ERROR_STOP=1 -f "$here/../db/schema.sql"

echo "[entrypoint] exec: $*"
exec "$@"
