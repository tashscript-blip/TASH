"""
core.py - Supply Chain Integrity.

Every third-party component (model, library, vendor artifact) is
registered with a cryptographic fingerprint. Any update changes the
fingerprint and requires explicit re-approval. The verify() method
detects any silent modification.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


COMPONENT_TYPES = [
    "model",
    "library",
    "vendor_artifact",
    "dataset",
    "container_image",
]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def fingerprint(data):
    """SHA-256 fingerprint of a component payload."""
    if isinstance(data, bytes):
        raw = data
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    else:
        raw = _canonical(data).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass
class Component:
    """A registered third-party component."""
    component_id: str
    name: str
    version: str
    component_type: str
    source: str
    fingerprint: str
    approval_status: str  # "approved", "pending", "rejected"
    registered_at: str
    approved_at: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Approval:
    """An approval or rejection event for a component."""
    component_id: str
    decision: str  # "approved", "rejected"
    reviewer: str
    reason: str
    timestamp: str

    def to_dict(self):
        return asdict(self)


class SupplyChainRegistry:
    """Registry of third-party components with integrity verification."""

    def __init__(self, path="supply_chain.jsonl"):
        self.path = Path(path) if path != ":memory:" else path
        self._components = {}
        self._approvals = []
        self._event_log = []

    def register_component(self, name, version, component_type, source,
                           payload, component_id=None, auto_approve=False):
        """Register a new component with its content fingerprint."""
        if component_type not in COMPONENT_TYPES:
            raise ValueError("Invalid component type: " + component_type)
        if not component_id:
            raw = (name + "|" + version + "|" + component_type).encode("utf-8")
            component_id = "cmp:" + hashlib.sha256(raw).hexdigest()[:12]

        fp = fingerprint(payload)
        status = "approved" if auto_approve else "pending"
        approved_at = _now() if auto_approve else None

        c = Component(
            component_id=component_id,
            name=name,
            version=version,
            component_type=component_type,
            source=source,
            fingerprint=fp,
            approval_status=status,
            registered_at=_now(),
            approved_at=approved_at,
        )
        self._components[component_id] = c
        self._event_log.append({
            "event": "register",
            "component_id": component_id,
            "timestamp": _now(),
            "fingerprint": fp,
        })
        return c

    def get_component(self, component_id):
        return self._components.get(component_id)

    def components(self):
        return list(self._components.values())

    def components_by_type(self, component_type):
        return [c for c in self._components.values() if c.component_type == component_type]

    def approve(self, component_id, reviewer, reason=""):
        c = self._components.get(component_id)
        if not c:
            raise ValueError("Unknown component: " + component_id)
        c.approval_status = "approved"
        c.approved_at = _now()
        approval = Approval(
            component_id=component_id,
            decision="approved",
            reviewer=reviewer,
            reason=reason,
            timestamp=_now(),
        )
        self._approvals.append(approval)
        self._event_log.append({
            "event": "approve",
            "component_id": component_id,
            "reviewer": reviewer,
            "timestamp": _now(),
        })
        return approval

    def reject(self, component_id, reviewer, reason=""):
        c = self._components.get(component_id)
        if not c:
            raise ValueError("Unknown component: " + component_id)
        c.approval_status = "rejected"
        approval = Approval(
            component_id=component_id,
            decision="rejected",
            reviewer=reviewer,
            reason=reason,
            timestamp=_now(),
        )
        self._approvals.append(approval)
        self._event_log.append({
            "event": "reject",
            "component_id": component_id,
            "reviewer": reviewer,
            "timestamp": _now(),
        })
        return approval

    def verify(self, component_id, payload):
        """Verify that a payload matches the registered fingerprint."""
        c = self._components.get(component_id)
        if not c:
            return {"ok": False, "reason": "unknown_component"}
        actual = fingerprint(payload)
        if actual != c.fingerprint:
            self._event_log.append({
                "event": "verify_fail",
                "component_id": component_id,
                "timestamp": _now(),
                "expected": c.fingerprint,
                "actual": actual,
            })
            return {
                "ok": False,
                "reason": "fingerprint_mismatch",
                "expected": c.fingerprint,
                "actual": actual,
            }
        self._event_log.append({
            "event": "verify_ok",
            "component_id": component_id,
            "timestamp": _now(),
        })
        return {"ok": True, "fingerprint": actual}

    def update_component(self, component_id, new_payload, new_version=None):
        """Register a new payload for an existing component. Resets approval."""
        c = self._components.get(component_id)
        if not c:
            raise ValueError("Unknown component: " + component_id)
        new_fp = fingerprint(new_payload)
        old_fp = c.fingerprint
        c.fingerprint = new_fp
        if new_version:
            c.version = new_version
        c.approval_status = "pending"
        c.approved_at = None
        self._event_log.append({
            "event": "update",
            "component_id": component_id,
            "timestamp": _now(),
            "old_fingerprint": old_fp,
            "new_fingerprint": new_fp,
        })
        return c

    def approvals(self):
        return list(self._approvals)

    def event_log(self):
        return list(self._event_log)

    def integrity_report(self):
        """Summary of component approval status."""
        by_status = {"approved": 0, "pending": 0, "rejected": 0}
        for c in self._components.values():
            by_status[c.approval_status] = by_status.get(c.approval_status, 0) + 1
        by_type = {}
        for ct in COMPONENT_TYPES:
            by_type[ct] = len(self.components_by_type(ct))
        verify_fails = sum(
            1 for e in self._event_log if e.get("event") == "verify_fail"
        )
        verify_oks = sum(
            1 for e in self._event_log if e.get("event") == "verify_ok"
        )
        pending_high = [
            c for c in self._components.values()
            if c.approval_status == "pending" and c.component_type in ("model", "vendor_artifact")
        ]
        return {
            "total_components": len(self._components),
            "by_status": by_status,
            "by_type": by_type,
            "verify_ok": verify_oks,
            "verify_fail": verify_fails,
            "pending_critical": len(pending_high),
        }

    def flush(self):
        if self.path == ":memory:":
            return 0
        with self.path.open("w", encoding="utf-8") as f:
            for c in self._components.values():
                line = {"__type__": "component"}
                line.update(c.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
            for a in self._approvals:
                line = {"__type__": "approval"}
                line.update(a.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
            for e in self._event_log:
                line = {"__type__": "event"}
                line.update(e)
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
        return len(self._components) + len(self._approvals) + len(self._event_log)

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
            if typ == "component":
                c = Component(**data)
                reg._components[c.component_id] = c
            elif typ == "approval":
                reg._approvals.append(Approval(**data))
            elif typ == "event":
                reg._event_log.append(data)
        return reg
