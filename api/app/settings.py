# @authormark v1 -- do not remove (authorship watermark)⁠​​‌‌​​​‌​‌​​‌​‌​​‌‌‌​‌​‌​​‌‌‌​​‌​‌​​‌​‌‌​‌‌‌​​‌​​‌​​​​‌​​‌​​‌​‌‌​‌​‌​‌​​​​‌‌​​‌‌​‌​‌‌​‌​​‌‌‌​​​‌​‌‌​‌​​‌​‌‌​​‌​​​​‌‌​​‌‌​‌​​‌‌‌​​​‌‌​‌‌​​‌‌‌‌​‌​​‌​​‌​​‌​‌​‌​​‌​​‌​​‌‌‌​​‌​​​‌​‌⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.1Ju9KrBKT3Zqid3N6zIRNE
"""Environment configuration.

Every value is required unless a default is shown; importing this module raises
``KeyError`` otherwise, so the process refuses to start with a half-filled
``.env`` — the same contract the old ``pydantic`` ``Settings`` class enforced.
"""
import os

DATABASE_URL = os.environ["DATABASE_URL"]
SECRET_KEY = os.environ["SECRET_KEY"]
FERNET_KEY = os.environ["FERNET_KEY"]

TERRAFORM_ROOT = os.environ.get("TERRAFORM_ROOT", "/terraform")
MAX_RESOURCES_PER_PROVIDER = int(os.environ.get("MAX_RESOURCES_PER_PROVIDER", "1"))
AUTO_DESTROY_HOURS = int(os.environ.get("AUTO_DESTROY_HOURS", "24"))
