# @authormark v1 -- do not remove (authorship watermark)⁠​‌​​‌​​​​‌‌​‌​‌​​‌​‌​‌‌​​​‌​‌‌​‌​‌‌​‌‌‌​​‌​​​​‌​​‌‌‌​‌‌​​​‌‌​‌​‌​‌‌‌​‌‌‌​‌​​‌‌​‌​‌‌​​​‌‌​‌​​​‌​​​‌​​‌​‌‌​​‌‌​​​​​‌​​​​‌​​‌​​‌‌‌​​‌​​‌‌‌​​‌‌‌​‌​‌​‌​‌​‌‌‌​‌‌‌​​​‌​​‌‌​​‌​​‌​‌‌​​‌⁠
# Copyright (c) 2026 Srinivasan Vijayaraghavan <srinivasan.shyam2000@gmail.com>
# Author: https://github.com/Srinivasan-78
# SPDX-License-Identifier: MIT
# Fingerprint: AMK1.HjV-nBv5wMcDK0BNNuWq2Y
"""
Single source of truth for what can be provisioned.
Frontend options are just labels — this allowlist is what actually gets
enforced server-side before any terraform command runs.
"""

FREE_TIER_ALLOWLIST = {
    "aws": {
        "compute": {
            "instance_type": "t3.micro",
            "region": "us-east-1",
            "ami_owner": "amazon",
            "hourly_limit": 750,
            "note": "750 hrs/mo, first 12 months only",
        }
    },
    "gcp": {
        "compute": {
            "machine_type": "e2-micro",
            "region": "us-west1",
            "zone": "us-west1-a",
            "hourly_limit": None,
            "note": "Always free, must be in us-west1/us-central1/us-east1",
        }
    },
    "azure": {
        "compute": {
            "vm_size": "Standard_B1s",
            "region": "eastus",
            "hourly_limit": 750,
            "note": "750 hrs/mo, first 12 months only",
        }
    },
    "oracle": {
        "compute": {
            "shape": "VM.Standard.E2.1.Micro",
            "region": "us-ashburn-1",
            "hourly_limit": None,
            "note": "Always free, 2 instances max",
        }
    },
}

SUPPORTED_PROVIDERS = list(FREE_TIER_ALLOWLIST.keys())

# A provider is only provisionable if terraform/modules/<provider> exists.
# azure and oracle are on the allowlist above -- their free-tier specs are
# researched and correct -- but no module has been written for them yet, so
# provisioning one would queue a Celery job that dies on os.listdir of a
# directory that is not there, after the user has already stored real cloud
# credentials. Reject it at the API instead, and let /catalog say so.
IMPLEMENTED_PROVIDERS = {"aws", "gcp"}


def normalize_provider(provider: str) -> str:
    """Canonical lowercase form, used for storage, workspace paths and module
    lookup alike. Everything downstream compares against lowercase names, so a
    request carrying "AWS" must not be written to the database as-is."""
    return (provider or "").strip().lower()


def validate_request(provider: str, resource_type: str) -> dict:
    """Raises ValueError if not on the allowlist. Returns the locked spec otherwise."""
    provider = normalize_provider(provider)
    if provider not in FREE_TIER_ALLOWLIST:
        raise ValueError(f"provider '{provider}' not supported")
    if provider not in IMPLEMENTED_PROVIDERS:
        raise ValueError(
            f"provider '{provider}' is on the free-tier allowlist but has no terraform "
            f"module yet, so it cannot be provisioned; implemented: "
            f"{', '.join(sorted(IMPLEMENTED_PROVIDERS))}"
        )
    spec = FREE_TIER_ALLOWLIST[provider].get(resource_type)
    if spec is None:
        raise ValueError(f"resource_type '{resource_type}' not on free-tier allowlist for {provider}")
    return spec
