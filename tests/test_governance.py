"""Tests for the Governance & Risk Orchestration module."""

from governance import (
    GovernanceOrchestrator,
    Control,
    Risk,
    RiskDecision,
    DOMAINS,
)


def test_domains_list():
    assert len(DOMAINS) == 8
    assert "runtime_protection" in DOMAINS
    assert "identity_governance" in DOMAINS
    assert "dspm_lineage" in DOMAINS


def test_register_control():
    gov = GovernanceOrchestrator(path=":memory:")
    ctl = gov.register_control(
        name="Test Control",
        domain="runtime_protection",
        description="Test",
        status="implemented",
    )
    assert isinstance(ctl, Control)
    assert ctl.control_id.startswith("ctl:")
    assert ctl.status == "implemented"
    assert len(gov.controls()) == 1


def test_register_control_invalid_domain():
    gov = GovernanceOrchestrator(path=":memory:")
    try:
        gov.register_control("x", "not_a_domain", "y")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_register_control_invalid_status():
    gov = GovernanceOrchestrator(path=":memory:")
    try:
        gov.register_control("x", "runtime_protection", "y", status="bad_status")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_register_risk():
    gov = GovernanceOrchestrator(path=":memory:")
    risk = gov.register_risk(
        title="Test Risk",
        severity="high",
        likelihood="medium",
        domain="runtime_protection",
    )
    assert isinstance(risk, Risk)
    assert risk.risk_id.startswith("risk:")
    assert risk.severity == "high"
    assert len(gov.risks()) == 1


def test_register_risk_invalid_severity():
    gov = GovernanceOrchestrator(path=":memory:")
    try:
        gov.register_risk("x", "extreme", "low", "runtime_protection")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_decide_mitigated():
    gov = GovernanceOrchestrator(path=":memory:")
    risk = gov.register_risk("x", "high", "medium", "runtime_protection")
    d = gov.decide(risk.risk_id, "mitigated", {"control": "ctl:1"})
    assert isinstance(d, RiskDecision)
    assert d.decision == "mitigated"
    assert d.evidence == {"control": "ctl:1"}


def test_decide_invalid_decision():
    gov = GovernanceOrchestrator(path=":memory:")
    risk = gov.register_risk("x", "high", "medium", "runtime_protection")
    try:
        gov.decide(risk.risk_id, "ignored")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_decide_unknown_risk():
    gov = GovernanceOrchestrator(path=":memory:")
    try:
        gov.decide("risk:doesnotexist", "mitigated")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_coverage_report():
    gov = GovernanceOrchestrator(path=":memory:")
    gov.register_control("a", "runtime_protection", "d", status="implemented")
    gov.register_control("b", "dspm_lineage", "d", status="implemented")
    gov.register_control("c", "supply_chain", "d", status="planned")

    report = gov.coverage_report()
    assert report["runtime_protection"]["coverage"] == "full"
    assert report["dspm_lineage"]["coverage"] == "full"
    assert report["supply_chain"]["coverage"] == "roadmap"
    assert report["identity_governance"]["coverage"] == "roadmap"


def test_risk_summary():
    gov = GovernanceOrchestrator(path=":memory:")
    r1 = gov.register_risk("r1", "high", "medium", "runtime_protection")
    r2 = gov.register_risk("r2", "low", "high", "supply_chain")
    gov.decide(r1.risk_id, "mitigated")
    gov.decide(r2.risk_id, "accepted")

    summary = gov.risk_summary()
    assert summary["high"]["total"] == 1
    assert summary["high"]["mitigated"] == 1
    assert summary["low"]["total"] == 1
    assert summary["low"]["accepted"] == 1


def test_flush_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "gov.jsonl")
    gov = GovernanceOrchestrator(path=path)
    ctl = gov.register_control(
        "Test", "runtime_protection", "desc", status="implemented"
    )
    risk = gov.register_risk(
        "Risk", "high", "medium", "runtime_protection",
        control_ids=[ctl.control_id],
    )
    gov.decide(risk.risk_id, "mitigated", {"evidence": "test"})
    gov.flush()

    loaded = GovernanceOrchestrator.load(path)
    assert len(loaded.controls()) == 1
    assert len(loaded.risks()) == 1
    assert len(loaded.decisions()) == 1
    assert loaded.risks()[0].control_ids == [ctl.control_id]
