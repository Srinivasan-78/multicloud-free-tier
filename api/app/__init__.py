# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌‌​‌​​​​‌‌​​‌‌​​‌‌​‌​​​‌‌​​‌‌‌​​‌‌​‌​‌​‌​​​‌‌‌​‌‌​​‌​​​‌‌‌​‌‌‌​​‌‌​‌‌​​‌‌​‌‌​‌​‌‌​‌​​‌​​‌‌‌​​‌​‌​​​​‌‌​‌‌​‌‌‌‌​‌‌‌​​‌‌​‌​‌‌‌‌‌​‌​‌​​​​​‌​​​‌‌​​‌‌​‌​‌‌​​‌‌​​‌‌​‌​‌​‌‌‌​‌‌​‌‌​​⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.t34g5Gdw6mi9Cos_PFk3Wl
"""Flask application factory. Replaces the FastAPI app that lived in
``app/main.py``.

The app is server-rendered (Jinja2) — there is no separate frontend. Auth is a
signed session cookie (Flask's built-in ``session``), not a JWT, so there is no
token for a browser to hold and no cross-origin surface: the pages and the JSON
endpoints are one origin, which is why there is no CORS config here.
"""
from flask import Flask, redirect, session, url_for

from app import settings


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.SECRET_KEY,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=256 * 1024,
    )

    from app import auth, credentials, resources

    app.register_blueprint(auth.bp)
    app.register_blueprint(credentials.bp)
    app.register_blueprint(resources.bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/")
    def index():
        target = "resources.dashboard" if session.get("user_id") else "auth.login"
        return redirect(url_for(target))

    return app
