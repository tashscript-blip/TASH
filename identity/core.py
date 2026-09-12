"""
core.py - Machine identity and cryptographic action signing.

Every agent has a machine identity with a secret key. Every action
is signed by that identity. Signatures can be verified independently,
providing a cryptographic "machine identity trail for every automated
action" (Article V: Identity Governance).

Security note: for the standalone demo, keys are persisted alongside
identities. Production deployments should store keys in a hardware
security module or managed key vault.
"""

import hashlib
import hmac
import json
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _now():
    return datetime.now(timezone.utc).isoformat()


def _canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def generate_key():
    """Generate a 32-byte secret key, returned as a hex string."""
    return secrets.token_hex(32)


def sign(key_hex, message):
    """HMAC-SHA256 signature of a canonical message."""
    key = bytes.fromhex(key_hex)
    body = _canonical(message).encode("utf-8")
    return hmac.new(key, body, hashlib.sha256).hexdigest()


def verify_signature(key_hex, message, signature):
    """Verify an HMAC-SHA256 signature with constant-time comparison."""
    expected = sign(key_hex, message)
    return hmac.compare_digest(expected, signature)


@dataclass
class MachineIdentity:
    """A non-human identity that can sign actions."""
    identity_id: str
    name: str
    role: str
    created_at: str
    public_fingerprint: str
    active: bool = True

    def to_dict(self):
        return asdict(self)


@dataclass
class SignedAction:
    """An action signed by a machine identity."""
    identity_id: str
    action: str
    payload: Dict[str, Any]
    timestamp: str
    signature: str

    def to_dict(self):
        return asdict(self)

    def signable(self):
        return {
            "identity_id": self.identity_id,
            "action": self.action,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


class IdentityRegistry:
    """Registry of machine identities and their signed action trail."""

    def __init__(self, path="identities.jsonl"):
        self.path = Path(path) if path != ":memory:" else path
        self._identities = {}
        self._keys = {}
        self._actions = []

    def register(self, name, role, identity_id=None):
        if not identity_id:
            raw = (name + "|" + role + "|" + secrets.token_hex(8)).encode("utf-8")
            identity_id = "id:" + hashlib.sha256(raw).hexdigest()[:12]
        key_hex = generate_key()
        fingerprint = hashlib.sha256(key_hex.encode("utf-8")).hexdigest()
        ident = MachineIdentity(
            identity_id=identity_id,
            name=name,
            role=role,
            created_at=_now(),
            public_fingerprint=fingerprint,
            active=True,
        )
        self._identities[identity_id] = ident
        self._keys[identity_id] = key_hex
        return ident

    def get(self, identity_id):
        return self._identities.get(identity_id)

    def identities(self):
        return list(self._identities.values())

    def revoke(self, identity_id):
        ident = self._identities.get(identity_id)
        if ident:
            ident.active = False
        return ident

    def sign_action(self, identity_id, action, payload=None):
        if identity_id not in self._identities:
            raise ValueError("Unknown identity: " + identity_id)
        if not self._identities[identity_id].active:
            raise ValueError("Identity is revoked: " + identity_id)
        signed = SignedAction(
            identity_id=identity_id,
            action=action,
            payload=payload or {},
            timestamp=_now(),
            signature="",
        )
        signed.signature = sign(self._keys[identity_id], signed.signable())
        self._actions.append(signed)
        return signed

    def verify_action(self, signed):
        key_hex = self._keys.get(signed.identity_id)
        if not key_hex:
            return False
        return verify_signature(key_hex, signed.signable(), signed.signature)

    def actions(self):
        return list(self._actions)

    def verify_all(self):
        return all(self.verify_action(a) for a in self._actions)

    def flush(self):
        if self.path == ":memory:":
            return 0
        with self.path.open("w", encoding="utf-8") as f:
            for ident in self._identities.values():
                line = {"__type__": "identity"}
                line.update(ident.to_dict())
                key_hex = self._keys.get(ident.identity_id)
                if key_hex:
                    # DEV ONLY: production systems use HSM/KMS.
                    line["_dev_key_hex"] = key_hex
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
            for a in self._actions:
                line = {"__type__": "action"}
                line.update(a.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
        return len(self._identities) + len(self._actions)

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
            if typ == "identity":
                key_hex = data.pop("_dev_key_hex", None)
                ident = MachineIdentity(**data)
                reg._identities[ident.identity_id] = ident
                if key_hex:
                    reg._keys[ident.identity_id] = key_hex
            elif typ == "action":
                reg._actions.append(SignedAction(**data))
        return reg
