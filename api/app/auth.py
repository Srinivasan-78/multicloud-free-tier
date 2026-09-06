# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌​‌‌​​​‌‌​​‌‌‌​​‌‌​‌‌‌​‌‌‌​‌​​​​‌‌​​‌‌​‌​‌​​‌​​‌‌​‌​‌​​​‌‌​‌​​​‌‌​​‌​​​‌‌​​​‌​​‌‌​‌‌‌​​‌‌​‌​‌‌​‌‌​‌​‌​​‌​​‌‌‌‌​‌​‌​‌​​​‌‌​​‌‌​​​‌‌​‌​‌​‌‌​​‌​​​‌​‌​‌​‌​‌​‌‌​​​​‌​​​‌‌​​‌‌‌​‌​​⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.lg7t3Rj4dbnkjOTf5dUXFt
"""Register / login / logout. Session cookie + bcrypt password hashing.
Replaces ``routers/auth.py``, which issued JWTs.
"""
import bcrypt
from flask import Blueprint, redirect, render_template, request, session, url_for

from app import db

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("resources.dashboard"))
        return render_template("login.html")

    email = (request.form.get("email") or "").strip().lower()
    password = (request.form.get("password") or "").encode()
    want_register = request.form.get("action") == "register"

    if not email or not password:
        return render_template("login.html", error="email and password required"), 400

    if want_register:
        if db.query_one("SELECT 1 FROM users WHERE email = %(e)s", {"e": email}):
            return render_template("login.html", error="email already registered"), 400
        pw_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode()
        row = db.execute_returning(
            "INSERT INTO users (email, hashed_password) VALUES (%(e)s, %(p)s) RETURNING id",
            {"e": email, "p": pw_hash},
        )
        session["user_id"] = str(row["id"])
        return redirect(url_for("resources.dashboard"))

    user = db.query_one(
        "SELECT id, hashed_password FROM users WHERE email = %(e)s", {"e": email}
    )
    if not user or not bcrypt.checkpw(password, user["hashed_password"].encode()):
        return render_template("login.html", error="invalid credentials"), 401
    session["user_id"] = str(user["id"])
    return redirect(url_for("resources.dashboard"))


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
