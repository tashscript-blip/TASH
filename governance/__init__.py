"""
Governance & Risk Orchestration - Risk register, controls, and decision log.

Maps to the Eight-Domain Stack "Governance & Risk Orchestration" domain:
  - Risk decisions connected to system controls
  - Coverage reporting across all eight compliance domains
  - Auditable decision trail for federal review
"""

from .core import (
    GovernanceOrchestrator,
    Control,
    Risk,
    RiskDecision,
    DOMAINS,
)

__all__ = [
    "GovernanceOrchestrator",
    "Control",
    "Risk",
    "RiskDecision",
    "DOMAINS",
]
