# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌​​​‌​​‌​​‌​‌​​‌‌​‌​‌‌​‌‌​​​‌‌​​‌​‌‌​‌​‌‌‌‌​​‌​​‌‌​‌​​​‌‌​‌‌​‌​‌​​‌​‌​​‌​​‌​​‌​‌​‌‌​​​​​‌‌​‌‌‌​‌​‌​‌​‌​‌‌​‌‌​‌​‌‌‌​​‌​​‌​​‌‌​‌​​‌‌​‌‌‌​‌‌​​‌​​​‌​‌​​‌​​‌‌​‌​​‌​​‌‌​‌​‌​‌​​‌​‌‌⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.bJkc-y4mJIX7UmrM7dRi5K
"""Request helpers. Replaces ``core/deps.py``, which turned a JWT bearer token
into a ``User`` row; here it is the session cookie instead.
"""
from functools import wraps

from flask import redirect, session, url_for

from app import db


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return db.query_one("SELECT id, email FROM users WHERE id = %(id)s", {"id": uid})


def login_required(view):
    """Wrap a view so it only runs for a logged-in user. The user row is passed
    as the first positional argument; unauthenticated requests are redirected to
    the login page.
    """

    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("auth.login"))
        return view(user, *args, **kwargs)

    return wrapped
