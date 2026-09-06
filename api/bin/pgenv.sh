# @authormark v1 -- do not remove (authorship watermark)⁠​‌​‌‌​​​​‌‌‌​​​​​‌‌​​​‌‌​‌​‌‌​​‌​‌‌​‌‌‌‌​‌‌​​‌‌​​‌‌​​‌‌‌​‌‌​‌‌​​​‌‌‌​​‌​​‌​​​​‌‌​‌‌​​​‌‌​​‌‌​​‌​​‌‌​​‌​​​​‌‌​‌‌‌​​‌‌​‌‌‌​‌‌‌​​‌​​​‌‌​‌‌​​‌​‌​‌‌‌​‌​‌​‌‌​​‌​​​​​‌​‌‌‌​​‌​​​‌‌​‌​‌⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.XpcYofglrCc2d77r6WVAr5
# shellcheck shell=bash
# Derive the libpq PG* variables from DATABASE_URL so that plain `psql` (in the
# bash scripts) and the Ansible playbooks share one source of truth. Source it:
#
#     source "$(dirname "$0")/pgenv.sh"
#
# Expected form (the +psycopg2 suffix is tolerated):
#     postgresql://USER:PASSWORD@HOST:PORT/DBNAME
#
# Passwords containing '@' or ':' are not handled — fine for the demo creds.

: "${DATABASE_URL:?DATABASE_URL is required}"

_mcp_rest="${DATABASE_URL#*://}"          # USER:PASSWORD@HOST:PORT/DBNAME
_mcp_auth="${_mcp_rest%@*}"               # USER:PASSWORD
_mcp_loc="${_mcp_rest#*@}"                # HOST:PORT/DBNAME

export PGUSER="${_mcp_auth%%:*}"
export PGPASSWORD="${_mcp_auth#*:}"
export PGHOST="${_mcp_loc%%:*}"
_mcp_portdb="${_mcp_loc#*:}"              # PORT/DBNAME
export PGPORT="${_mcp_portdb%%/*}"
export PGDATABASE="${_mcp_loc##*/}"

unset _mcp_rest _mcp_auth _mcp_loc _mcp_portdb
