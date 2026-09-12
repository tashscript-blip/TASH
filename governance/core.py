"""
core.py - Governance & Risk Orchestration.

Registers controls (mapped to the Eight-Domain Stack), registers risks
tied to those controls, and produces auditable risk decisions that
include the evidence used.

The coverage_report() method shows which of the eight compliance
domains have implemented controls and which are on the roadmap.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DOMAINS = [
    "governance_risk",
    "ai_discovery",
    "agent_orchestration",
    "dspm_lineage",
    "identity_governance",
    "runtime_protection",
    "supply_chain",
    "digital_legacy",
]

SEVERITIES = ["low", "medium", "high", "critical"]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def _hash(data):
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


@dataclass
class Control:
    """A compliance control mapped to one of the eight domains."""
    control_id: str
    name: str
    domain: str
    description: str
    status: str  # "implemented", "partial", "planned"
    registered_at: str = ""

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = _now()

    def to_dict(self):
        return asdict(self)


@dataclass
class Risk:
    """A risk tied to one or more controls."""
    risk_id: str
    title: str
    severity: str
    likelihood: str
    domain: str
    control_ids: List[str] = field(default_factory=list)
    registered_at: str = ""

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = _now()
        if self.severity not in SEVERITIES:
            raise ValueError("Invalid severity: " + self.severity)

    def to_dict(self):
        return asdict(self)


@dataclass
class RiskDecision:
    """An auditable decision about a risk."""
    risk_id: str
    decision: str  # "mitigated", "accepted", "escalated"
    evidence: Dict[str, Any]
    timestamp: str
    signature: str

    def to_dict(self):
        return asdict(self)

    def signable(self):
        return {
            "risk_id": self.risk_id,
            "decision": self.decision,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
        }


class GovernanceOrchestrator:
    """Risk register with controls and auditable decisions."""

    def __init__(self, path="governance.jsonl"):
        self.path = Path(path) if path != ":memory:" else path
        self._controls = {}
        self._risks = {}
        self._decisions = []

    # --- Controls ---

    def register_control(self, name, domain, description, status="implemented", control_id=None):
        if domain not in DOMAINS:
            raise ValueError("Unknown domain: " + domain)
        if status not in ("implemented", "partial", "planned"):
            raise ValueError("Invalid status: " + status)
        if not control_id:
            raw = (name + "|" + domain).encode("utf-8")
            control_id = "ctl:" + hashlib.sha256(raw).hexdigest()[:10]
        ctl = Control(
            control_id=control_id, name=name, domain=domain,
            description=description, status=status,
        )
        self._controls[control_id] = ctl
        return ctl

    def controls(self):
        return list(self._controls.values())

    def controls_for_domain(self, domain):
        return [c for c in self._controls.values() if c.domain == domain]

    # --- Risks ---

    def register_risk(self, title, severity, likelihood, domain, control_ids=None, risk_id=None):
        if domain not in DOMAINS:
            raise ValueError("Unknown domain: " + domain)
        if not risk_id:
            raw = (title + "|" + domain + "|" + severity).encode("utf-8")
            risk_id = "risk:" + hashlib.sha256(raw).hexdigest()[:10]
        risk = Risk(
            risk_id=risk_id, title=title, severity=severity,
            likelihood=likelihood, domain=domain,
            control_ids=control_ids or [],
        )
        self._risks[risk_id] = risk
        return risk

    def risks(self):
        return list(self._risks.values())

    # --- Decisions ---

    def decide(self, risk_id, decision, evidence=None, signing_key=""):
        if decision not in ("mitigated", "accepted", "escalated"):
            raise ValueError("Invalid decision: " + decision)
        if risk_id not in self._risks:
            raise ValueError("Unknown risk: " + risk_id)
        timestamp = _now()
        sig = ""
        if signing_key:
            import hmac
            key = bytes.fromhex(signing_key)
            body = _canonical({
                "risk_id": risk_id, "decision": decision,
                "evidence": evidence or {}, "timestamp": timestamp,
            }).encode("utf-8")
            sig = hmac.new(key, body, hashlib.sha256).hexdigest()
        d = RiskDecision(
            risk_id=risk_id, decision=decision,
            evidence=evidence or {}, timestamp=timestamp, signature=sig,
        )
        self._decisions.append(d)
        return d

    def decisions(self):
        return list(self._decisions)

    # --- Reporting ---

    def coverage_report(self):
        """Report which domains have implemented controls."""
        report = {}
        for dom in DOMAINS:
            ctls = self.controls_for_domain(dom)
            implemented = [c for c in ctls if c.status == "implemented"]
            partial = [c for c in ctls if c.status == "partial"]
            planned = [c for c in ctls if c.status == "planned"]
            report[dom] = {
                "total": len(ctls),
                "implemented": len(implemented),
                "partial": len(partial),
                "planned": len(planned),
                "coverage": "full" if implemented and not (partial or planned)
                            else "partial" if implemented
                            else "roadmap",
            }
        return report

    def risk_summary(self):
        """Summary of risks by severity and decision."""
        summary = {s: {"total": 0, "mitigated": 0, "accepted": 0, "escalated": 0}
                   for s in SEVERITIES}
        for r in self._risks.values():
            summary[r.severity]["total"] += 1
        for d in self._decisions:
            r = self._risks.get(d.risk_id)
            if r:
                summary[r.severity][d.decision] += 1
        return summary

    # --- Persistence ---

    def flush(self):
        if self.path == ":memory:":
            return 0
        with self.path.open("w", encoding="utf-8") as f:
            for c in self._controls.values():
                line = {"__type__": "control"}
                line.update(c.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
            for r in self._risks.values():
                line = {"__type__": "risk"}
                line.update(r.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
            for d in self._decisions:
                line = {"__type__": "decision"}
                line.update(d.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
        return len(self._controls) + len(self._risks) + len(self._decisions)

    @classmethod
    def load(cls, path):
        obj = cls(path=path)
        p = Path(path)
        if not p.exists():
            return obj
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            typ = data.pop("__type__", None)
            if typ == "control":
                c = Control(**data)
                obj._controls[c.control_id] = c
            elif typ == "risk":
                r = Risk(**data)
                obj._risks[r.risk_id] = r
            elif typ == "decision":
                obj._decisions.append(RiskDecision(**data))
        return obj
