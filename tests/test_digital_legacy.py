"""Tests for the Verifiable Digital Legacy module."""

from digital_legacy import (
    DigitalLegacyRegistry,
    Asset,
    Deed,
    Transfer,
    ASSET_TYPES,
)
from digital_legacy.core import content_fingerprint, GENESIS_HASH


def test_asset_types():
    assert len(ASSET_TYPES) == 7
    assert "source_code" in ASSET_TYPES
    assert "creative_work" in ASSET_TYPES


def test_content_fingerprint_deterministic():
    a = content_fingerprint({"x": 1, "y": 2})
    b = content_fingerprint({"y": 2, "x": 1})
    assert a == b
    assert len(a) == 64


def test_register_asset():
    reg = DigitalLegacyRegistry(path=":memory:")
    a = reg.register_asset(
        name="MyWork",
        asset_type="creative_work",
        owner="Alice",
        payload={"title": "Test"},
        successor="Bob",
    )
    assert isinstance(a, Asset)
    assert a.asset_id.startswith("asset:")
    assert a.owner == "Alice"
    assert a.successor == "Bob"
    assert len(reg.assets()) == 1


def test_register_asset_invalid_type():
    reg = DigitalLegacyRegistry(path=":memory:")
    try:
        reg.register_asset("X", "bogus_type", "Alice", {})
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_assets_by_owner():
    reg = DigitalLegacyRegistry(path=":memory:")
    reg.register_asset("A", "source_code", "Alice", {"x": 1})
    reg.register_asset("B", "source_code", "Alice", {"x": 2})
    reg.register_asset("C", "source_code", "Bob", {"x": 3})
    assert len(reg.assets_by_owner("Alice")) == 2
    assert len(reg.assets_by_owner("Bob")) == 1


def test_issue_deed():
    reg = DigitalLegacyRegistry(path=":memory:")
    a = reg.register_asset(
        "MyWork", "creative_work", "Alice",
        {"title": "Test"}, successor="Bob",
    )
    d = reg.issue_deed(a.asset_id)
    assert isinstance(d, Deed)
    assert d.deed_id.startswith("deed:")
    assert d.owner == "Alice"
    assert d.successor == "Bob"
    assert d.content_hash == a.content_hash


def test_issue_deed_unknown_asset():
    reg = DigitalLegacyRegistry(path=":memory:")
    try:
        reg.issue_deed("asset:doesnotexist")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_verify_deed_ok():
    reg = DigitalLegacyRegistry(path=":memory:")
    a = reg.register_asset(
        "MyWork", "creative_work", "Alice", {"title": "Test"},
    )
    d = reg.issue_deed(a.asset_id)
    result = reg.verify_deed(d.deed_id, {"title": "Test"})
    assert result["ok"] is True


def test_verify_deed_content_mismatch():
    reg = DigitalLegacyRegistry(path=":memory:")
    a = reg.register_asset(
        "MyWork", "creative_work", "Alice", {"title": "Test"},
    )
    d = reg.issue_deed(a.asset_id)
    result = reg.verify_deed(d.deed_id, {"title": "TAMPERED"})
    assert result["ok"] is False
    assert result["reason"] == "content_mismatch"


def test_verify_deed_unknown():
    reg = DigitalLegacyRegistry(path=":memory:")
    result = reg.verify_deed("deed:doesnotexist", {"x": 1})
    assert result["ok"] is False
    assert result["reason"] == "unknown_deed"


def test_transfer_updates_owner():
    reg = DigitalLegacyRegistry(path=":memory:")
    a = reg.register_asset(
        "MyWork", "creative_work", "Alice", {"x": 1},
        successor="Bob",
    )
    t = reg.transfer(a.asset_id, "Bob", reason="succession")
    assert isinstance(t, Transfer)
    assert t.from_party == "Alice"
    assert t.to_party == "Bob"
    assert reg.get_asset(a.asset_id).owner == "Bob"


def test_transfer_chain_verifies():
    reg = DigitalLegacyRegistry(path=":memory:")
    a = reg.register_asset("X", "source_code", "A", {"x": 1})
    reg.transfer(a.asset_id, "B")
    reg.transfer(a.asset_id, "C")
    chain = reg.verify_chain()
    assert chain["ok"] is True
    assert chain["length"] == 2


def test_transfer_chain_tamper_detected():
    reg = DigitalLegacyRegistry(path=":memory:")
    a = reg.register_asset("X", "source_code", "A", {"x": 1})
    reg.transfer(a.asset_id, "B")
    reg.transfer(a.asset_id, "C")
    reg._transfers[0].to_party = "TAMPERED"
    chain = reg.verify_chain()
    assert chain["ok"] is False
    assert chain["at"] == 0


def test_transfer_unknown_asset():
    reg = DigitalLegacyRegistry(path=":memory:")
    try:
        reg.transfer("asset:doesnotexist", "Bob")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_legacy_report():
    reg = DigitalLegacyRegistry(path=":memory:")
    a1 = reg.register_asset("A", "source_code", "Alice", {"x": 1}, successor="Bob")
    a2 = reg.register_asset("B", "creative_work", "Alice", {"x": 2}, successor="Bob")
    a3 = reg.register_asset("C", "trademark", "Corp", {"x": 3})
    reg.issue_deed(a1.asset_id)
    reg.issue_deed(a2.asset_id)
    reg.transfer(a1.asset_id, "Bob")

    report = reg.legacy_report()
    assert report["total_assets"] == 3
    assert report["total_deeds"] == 2
    assert report["total_transfers"] == 1
    assert report["assets_with_successor"] == 2
    assert report["assets_by_type"]["source_code"] == 1
    assert report["assets_by_type"]["creative_work"] == 1
    assert report["assets_by_type"]["trademark"] == 1


def test_flush_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "legacy.jsonl")
    reg = DigitalLegacyRegistry(path=path)
    a = reg.register_asset(
        "Persist", "source_code", "Alice",
        {"x": 1}, successor="Bob",
    )
    d = reg.issue_deed(a.asset_id)
    reg.transfer(a.asset_id, "Bob")
    reg.flush()

    loaded = DigitalLegacyRegistry.load(path)
    assert len(loaded.assets()) == 1
    assert len(loaded.deeds()) == 1
    assert len(loaded.transfers()) == 1
    assert loaded.verify_chain()["ok"] is True
    assert loaded.get_asset(a.asset_id).owner == "Bob"
