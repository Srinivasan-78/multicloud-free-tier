# @authormark v1 -- do not remove (authorship watermark)⁠​‌​‌​​‌​​​‌‌​‌​‌​‌‌​‌​‌​​‌‌​‌​​‌​‌​​‌​‌​​‌​​​​‌‌​‌‌​​​‌​​​‌‌​​​‌​‌‌​​​​‌​‌‌​‌​​‌​‌‌​‌‌‌‌​‌​‌​‌​‌​‌‌​‌​‌​​‌​‌​​​​​‌‌‌​‌​‌​​‌‌​​‌​​‌​‌​‌‌​​‌‌​‌​‌‌​‌‌​‌‌‌​​‌‌​‌​​‌​‌‌‌​​​‌​​‌‌​​​​⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.R5jiJCb1aioUjPu2Vkniq0
"""Catalog, provisioning, listing, teardown. Replaces ``routers/resources.py``.

The browser still sends only two labels (``provider``, ``resource_type``). The
locked spec is looked up server-side in :mod:`app.free_tier` and written onto the
row; the worker (``bin/worker.sh``) picks the row up and runs Ansible. There is
no field in which a hacked page could ask for a paid instance.
"""
import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app import db, pricing
from app.deps import login_required
from app.free_tier import (
    FREE_TIER_ALLOWLIST,
    IMPLEMENTED_PROVIDERS,
    normalize_provider,
    validate_request,
)
from app.settings import MAX_RESOURCES_PER_PROVIDER

bp = Blueprint("resources", __name__)

# Counts against the per-provider cap (mirrors the old ResourceStatus set).
_CAP_STATES = ("pending", "provisioning", "active")

_RESOURCE_COLUMNS = """
    id, provider, resource_type, status, spec, outputs,
    error_message, auto_destroy_at, created_at
"""


def _catalog():
    return {
        provider: {
            "implemented": provider in IMPLEMENTED_PROVIDERS,
            "resource_types": types,
        }
        for provider, types in FREE_TIER_ALLOWLIST.items()
    }


def _estimates():
    rows = []
    for provider, types in FREE_TIER_ALLOWLIST.items():
        for rtype, spec in types.items():
            est = pricing.estimate(provider, rtype)
            rows.append(
                {
                    "provider": provider,
                    "resource_type": rtype,
                    "instance_label": spec.get("instance_type")
                    or spec.get("machine_type")
                    or spec.get("vm_size")
                    or spec.get("shape", ""),
                    "hourly_usd": est["hourly_usd"],
                    "monthly_usd_if_paid": est["monthly_usd_if_paid"],
                }
            )
    return rows


def _resources_for(user):
    return db.query_all(
        f"SELECT {_RESOURCE_COLUMNS} FROM resources "
        "WHERE user_id = %(uid)s ORDER BY created_at DESC",
        {"uid": user["id"]},
    )


def render_dashboard(user):
    configured = [
        r["provider"]
        for r in db.query_all(
            "SELECT provider FROM cloud_credentials WHERE user_id = %(uid)s",
            {"uid": user["id"]},
        )
    ]
    return render_template(
        "dashboard.html",
        email=user["email"],
        catalog=_catalog(),
        estimates=_estimates(),
        resources=_resources_for(user),
        configured=configured,
        providers=list(FREE_TIER_ALLOWLIST.keys()),
    )


@bp.get("/dashboard")
@login_required
def dashboard(user):
    return render_dashboard(user)


@bp.get("/resources/fragment")
@login_required
def resources_fragment(user):
    return render_template("_resources.html", resources=_resources_for(user))


@bp.get("/resources")
@login_required
def list_resources(user):
    return {"resources": [_json_safe(r) for r in _resources_for(user)]}


@bp.get("/resources/catalog")
def catalog():
    return _catalog()


@bp.get("/resources/catalog/estimate")
def catalog_estimate():
    return {"estimates": _estimates()}


@bp.post("/resources")
@login_required
def create_resource(user):
    raw_provider = request.form.get("provider") or ""
    provider = normalize_provider(raw_provider)
    resource_type = request.form.get("resource_type") or "compute"

    try:
        spec = validate_request(provider, resource_type)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("resources.dashboard"))

    live = db.query_one(
        "SELECT count(*) AS n FROM resources "
        "WHERE user_id = %(uid)s AND provider = %(p)s AND status = ANY(%(states)s)",
        {"uid": user["id"], "p": provider, "states": list(_CAP_STATES)},
    )["n"]
    if live >= MAX_RESOURCES_PER_PROVIDER:
        flash(
            f"resource cap reached for {provider} (max {MAX_RESOURCES_PER_PROVIDER})",
            "error",
        )
        return redirect(url_for("resources.dashboard"))

    db.execute(
        """
        INSERT INTO resources
            (user_id, provider, resource_type, status, terraform_workspace, spec)
        VALUES
            (%(uid)s, %(p)s, %(rt)s, 'pending', %(ws)s, %(spec)s::jsonb)
        """,
        {
            "uid": user["id"],
            "p": provider,
            "rt": resource_type,
            "ws": f'{user["id"]}/{provider}',
            "spec": json.dumps(spec),
        },
    )
    flash(f"queued {provider} {resource_type} — provisioning shortly", "ok")
    return redirect(url_for("resources.dashboard"))


@bp.post("/resources/<uuid:resource_id>/destroy")
@login_required
def destroy_resource(user, resource_id):
    row = db.query_one(
        "SELECT status FROM resources WHERE id = %(id)s AND user_id = %(uid)s",
        {"id": str(resource_id), "uid": user["id"]},
    )
    if row is None:
        abort(404)
    if row["status"] in ("active", "error"):
        db.execute(
            "UPDATE resources SET status = 'destroying', claimed_at = NULL, "
            "updated_at = now() WHERE id = %(id)s",
            {"id": str(resource_id)},
        )
        flash("teardown queued", "ok")
    else:
        flash(f"cannot destroy from status '{row['status']}'", "error")
    return redirect(url_for("resources.dashboard"))


def _json_safe(row):
    out = dict(row)
    for key, value in out.items():
        if hasattr(value, "isoformat"):
            out[key] = value.isoformat()
    out["id"] = str(out["id"])
    return out
