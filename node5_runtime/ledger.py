"""
ledger.py - Hash-chained, append-only action ledger.
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

GENESIS_HASH = "0" * 64


def _canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash_entry(index, timestamp, action, payload, prev_hash):
    body = _canonical({
        "index": index,
        "timestamp": timestamp,
        "action": action,
        "payload": payload,
        "prev_hash": prev_hash,
    })
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass
class LedgerEntry:
    index: int
    timestamp: str
    action: str
    payload: Dict[str, Any]
    prev_hash: str
    hash: str

    def to_dict(self):
        return asdict(self)


class ActionLedger:
    def __init__(self, path="node5_ledger.jsonl"):
        self.path = Path(path) if path != ":memory:" else path
        self._entries = []
        self._next_index = 0
        self._last_hash = GENESIS_HASH

    def __len__(self):
        return len(self._entries)

    def last_hash(self):
        return self._last_hash

    def append(self, action, payload):
        index = self._next_index
        self._next_index += 1
        timestamp = datetime.now(timezone.utc).isoformat()
        prev_hash = self._last_hash
        entry_hash = _hash_entry(index, timestamp, action, payload, prev_hash)
        entry = LedgerEntry(
            index=index,
            timestamp=timestamp,
            action=action,
            payload=payload,
            prev_hash=prev_hash,
            hash=entry_hash,
        )
        self._entries.append(entry)
        self._last_hash = entry_hash
        return entry

    def flush(self):
        count = len(self._entries)
        if self.path == ":memory:" or count == 0:
            self._entries.clear()
            return count
        with self.path.open("a", encoding="utf-8") as f:
            for e in self._entries:
                f.write(json.dumps(e.to_dict(), sort_keys=True, default=str) + "\n")
        self._entries.clear()
        return count

    @classmethod
    def load(cls, path):
        ledger = cls(path=path)
        p = Path(path)
        if not p.exists():
            return ledger
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            ledger._entries.append(LedgerEntry(**data))
        ledger._next_index = len(ledger._entries)
        if ledger._entries:
            ledger._last_hash = ledger._entries[-1].hash
        return ledger

    def verify(self):
        prev = GENESIS_HASH
        for i, e in enumerate(self._entries):
            if e.index != i:
                return {"ok": False, "reason": "index mismatch at position " + str(i), "at": i}
            if e.prev_hash != prev:
                return {"ok": False, "reason": "prev_hash mismatch at position " + str(i), "at": i}
            expected = _hash_entry(e.index, e.timestamp, e.action, e.payload, e.prev_hash)
            if e.hash != expected:
                return {"ok": False, "reason": "hash mismatch at position " + str(i), "at": i}
            prev = e.hash
        return {"ok": True, "length": len(self._entries), "head": prev}
