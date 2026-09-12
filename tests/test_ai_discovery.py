"""Tests for the AI Discovery & Security Posture module."""

from ai_discovery import (
    AIDiscoveryRegistry,
    AIModel,
    Vendor,
    RISK_CLASSES,
)


def test_risk_classes():
    assert len(RISK_CLASSES) == 4
    assert "high" in RISK_CLASSES
    assert "unacceptable" in RISK_CLASSES


def test_register_vendor():
    reg = AIDiscoveryRegistry(path=":memory:")
    v = reg.register_vendor(
        name="Test Vendor",
        country="US",
        services=["api"],
        verification_status="verified",
    )
    assert isinstance(v, Vendor)
    assert v.vendor_id.startswith("vendor:")
    assert v.verification_status == "verified"
    assert len(reg.vendors()) == 1


def test_register_vendor_invalid_status():
    reg = AIDiscoveryRegistry(path=":memory:")
    try:
        reg.register_vendor("X", "US", verification_status="bogus")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_set_vendor_status():
    reg = AIDiscoveryRegistry(path=":memory:")
    v = reg.register_vendor("X", "US")
    reg.set_vendor_status(v.vendor_id, "verified")
    assert reg.get_vendor(v.vendor_id).verification_status == "verified"


def test_register_model():
    reg = AIDiscoveryRegistry(path=":memory:")
    m = reg.register_model(
        name="M", provider="P", version="1.0",
        purpose="test", risk_class="limited",
        deployment_scope="internal",
    )
    assert isinstance(m, AIModel)
    assert m.model_id.startswith("model:")
    assert m.risk_class == "limited"
    assert len(reg.models()) == 1


def test_register_model_invalid_risk():
    reg = AIDiscoveryRegistry(path=":memory:")
    try:
        reg.register_model(
            name="M", provider="P", version="1.0",
            purpose="t", risk_class="bogus",
            deployment_scope="internal",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_register_model_unknown_vendor():
    reg = AIDiscoveryRegistry(path=":memory:")
    try:
        reg.register_model(
            name="M", provider="P", version="1.0",
            purpose="t", risk_class="limited",
            deployment_scope="internal",
            vendor_id="vendor:doesnotexist",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_models_by_risk():
    reg = AIDiscoveryRegistry(path=":memory:")
    reg.register_model("a", "p", "1", "t", "minimal", "internal")
    reg.register_model("b", "p", "1", "t", "high", "internal")
    reg.register_model("c", "p", "1", "t", "high", "internal")
    assert len(reg.models_by_risk("high")) == 2
    assert len(reg.models_by_risk("minimal")) == 1
    assert len(reg.models_by_risk("unacceptable")) == 0


def test_inventory_report():
    reg = AIDiscoveryRegistry(path=":memory:")
    v = reg.register_vendor("V", "US", verification_status="verified")
    reg.register_model("a", "p", "1", "t", "minimal", "internal")
    reg.register_model("b", "p", "1", "t", "high", "internal", vendor_id=v.vendor_id)
    inv = reg.inventory_report()
    assert inv["model_count"] == 2
    assert inv["vendor_count"] == 1
    assert inv["models_by_risk"]["high"] == 1
    assert inv["vendors_by_status"]["verified"] == 1


def test_posture_strong_with_clean_registry():
    reg = AIDiscoveryRegistry(path=":memory:")
    v = reg.register_vendor("V", "US", verification_status="verified")
    reg.register_model("a", "p", "1", "t", "limited", "internal", vendor_id=v.vendor_id)
    posture = reg.security_posture()
    assert posture["posture"] == "strong"
    assert posture["score"] >= 0.9


def test_posture_critical_with_unacceptable_model():
    reg = AIDiscoveryRegistry(path=":memory:")
    reg.register_model("bad", "p", "1", "t", "unacceptable", "research")
    posture = reg.security_posture()
    assert posture["posture"] in ("critical", "weak")
    assert any(f["severity"] == "critical" for f in posture["findings"])


def test_posture_high_risk_unverified_vendor():
    reg = AIDiscoveryRegistry(path=":memory:")
    v = reg.register_vendor("V", "US", verification_status="unverified")
    reg.register_model("a", "p", "1", "t", "high", "internal", vendor_id=v.vendor_id)
    posture = reg.security_posture()
    severities = [f["severity"] for f in posture["findings"]]
    assert "high" in severities


def test_flush_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "ai.jsonl")
    reg = AIDiscoveryRegistry(path=path)
    v = reg.register_vendor("V", "US", verification_status="verified")
    reg.register_model(
        "M", "P", "1.0", "test", "limited", "internal",
        vendor_id=v.vendor_id,
    )
    reg.flush()

    loaded = AIDiscoveryRegistry.load(path)
    assert len(loaded.vendors()) == 1
    assert len(loaded.models()) == 1
    assert loaded.vendors()[0].verification_status == "verified"
