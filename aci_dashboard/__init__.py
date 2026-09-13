"""
ACI Dashboard - Adaptive Ceremonial Interface.

A live web dashboard that visualizes all eight compliance domains,
runs live demos, and adapts its display based on overall system posture.

Maps to the "Adaptive Ceremonial Interface" language in the LGC
Article V framework.
"""

from .app import create_app

__all__ = ["create_app"]
