"""
core.py - AI Discovery & Security Posture.

Maintains a live inventory of AI models and vendors used by the system,
classifies each by risk (per NIST AI RMF), and produces a security
posture report suitable for federal review.

Risk classes (NIST AI RMF):
  minimal       - no or minimal harm potential
  limited       - some harm potential, transparency required
  high          - significant harm potential, strict controls required
  unacceptable  - prohibited use
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


RISK_CLASSES = ["minimal", "limited", "high", "unacceptable"]
VENDOR_STATUS = ["unverified", "verified", "suspended"]


def _now():
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Vendor:
    """A vendor providing AI or infrastructure services."""
    vendor_id: str
    name: str
    country: str
    services: List[str] = field(default_factory=list)
    verification_status: str = "unverified"
    registered_at: str = ""

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = _now()
        if self.verification_status not in VENDOR_STATUS:
            raise ValueError("Invalid vendor status: " + self.verification_status)

    def to_dict(self):
        return asdict(self)


@dataclass
class AIModel:
    """An AI model integrated into the system."""
    model_id: str
    name: str
    provider: str
    version: str
    purpose: str
    risk_class: str
    deployment_scope: str
    vendor_id: Optional[str] = None
    registered_at: str = ""

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = _now()
        if self.risk_class not in RISK_CLASSES:
            raise ValueError("Invalid risk class: " + self.risk_class)

    def to_dict(self):
        return asdict(self)


class AIDiscoveryRegistry:
    """Live inventory of AI models and vendors."""

    def __init__(self, path="ai_discovery.jsonl"):
        self.path = Path(path) if path != ":memory:" else path
        self._vendors = {}
        self._models = {}

    # --- Vendors ---

    def register_vendor(self, name, country, services=None, verification_status="unverified", vendor_id=None):
        if verification_status not in VENDOR_STATUS:
            raise ValueError("Invalid vendor status: " + verification_status)
        if not vendor_id:
            raw = (name + "|" + country).encode("utf-8")
            vendor_id = "vendor:" + hashlib.sha256(raw).hexdigest()[:10]
        v = Vendor(
            vendor_id=vendor_id,
            name=name,
            country=country,
            services=services or [],
            verification_status=verification_status,
        )
        self._vendors[vendor_id] = v
        return v

    def vendors(self):
        return list(self._vendors.values())

    def get_vendor(self, vendor_id):
        return self._vendors.get(vendor_id)

    def set_vendor_status(self, vendor_id, status):
        if status not in VENDOR_STATUS:
            raise ValueError("Invalid status: " + status)
        v = self._vendors.get(vendor_id)
        if v:
            v.verification_status = status
        return v

    # --- Models ---

    def register_model(self, name, provider, version, purpose, risk_class, deployment_scope, vendor_id=None, model_id=None):
        if risk_class not in RISK_CLASSES:
            raise ValueError("Invalid risk class: " + risk_class)
        if vendor_id is not None and vendor_id not in self._vendors:
            raise ValueError("Unknown vendor: " + vendor_id)
        if not model_id:
            raw = (name + "|" + provider + "|" + version).encode("utf-8")
            model_id = "model:" + hashlib.sha256(raw).hexdigest()[:10]
        m = AIModel(
            model_id=model_id,
            name=name,
            provider=provider,
            version=version,
            purpose=purpose,
            risk_class=risk_class,
            deployment_scope=deployment_scope,
            vendor_id=vendor_id,
        )
        self._models[model_id] = m
        return m

    def models(self):
        return list(self._models.values())

    def get_model(self, model_id):
        return self._models.get(model_id)

    def models_by_risk(self, risk_class):
        return [m for m in self._models.values() if m.risk_class == risk_class]

    # --- Reporting ---

    def inventory_report(self):
        """Full inventory of models and vendors."""
        return {
            "model_count": len(self._models),
            "vendor_count": len(self._vendors),
            "models_by_risk": {
                rc: len(self.models_by_risk(rc)) for rc in RISK_CLASSES
            },
            "vendors_by_status": {
                st: sum(1 for v in self._vendors.values() if v.verification_status == st)
                for st in VENDOR_STATUS
            },
        }

    def security_posture(self):
        """
        Posture score based on:
          - Percentage of high/unacceptable-risk models with a verified vendor
          - Percentage of vendors verified
          - Absence of unacceptable-risk models
        """
        findings = []
        score = 1.0

        # Unacceptable-risk models are prohibited
        unacc = self.models_by_risk("unacceptable")
        if unacc:
            score -= 0.5
            findings.append({
                "severity": "critical",
                "message": str(len(unacc)) + " unacceptable-risk model(s) present",
            })

        # High-risk models should have a verified vendor
        high_risk = self.models_by_risk("high")
        unverified_high = [
            m for m in high_risk
            if not m.vendor_id
            or self._vendors.get(m.vendor_id, Vendor("", "", "", verification_status="unverified")).verification_status != "verified"
        ]
        if high_risk:
            ratio = 1.0 - (len(unverified_high) / len(high_risk))
            score -= (1.0 - ratio) * 0.3
            if unverified_high:
                findings.append({
                    "severity": "high",
                    "message": str(len(unverified_high)) + " high-risk model(s) with unverified vendor",
                })

        # Overall vendor verification
        if self._vendors:
            verified = sum(1 for v in self._vendors.values()
                           if v.verification_status == "verified")
            ratio = verified / len(self._vendors)
            score -= (1.0 - ratio) * 0.2
            if verified < len(self._vendors):
                findings.append({
                    "severity": "medium",
                    "message": str(len(self._vendors) - verified) + " unverified vendor(s)",
                })

        score = max(0.0, round(score, 2))
        if score >= 0.9:
            posture = "strong"
        elif score >= 0.7:
            posture = "adequate"
        elif score >= 0.5:
            posture = "weak"
        else:
            posture = "critical"

        return {
            "posture": posture,
            "score": score,
            "findings": findings,
        }

    # --- Persistence ---

    def flush(self):
        if self.path == ":memory:":
            return 0
        with self.path.open("w", encoding="utf-8") as f:
            for v in self._vendors.values():
                line = {"__type__": "vendor"}
                line.update(v.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
            for m in self._models.values():
                line = {"__type__": "model"}
                line.update(m.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
        return len(self._vendors) + len(self._models)

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
            if typ == "vendor":
                v = Vendor(**data)
                reg._vendors[v.vendor_id] = v
            elif typ == "model":
                m = AIModel(**data)
                reg._models[m.model_id] = m
        return reg
