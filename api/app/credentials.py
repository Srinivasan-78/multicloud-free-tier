# @authormark v1 -- do not remove (authorship watermark)⁠​‌​​‌‌​‌​‌​​​​​‌​‌​‌‌​​‌​‌​​​​‌‌​​‌‌​​​​​​‌‌​​‌​​‌​​​​‌​​​‌‌‌​​‌​‌​‌​​​​​‌​‌‌‌‌‌​‌‌​‌​‌‌​‌​​‌​​‌​‌​‌​‌‌​​‌‌​‌‌‌‌​‌​​​‌​‌​‌‌‌​​​‌​​‌‌‌​​​​‌‌‌‌​​‌​‌​​​‌​​​‌​​​​​‌​‌‌​​​‌​​‌‌‌​‌‌​⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.MAYC02B9P_kIVoEq8yDAbv
"""Store and list cloud credentials.

The payload is Fernet-encrypted before it touches the database; the plaintext is
only ever re-derived by the Ansible playbooks at provision/destroy time. Listing
returns the provider names only, never the blob. Replaces
``routers/credentials.py``.
"""
import json

from flask import Blueprint, flash, redirect, request, url_for

from app import db
from app.crypto import encrypt
from app.deps import login_required
from app.free_tier import SUPPORTED_PROVIDERS, normalize_provider

bp = Blueprint("credentials", __name__)


@bp.post("/credentials")
@login_required
def store(user):
    raw_provider = request.form.get("provider") or ""
    provider = normalize_provider(raw_provider)
    if provider not in SUPPORTED_PROVIDERS:
        flash(f"unsupported provider '{raw_provider}'", "error")
        return redirect(url_for("resources.dashboard"))

    try:
        payload = json.loads(request.form.get("payload") or "")
    except ValueError:
        payload = None
    if not isinstance(payload, dict):
        flash("credential payload must be a JSON object", "error")
        return redirect(url_for("resources.dashboard"))

    db.execute(
        """
        INSERT INTO cloud_credentials (user_id, provider, encrypted_payload)
        VALUES (%(uid)s, %(provider)s, %(enc)s)
        ON CONFLICT (user_id, provider)
        DO UPDATE SET encrypted_payload = EXCLUDED.encrypted_payload
        """,
        {"uid": user["id"], "provider": provider, "enc": encrypt(json.dumps(payload))},
    )
    flash(f"stored credentials for {provider}", "ok")
    return redirect(url_for("resources.dashboard"))


@bp.get("/credentials")
@login_required
def list_configured(user):
    rows = db.query_all(
        "SELECT provider, created_at FROM cloud_credentials "
        "WHERE user_id = %(uid)s ORDER BY provider",
        {"uid": user["id"]},
    )
    return {
        "credentials": [
            {"provider": r["provider"], "created_at": r["created_at"].isoformat()}
            for r in rows
        ]
    }
