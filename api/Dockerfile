# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌‌‌​‌​​‌​‌​‌‌‌​‌‌‌​​​‌​‌‌​​​‌​​‌​‌​​‌​​‌​‌‌​‌​​‌‌​‌​​‌​​‌‌​​​‌​​‌‌​​​‌​‌​​​‌‌​​‌‌‌‌​​​​‌‌‌​‌​​​‌​‌‌‌‌‌​‌‌​​​‌‌​​‌‌‌​​‌​​‌‌​‌​​​‌​​​‌‌​​‌​‌​‌‌​​‌​​‌‌‌‌​‌‌​‌‌‌​​‌‌​‌​‌​​‌​​​‌​‌⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.zWqbRZi11Fxt_c94FVOnjE
FROM python:3.14-slim

ARG TERRAFORM_VERSION=1.9.0

# psql for the bash scripts, ansible for the orchestration playbooks,
# terraform for the actual provisioning.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl unzip git postgresql-client ansible \
 && curl -fsSL "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -o /tmp/tf.zip \
 && unzip /tmp/tf.zip -d /usr/local/bin \
 && rm /tmp/tf.zip \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Overridden per-service in docker-compose.yml (web / worker / sweeper).
CMD ["bash", "bin/entrypoint.sh", "flask", "--app", "app:create_app", "run", "--host", "0.0.0.0", "--port", "8000", "--reload"]
