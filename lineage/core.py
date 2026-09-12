"""
core.py - Data lineage tracking for TASH.

Every input to a TASH decision is registered as a Source with a
verifiable content hash. Every transformation is recorded as a
LineageRecord. Records are hash-chained so any tampering is
detectable.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

GENESIS_HASH = "0" * 64


def content_hash(data):
    """SHA-256 of canonical JSON encoding. Same data to same hash, always."""
    body = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass
class Source:
    """A registered data source with verifiable origin."""
    source_id: str
    uri: str
    content_hash: str
    kind: str
    registered_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class LineageRecord:
    """A single transformation in the lineage chain."""
    index: int
    timestamp: str
    action: str
    input_source_ids: List[str]
    input_hashes: List[str]
    output_hash: str
    output_summary: str
    prev_hash: str
    hash: str

    def to_dict(self):
        return asdict(self)


def _hash_record(rec_dict):
    """Compute hash of a record dict (excluding its own 'hash' field)."""
    body = {k: v for k, v in rec_dict.items() if k != "hash"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class LineageTracker:
    """Tracks data provenance with a hash-chained, append-only record."""

    def __init__(self, path="lineage.jsonl"):
        self.path = Path(path) if path != ":memory:" else path
        self._sources = {}
        self._records = []
        self._next_index = 0
        self._last_hash = GENESIS_HASH

    def __len__(self):
        return len(self._records)

    def last_hash(self):
        return self._last_hash

    def register_source(self, uri, data, kind="data", metadata=None):
        """Register a data source with verifiable origin."""
        chash = content_hash(data)
        sid_raw = (uri + ":" + chash).encode("utf-8")
        sid = "src:" + hashlib.sha256(sid_raw).hexdigest()[:16]
        src = Source(
            source_id=sid,
            uri=uri,
            content_hash=chash,
            kind=kind,
            registered_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self._sources[sid] = src
        return src

    def get_source(self, source_id):
        return self._sources.get(source_id)

    def sources(self):
        return list(self._sources.values())

    def trace(self, action, fn, args=(), kwargs=None, sources=None):
        """Execute fn with full lineage tracking. Returns fn result."""
        kwargs = kwargs or {}
        sources = sources or []
        result = fn(*args, **kwargs)
        self.record(action, result, sources)
        return result

    def record(self, action, result, sources=None):
        """Record a transformation and its inputs."""
        sources = sources or []
        index = self._next_index
        self._next_index += 1
        timestamp = datetime.now(timezone.utc).isoformat()

        rec_dict = {
            "index": index,
            "timestamp": timestamp,
            "action": action,
            "input_source_ids": [s.source_id for s in sources],
            "input_hashes": [s.content_hash for s in sources],
            "output_hash": content_hash(result),
            "output_summary": str(result)[:120],
            "prev_hash": self._last_hash,
            "hash": "",
        }
        rec_dict["hash"] = _hash_record(rec_dict)
        rec = LineageRecord(**rec_dict)
        self._records.append(rec)
        self._last_hash = rec.hash
        return rec

    def flush(self):
        """Write pending records to disk (append-only)."""
        if self.path == ":memory:":
            count = len(self._records)
            self._records.clear()
            return count
        count = len(self._records)
        if count == 0:
            return 0
        with self.path.open("a", encoding="utf-8") as f:
            for r in self._records:
                line = dict(r.to_dict())
                line["__type__"] = "record"
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
        self._records.clear()
        return count

    @classmethod
    def load(cls, path):
        """Load a tracker from a JSONL file for verification."""
        tracker = cls(path=path)
        p = Path(path)
        if not p.exists():
            return tracker
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            data.pop("__type__", None)
            tracker._records.append(LineageRecord(**data))
        tracker._next_index = len(tracker._records)
        if tracker._records:
            tracker._last_hash = tracker._records[-1].hash
        return tracker

    @staticmethod
    def _verify_records(records):
        prev = GENESIS_HASH
        for i, r in enumerate(records):
            if r.index != i:
                return {"ok": False, "reason": "index mismatch at position " + str(i), "at": i}
            if r.prev_hash != prev:
                return {"ok": False, "reason": "prev_hash mismatch at position " + str(i), "at": i}
            expected = _hash_record(r.to_dict())
            if r.hash != expected:
                return {"ok": False, "reason": "hash mismatch at position " + str(i), "at": i}
            prev = r.hash
        return {"ok": True, "length": len(records), "head": prev}

    def verify(self):
        """Verify the in-memory chain."""
        return self._verify_records(self._records)
