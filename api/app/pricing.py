# @authormark v1 -- do not remove (authorship watermark)⁠​‌‌‌‌​‌​​‌‌​​​‌‌​​‌‌​​‌‌​‌​​‌​‌​​‌‌​​‌‌‌​‌​​​​‌‌​‌‌​​‌‌​​‌​​‌‌‌​​​‌‌​‌​‌​‌‌​‌‌‌‌​​‌‌​​‌​​‌​‌​​‌‌​‌​​​‌​‌​‌‌​‌​​‌​​‌‌​‌​​​‌​‌‌​​‌​‌‌‌‌​​​​‌‌​‌​​‌​‌​​‌‌​‌​‌​​‌​​‌​‌​‌‌​‌​​‌‌​​​​‌⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.zc3JgCfN5o2SEi4YxiMIZa
"""
Theoretical cost display only — actual spend is $0 on free tier.
Hardcoded public on-demand pricing snapshot (update periodically; real
implementation would call each provider's pricing API/SDK).
"""

PRICING_USD_PER_HOUR = {
    "aws": {"compute": 0.0104},      # t3.micro on-demand, us-east-1
    "gcp": {"compute": 0.0084},      # e2-micro on-demand, us-west1
    "azure": {"compute": 0.0104},    # B1s on-demand, eastus
    "oracle": {"compute": 0.0},      # always-free shape has no paid equivalent tier
}


def estimate(provider: str, resource_type: str) -> dict:
    hourly = PRICING_USD_PER_HOUR.get(provider, {}).get(resource_type, 0.0)
    return {
        "provider": provider,
        "resource_type": resource_type,
        "hourly_usd": hourly,
        "monthly_usd_if_paid": round(hourly * 730, 2),
    }
