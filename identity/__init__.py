"""
Identity Governance - Cryptographic machine identity and signed action trails.

Maps to the Eight-Domain Stack "Identity Governance" domain:
  - Machine identity trails for every automated action
  - Cryptographic verification of who did what
  - Revocation and lifecycle management
"""

from .core import (
    IdentityRegistry,
    MachineIdentity,
    SignedAction,
    generate_key,
    sign,
    verify_signature,
)

__all__ = [
    "IdentityRegistry",
    "MachineIdentity",
    "SignedAction",
    "generate_key",
    "sign",
    "verify_signature",
]
