"""
Supply Chain Integrity - Third-party component tracking and verification.

Maps to the Eight-Domain Stack "Supply Chain Integrity" domain:
  - Verification of third-party model updates
  - Tracking of external library versions
  - Tamper detection on any registered component
  - Approval workflow for changes
"""

from .core import (
    SupplyChainRegistry,
    Component,
    Approval,
    COMPONENT_TYPES,
)

__all__ = ["SupplyChainRegistry", "Component", "Approval", "COMPONENT_TYPES"]
