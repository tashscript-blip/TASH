"""Tests for the Agent Orchestration module."""

from agent_orchestration import AgentRegistry, Supervisor, Authorization


def make_registry():
    reg = AgentRegistry(path=":memory:")
    sup = reg.register_supervisor(
        name="Test Supervisor",
        email="test@example.com",
        role="PI",
    )
    return reg, sup


def test_register_supervisor():
    reg, sup = make_registry()
    assert isinstance(sup, Supervisor)
    assert sup.name == "Test Supervisor"
    assert sup.supervisor_id.startswith("sup:")
    assert len(reg.supervisors()) == 1


def test_register_agent_requires_known_supervisor():
    reg = AgentRegistry(path=":memory:")
    try:
        reg.register_agent(
            name="A", version="1.0",
            purpose="test", supervisor_id="sup:doesnotexist",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_register_agent():
    reg, sup = make_registry()
    agent = reg.register_agent(
        name="Test Agent",
        version="1.0.0",
        purpose="Testing",
        supervisor_id=sup.supervisor_id,
    )
    assert agent.agent_id.startswith("agent:")
    assert agent.name == "Test Agent"
    assert len(reg.agents()) == 1


def test_wildcard_authorization_allows_all():
    reg, sup = make_registry()
    agent = reg.register_agent(
        name="A", version="1.0", purpose="t",
        supervisor_id=sup.supervisor_id,
        allowed_actions=["*"],
    )
    assert reg.authorize_action(agent.agent_id, "anything") is True
    assert reg.authorize_action(agent.agent_id, "anything_else") is True


def test_scoped_authorization():
    reg, sup = make_registry()
    agent = reg.register_agent(
        name="A", version="1.0", purpose="t",
        supervisor_id=sup.supervisor_id,
        allowed_actions=["read", "write"],
    )
    assert reg.authorize_action(agent.agent_id, "read") is True
    assert reg.authorize_action(agent.agent_id, "write") is True
    assert reg.authorize_action(agent.agent_id, "delete") is False


def test_unknown_agent_denied():
    reg, _ = make_registry()
    assert reg.authorize_action("agent:unknown", "any") is False


def test_rate_limit():
    reg, sup = make_registry()
    agent = reg.register_agent(
        name="A", version="1.0", purpose="t",
        supervisor_id=sup.supervisor_id,
        allowed_actions=["*"],
        max_actions_per_hour=3,
    )
    assert reg.authorize_action(agent.agent_id, "x") is True
    assert reg.authorize_action(agent.agent_id, "x") is True
    assert reg.authorize_action(agent.agent_id, "x") is True
    assert reg.authorize_action(agent.agent_id, "x") is False


def test_audit_report_counts():
    reg, sup = make_registry()
    agent = reg.register_agent(
        name="A", version="1.0", purpose="t",
        supervisor_id=sup.supervisor_id,
        allowed_actions=["read"],
    )
    reg.authorize_action(agent.agent_id, "read")
    reg.authorize_action(agent.agent_id, "read")
    reg.authorize_action(agent.agent_id, "delete")
    report = reg.audit_report()
    stats = report[agent.agent_id]
    assert stats["allowed"] == 2
    assert stats["denied"] == 1
    assert "action_not_in_scope" in stats["deny_reasons"]


def test_flush_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "agents.jsonl")
    reg = AgentRegistry(path=path)
    sup = reg.register_supervisor("S", "s@x.com", "role")
    reg.register_agent(
        name="A", version="1.0", purpose="t",
        supervisor_id=sup.supervisor_id,
        allowed_actions=["read"],
    )
    reg.flush()

    loaded = AgentRegistry.load(path)
    assert len(loaded.supervisors()) == 1
    assert len(loaded.agents()) == 1
    agent = loaded.agents()[0]
    assert agent.authorization.allowed_actions == ["read"]


def test_expired_authorization_denied():
    reg, sup = make_registry()
    agent = reg.register_agent(
        name="A", version="1.0", purpose="t",
        supervisor_id=sup.supervisor_id,
        allowed_actions=["*"],
        valid_until="2020-01-01T00:00:00+00:00",
    )
    assert reg.authorize_action(agent.agent_id, "x") is False
