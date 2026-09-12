"""
Lineage - Data provenance tracking for TASH.

Maps to the Eight-Domain Stack "DSPM & Data Lineage" domain:
  - Automated controls for training data origin
  - "Truthful Output" claims
  - Data provenance for autonomous systems
"""

from .core import LineageTracker, LineageRecord, Source, GENESIS_HASH, content_hash

__all__ = ["LineageTracker", "LineageRecord", "Source", "GENESIS_HASH", "content_hash"]
