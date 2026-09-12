"""
core.py - Verifiable Digital Legacy.

Registers digital assets, issues cryptographic deeds binding asset to
owner and successor, and records transfers as a hash-chained succession
log. Every deed includes a SHA-256 fingerprint of the asset content and
can be verified independently.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ASSET_TYPES = [
    "creative_work",
    "source_code",
    "dataset",
    "trademark",
    "patent",
    "financial_instrument",
    "personal_artifact",
]

GENESIS_HASH = "0" * 64


def _now():
    return datetime.now(timezone.utc).isoformat()


def _canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def content_fingerprint(data):
    """SHA-256 of canonical JSON or raw bytes/str."""
    if isinstance(data, bytes):
        raw = data
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    else:
        raw = _canonical(data).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _hash_transfer(rec_dict):
    body = {k: v for k, v in rec_dict.items() if k != "hash"}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


@dataclass
class Asset:
    """A registered digital asset."""
    asset_id: str
    name: str
    asset_type: str
    owner: str
    successor: Optional[str]
    content_hash: str
    registered_at: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Deed:
    """A cryptographic deed binding asset to owner and successor."""
    deed_id: str
    asset_id: str
    owner: str
    successor: Optional[str]
    content_hash: str
    issued_at: str
    deed_signature: str

    def to_dict(self):
        return asdict(self)

    def signable(self):
        return {
            "deed_id": self.deed_id,
            "asset_id": self.asset_id,
            "owner": self.owner,
            "successor": self.successor,
            "content_hash": self.content_hash,
            "issued_at": self.issued_at,
        }


@dataclass
class Transfer:
    """A hash-chained transfer of an asset between parties."""
    index: int
    asset_id: str
    from_party: str
    to_party: str
    reason: str
    timestamp: str
    prev_hash: str
    hash: str

    def to_dict(self):
        return asdict(self)


class DigitalLegacyRegistry:
    """Registry for verifiable digital legacy and succession."""

    def __init__(self, path="digital_legacy.jsonl"):
        self.path = Path(path) if path != ":memory:" else path
        self._assets = {}
        self._deeds = {}
        self._transfers = []
        self._next_index = 0
        self._last_hash = GENESIS_HASH

    def __len__(self):
        return len(self._assets)

    def last_hash(self):
        return self._last_hash

    # --- Assets ---

    def register_asset(self, name, asset_type, owner, payload, successor=None, asset_id=None):
        if asset_type not in ASSET_TYPES:
            raise ValueError("Invalid asset type: " + asset_type)
        if not asset_id:
            raw = (name + "|" + asset_type + "|" + owner).encode("utf-8")
            asset_id = "asset:" + hashlib.sha256(raw).hexdigest()[:12]
        a = Asset(
            asset_id=asset_id,
            name=name,
            asset_type=asset_type,
            owner=owner,
            successor=successor,
            content_hash=content_fingerprint(payload),
            registered_at=_now(),
        )
        self._assets[asset_id] = a
        return a

    def get_asset(self, asset_id):
        return self._assets.get(asset_id)

    def assets(self):
        return list(self._assets.values())

    def assets_by_owner(self, owner):
        return [a for a in self._assets.values() if a.owner == owner]

    # --- Deeds ---

    def issue_deed(self, asset_id, signing_key=""):
        """Issue a deed for an asset. Optionally HMAC-signed."""
        a = self._assets.get(asset_id)
        if not a:
            raise ValueError("Unknown asset: " + asset_id)
        raw = (asset_id + "|" + a.owner + "|" + (a.successor or "") + "|" + a.content_hash).encode("utf-8")
        deed_id = "deed:" + hashlib.sha256(raw).hexdigest()[:12]
        issued = _now()
        signature = ""
        if signing_key:
            import hmac
            key = bytes.fromhex(signing_key)
            body = _canonical({
                "deed_id": deed_id, "asset_id": asset_id,
                "owner": a.owner, "successor": a.successor,
                "content_hash": a.content_hash, "issued_at": issued,
            }).encode("utf-8")
            signature = hmac.new(key, body, hashlib.sha256).hexdigest()
        d = Deed(
            deed_id=deed_id,
            asset_id=asset_id,
            owner=a.owner,
            successor=a.successor,
            content_hash=a.content_hash,
            issued_at=issued,
            deed_signature=signature,
        )
        self._deeds[deed_id] = d
        return d

    def deeds(self):
        return list(self._deeds.values())

    def get_deed(self, deed_id):
        return self._deeds.get(deed_id)

    def verify_deed(self, deed_id, payload, signing_key=""):
        """Verify a deed matches the asset payload and (optionally) the signature."""
        d = self._deeds.get(deed_id)
        if not d:
            return {"ok": False, "reason": "unknown_deed"}
        actual = content_fingerprint(payload)
        if actual != d.content_hash:
            return {
                "ok": False,
                "reason": "content_mismatch",
                "expected": d.content_hash,
                "actual": actual,
            }
        if signing_key and d.deed_signature:
            import hmac
            key = bytes.fromhex(signing_key)
            body = _canonical(d.signable()).encode("utf-8")
            expected_sig = hmac.new(key, body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected_sig, d.deed_signature):
                return {"ok": False, "reason": "signature_invalid"}
        return {"ok": True, "deed_id": deed_id}

    # --- Transfers ---

    def transfer(self, asset_id, to_party, reason="succession"):
        """Record a transfer of ownership. Hash-chained."""
        a = self._assets.get(asset_id)
        if not a:
            raise ValueError("Unknown asset: " + asset_id)
        index = self._next_index
        self._next_index += 1
        timestamp = _now()
        rec_dict = {
            "index": index,
            "asset_id": asset_id,
            "from_party": a.owner,
            "to_party": to_party,
            "reason": reason,
            "timestamp": timestamp,
            "prev_hash": self._last_hash,
            "hash": "",
        }
        rec_dict["hash"] = _hash_transfer(rec_dict)
        t = Transfer(**rec_dict)
        self._transfers.append(t)
        self._last_hash = t.hash
        # Update the asset owner
        a.owner = to_party
        return t

    def transfers(self):
        return list(self._transfers)

    def verify_chain(self):
        prev = GENESIS_HASH
        for i, t in enumerate(self._transfers):
            if t.index != i:
                return {"ok": False, "reason": "index mismatch at " + str(i), "at": i}
            if t.prev_hash != prev:
                return {"ok": False, "reason": "prev_hash mismatch at " + str(i), "at": i}
            expected = _hash_transfer(t.to_dict())
            if t.hash != expected:
                return {"ok": False, "reason": "hash mismatch at " + str(i), "at": i}
            prev = t.hash
        return {"ok": True, "length": len(self._transfers), "head": prev}

    # --- Reporting ---

    def legacy_report(self):
        return {
            "total_assets": len(self._assets),
            "total_deeds": len(self._deeds),
            "total_transfers": len(self._transfers),
            "assets_with_successor": sum(1 for a in self._assets.values() if a.successor),
            "assets_by_type": {
                t: sum(1 for a in self._assets.values() if a.asset_type == t)
                for t in ASSET_TYPES
            },
        }

    # --- Persistence ---

    def flush(self):
        if self.path == ":memory:":
            return 0
        with self.path.open("w", encoding="utf-8") as f:
            for a in self._assets.values():
                line = {"__type__": "asset"}
                line.update(a.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
            for d in self._deeds.values():
                line = {"__type__": "deed"}
                line.update(d.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
            for t in self._transfers:
                line = {"__type__": "transfer"}
                line.update(t.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
        return len(self._assets) + len(self._deeds) + len(self._transfers)

    @classmethod
    def load(cls, path):
        reg = cls(path=path)
        p = Path(path)
        if not p.exists():
            return reg
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            typ = data.pop("__type__", None)
            if typ == "asset":
                a = Asset(**data)
                reg._assets[a.asset_id] = a
            elif typ == "deed":
                d = Deed(**data)
                reg._deeds[d.deed_id] = d
            elif typ == "transfer":
                t = Transfer(**data)
                reg._transfers.append(t)
        reg._next_index = len(reg._transfers)
        if reg._transfers:
            reg._last_hash = reg._transfers[-1].hash
        return reg
