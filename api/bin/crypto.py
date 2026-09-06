#!/usr/bin/env python3
# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌​​​‌​​‌​‌​​‌‌​‌​​‌​​‌​‌​​‌‌‌​​‌‌​‌​‌‌​‌​‌‌​‌​​​‌‌​‌‌‌​‌‌​‌​‌‌​‌‌​​​‌​​‌​​‌​​‌​‌​​‌​​​​​‌​‌‌​‌​‌​​‌​‌‌​‌​‌‌​‌​​‌​​​‌‌​​​‌‌​‌​​​​‌‌​‌​‌​‌‌‌​​‌​​‌​‌​‌​​​​‌‌​‌​​​‌​‌​‌‌‌​​‌‌​‌‌​⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.bSINkZ7kbIH-KZF45rT4W6
"""Fernet encrypt/decrypt, stdin -> stdout. The Ansible playbooks call this to
recover a stored credential blob at provision/destroy time.

Same two library calls as app/crypto.py, without importing Flask. Key comes from
FERNET_KEY — the same variable the web app uses.

    echo -n "$ciphertext" | bin/crypto.py decrypt
"""
import os
import sys

from cryptography.fernet import Fernet


def main(argv):
    if len(argv) != 1 or argv[0] not in ("encrypt", "decrypt"):
        sys.exit("usage: crypto.py encrypt|decrypt  (reads stdin, writes stdout)")

    fernet = Fernet(os.environ["FERNET_KEY"].encode())
    data = sys.stdin.buffer.read()
    if argv[0] == "encrypt":
        sys.stdout.buffer.write(fernet.encrypt(data))
    else:
        sys.stdout.buffer.write(fernet.decrypt(data))


if __name__ == "__main__":
    main(sys.argv[1:])
