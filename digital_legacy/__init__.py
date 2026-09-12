"""
Verifiable Digital Legacy - Sovereign digital estate tracking.

Maps to the Eight-Domain Stack "Verifiable Digital Legacy" domain:
  - Digital deeds backed by cryptographic fingerprints
  - Succession chains for asset transfer across generations
  - Tamper-evident ownership records
  - Verifiable legacy certificates
"""

from .core import (
    DigitalLegacyRegistry,
    Asset,
    Deed,
    Transfer,
    ASSET_TYPES,
)

__all__ = [
    "DigitalLegacyRegistry",
    "Asset",
    "Deed",
    "Transfer",
    "ASSET_TYPES",
]
