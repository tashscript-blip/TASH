"""
AI Discovery & Security Posture - Model and vendor inventory.

Maps to the Eight-Domain Stack "AI Discovery & Security Posture" domain:
  - Continuous inventory of model integrations
  - Continuous inventory of vendor integrations
  - Risk classification per NIST AI RMF
  - Security posture reporting for federal review
"""

from .core import (
    AIDiscoveryRegistry,
    AIModel,
    Vendor,
    RISK_CLASSES,
)

__all__ = ["AIDiscoveryRegistry", "AIModel", "Vendor", "RISK_CLASSES"]
