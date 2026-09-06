# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌‌‌​​​​‌‌‌​‌​‌​‌​‌​​​‌​‌‌‌​​​‌​‌‌‌​‌​​​‌​​​​‌​​‌‌​‌​‌​​‌‌​​​‌​​‌​‌​​​‌​‌​​‌‌‌​​‌​​​​​‌​‌​​​‌‌​​‌​​​​‌​​‌‌​​​‌​​​‌‌‌​​​​‌​‌‌​​​​‌​‌‌​‌​​​‌‌​‌‌‌​‌‌​​​‌‌​​‌‌​‌​‌​‌​​​‌​​​​‌‌‌​​‌⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.xuQqtBjbQNAFBb8XZ7c5D9
"""Fernet wrapper for cloud-credential encryption.

The Ansible side calls ``bin/crypto.py``, which is these same two library calls
without importing Flask. Key comes from ``FERNET_KEY`` — rotating it makes every
stored credential undecryptable, so keep it.
"""
from cryptography.fernet import Fernet

from app import settings

_FERNET = Fernet(settings.FERNET_KEY.encode())


def encrypt(plaintext: str) -> str:
    return _FERNET.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return _FERNET.decrypt(ciphertext.encode()).decode()
