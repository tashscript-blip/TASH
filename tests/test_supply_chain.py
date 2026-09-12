"""Tests for the Supply Chain Integrity module."""

from supply_chain import (
    SupplyChainRegistry,
    Component,
    Approval,
    COMPONENT_TYPES,
)
from supply_chain.core import fingerprint


def test_component_types():
    assert len(COMPONENT_TYPES) == 5
    assert "model" in COMPONENT_TYPES
    assert "library" in COMPONENT_TYPES


def test_fingerprint_deterministic():
    a = fingerprint({"x": 1, "y": 2})
    b = fingerprint({"y": 2, "x": 1})
    assert a == b
    assert len(a) == 64


def test_fingerprint_accepts_bytes_and_str():
    h1 = fingerprint(b"hello")
    h2 = fingerprint("hello")
    assert h1 == h2


def test_register_component():
    reg = SupplyChainRegistry(path=":memory:")
    c = reg.register_component(
        name="TestLib",
        version="1.0",
        component_type="library",
        source="pypi",
        payload={"sha": "abc"},
    )
    assert isinstance(c, Component)
    assert c.component_id.startswith("cmp:")
    assert c.approval_status == "pending"
    assert c.approved_at is None


def test_register_component_invalid_type():
    reg = SupplyChainRegistry(path=":memory:")
    try:
        reg.register_component(
            name="X", version="1.0",
            component_type="bogus",
            source="x", payload={},
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_register_component_auto_approve():
    reg = SupplyChainRegistry(path=":memory:")
    c = reg.register_component(
        name="X", version="1.0",
        component_type="library",
        source="x", payload={},
        auto_approve=True,
    )
    assert c.approval_status == "approved"
    assert c.approved_at is not None


def test_approve_component():
    reg = SupplyChainRegistry(path=":memory:")
    c = reg.register_component(
        name="X", version="1.0",
        component_type="library",
        source="x", payload={"a": 1},
    )
    approval = reg.approve(c.component_id, "reviewer", "looks good")
    assert isinstance(approval, Approval)
    assert approval.decision == "approved"
    assert reg.get_component(c.component_id).approval_status == "approved"
    assert len(reg.approvals()) == 1


def test_reject_component():
    reg = SupplyChainRegistry(path=":memory:")
    c = reg.register_component(
        name="X", version="1.0",
        component_type="library",
        source="x", payload={"a": 1},
    )
    reg.reject(c.component_id, "reviewer", "untrusted source")
    assert reg.get_component(c.component_id).approval_status == "rejected"


def test_approve_unknown_component():
    reg = SupplyChainRegistry(path=":memory:")
    try:
        reg.approve("cmp:doesnotexist", "reviewer")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_verify_ok():
    reg = SupplyChainRegistry(path=":memory:")
    payload = {"sha": "abc", "size": 100}
    c = reg.register_component(
        name="X", version="1.0",
        component_type="library",
        source="x", payload=payload,
    )
    result = reg.verify(c.component_id, payload)
    assert result["ok"] is True


def test_verify_tamper_detected():
    reg = SupplyChainRegistry(path=":memory:")
    payload = {"sha": "abc", "size": 100}
    c = reg.register_component(
        name="X", version="1.0",
        component_type="library",
        source="x", payload=payload,
    )
    tampered = {"sha": "TAMPERED", "size": 100}
    result = reg.verify(c.component_id, tampered)
    assert result["ok"] is False
    assert result["reason"] == "fingerprint_mismatch"
    assert result["expected"] != result["actual"]


def test_verify_unknown_component():
    reg = SupplyChainRegistry(path=":memory:")
    result = reg.verify("cmp:doesnotexist", {"x": 1})
    assert result["ok"] is False
    assert result["reason"] == "unknown_component"


def test_update_resets_approval():
    reg = SupplyChainRegistry(path=":memory:")
    c = reg.register_component(
        name="X", version="1.0",
        component_type="library",
        source="x", payload={"v": 1},
        auto_approve=True,
    )
    assert c.approval_status == "approved"
    reg.update_component(c.component_id, {"v": 2}, new_version="1.1")
    updated = reg.get_component(c.component_id)
    assert updated.approval_status == "pending"
    assert updated.approved_at is None
    assert updated.version == "1.1"


def test_integrity_report():
    reg = SupplyChainRegistry(path=":memory:")
    c1 = reg.register_component(
        "A", "1.0", "library", "src", {"a": 1},
        auto_approve=True,
    )
    c2 = reg.register_component(
        "B", "1.0", "model", "src", {"b": 2},
    )
    reg.verify(c1.component_id, {"a": 1})
    reg.verify(c2.component_id, {"b": "wrong"})

    report = reg.integrity_report()
    assert report["total_components"] == 2
    assert report["by_status"]["approved"] == 1
    assert report["by_status"]["pending"] == 1
    assert report["verify_ok"] == 1
    assert report["verify_fail"] == 1
    assert report["pending_critical"] == 1


def test_flush_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "sc.jsonl")
    reg = SupplyChainRegistry(path=path)
    c = reg.register_component(
        name="Persist", version="1.0",
        component_type="model",
        source="x", payload={"k": "v"},
    )
    reg.approve(c.component_id, "rev", "ok")
    reg.verify(c.component_id, {"k": "v"})
    reg.flush()

    loaded = SupplyChainRegistry.load(path)
    assert len(loaded.components()) == 1
    assert len(loaded.approvals()) == 1
    assert loaded.components()[0].approval_status == "approved"
    assert loaded.event_log()  # events preserved
