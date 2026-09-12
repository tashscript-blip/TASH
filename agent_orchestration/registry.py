"""
registry.py - Agent Orchestration registry.

Tracks agents, their human supervisors, and their authorization scope.
Every action attempt is logged (allowed or denied), producing an audit
report for federal compliance review.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Supervisor:
    """A human overseer who authorizes an agent."""
    supervisor_id: str
    name: str
    email: str
    role: str
    registered_at: str = ""

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return asdict(self)


@dataclass
class Authorization:
    """Scoped authorization for an agent."""
    allowed_actions: List[str] = field(default_factory=list)
    max_actions_per_hour: int = 1000
    valid_from: str = ""
    valid_until: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    def allows(self, action):
        if not self.allowed_actions or "*" in self.allowed_actions:
            return True
        return action in self.allowed_actions

    def is_currently_valid(self, now=None):
        now = now or datetime.now(timezone.utc)
        if self.valid_from:
            try:
                if now < datetime.fromisoformat(self.valid_from):
                    return False
            except Exception:
                pass
        if self.valid_until:
            try:
                if now > datetime.fromisoformat(self.valid_until):
                    return False
            except Exception:
                pass
        return True


@dataclass
class AgentRegistration:
    """A registered AI agent with its supervisor and authorization."""
    agent_id: str
    name: str
    version: str
    purpose: str
    supervisor_id: str
    authorization: Authorization
    registered_at: str

    def to_dict(self):
        d = asdict(self)
        d["authorization"] = self.authorization.to_dict()
        return d


class AgentRegistry:
    """Registry of agents, supervisors, and authorizations."""

    def __init__(self, path="agents.jsonl"):
        self.path = Path(path) if path != ":memory:" else path
        self._supervisors = {}
        self._agents = {}
        self._action_log = []

    def register_supervisor(self, name, email, role, supervisor_id=None):
        if not supervisor_id:
            raw = (name + "|" + email).encode("utf-8")
            supervisor_id = "sup:" + hashlib.sha256(raw).hexdigest()[:12]
        sup = Supervisor(
            supervisor_id=supervisor_id,
            name=name, email=email, role=role
        )
        self._supervisors[supervisor_id] = sup
        return sup

    def get_supervisor(self, supervisor_id):
        return self._supervisors.get(supervisor_id)

    def supervisors(self):
        return list(self._supervisors.values())

    def register_agent(self, name, version, purpose, supervisor_id,
                       allowed_actions=None, max_actions_per_hour=1000,
                       valid_until=None, agent_id=None):
        if supervisor_id not in self._supervisors:
            raise ValueError("Unknown supervisor: " + supervisor_id)
        if not agent_id:
            raw = (name + "|" + version + "|" + supervisor_id).encode("utf-8")
            agent_id = "agent:" + hashlib.sha256(raw).hexdigest()[:12]
        auth = Authorization(
            allowed_actions=allowed_actions or ["*"],
            max_actions_per_hour=max_actions_per_hour,
            valid_from=datetime.now(timezone.utc).isoformat(),
            valid_until=valid_until,
        )
        reg = AgentRegistration(
            agent_id=agent_id,
            name=name, version=version, purpose=purpose,
            supervisor_id=supervisor_id,
            authorization=auth,
            registered_at=datetime.now(timezone.utc).isoformat(),
        )
        self._agents[agent_id] = reg
        return reg

    def get_agent(self, agent_id):
        return self._agents.get(agent_id)

    def agents(self):
        return list(self._agents.values())

    def authorize_action(self, agent_id, action):
        """Check if agent is authorized; log the attempt."""
        agent = self._agents.get(agent_id)
        timestamp = datetime.now(timezone.utc).isoformat()

        if not agent:
            self._action_log.append({
                "agent_id": agent_id, "action": action,
                "timestamp": timestamp, "allowed": False,
                "reason": "unknown_agent",
            })
            return False

        if not agent.authorization.is_currently_valid():
            self._action_log.append({
                "agent_id": agent_id, "action": action,
                "timestamp": timestamp, "allowed": False,
                "reason": "expired_or_not_yet_valid",
            })
            return False

        if not agent.authorization.allows(action):
            self._action_log.append({
                "agent_id": agent_id, "action": action,
                "timestamp": timestamp, "allowed": False,
                "reason": "action_not_in_scope",
            })
            return False

        allowed_count = sum(
            1 for x in self._action_log
            if x["agent_id"] == agent_id and x["allowed"]
        )
        if allowed_count >= agent.authorization.max_actions_per_hour:
            self._action_log.append({
                "agent_id": agent_id, "action": action,
                "timestamp": timestamp, "allowed": False,
                "reason": "rate_limit_exceeded",
            })
            return False

        self._action_log.append({
            "agent_id": agent_id, "action": action,
            "timestamp": timestamp, "allowed": True,
            "reason": "authorized",
        })
        return True

    def action_log(self):
        return list(self._action_log)

    def audit_report(self):
        """Summary of all action attempts per agent."""
        report = {}
        for entry in self._action_log:
            aid = entry["agent_id"]
            if aid not in report:
                report[aid] = {"allowed": 0, "denied": 0, "deny_reasons": []}
            if entry["allowed"]:
                report[aid]["allowed"] += 1
            else:
                report[aid]["denied"] += 1
                report[aid]["deny_reasons"].append(entry.get("reason", "unknown"))
        return report

    def flush(self):
        if self.path == ":memory:":
            return 0
        count = 0
        with self.path.open("w", encoding="utf-8") as f:
            for sup in self._supervisors.values():
                line = {"__type__": "supervisor"}
                line.update(sup.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
                count += 1
            for ag in self._agents.values():
                line = {"__type__": "agent"}
                line.update(ag.to_dict())
                f.write(json.dumps(line, sort_keys=True, default=str) + "\n")
                count += 1
        return count

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
            if typ == "supervisor":
                reg._supervisors[data["supervisor_id"]] = Supervisor(**data)
            elif typ == "agent":
                auth_data = data.pop("authorization", {})
                auth = Authorization(**auth_data)
                data["authorization"] = auth
                reg._agents[data["agent_id"]] = AgentRegistration(**data)
        return reg
