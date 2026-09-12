"""Tests for the Node 5 Runtime and hash-chained ledger."""

import json
from pathlib import Path

from node5_runtime import ActionLedger, LedgerEntry, GENESIS_HASH, Node5Runtime
from node5_runtime.ledger import _hash_entry


def test_empty_ledger_verifies():
    ledger = ActionLedger(path=":memory:")
    report = ledger.verify()
    assert report["ok"] is True
    assert report["length"] == 0
    assert report["head"] == GENESIS_HASH


def test_append_links_chain():
    ledger = ActionLedger(path=":memory:")
    e1 = ledger.append("A", {"x": 1})
    e2 = ledger.append("B", {"x": 2})
    assert e2.prev_hash == e1.hash
    assert e1.prev_hash == GENESIS_HASH
    assert e1.index == 0
    assert e2.index == 1


def test_verify_passes_on_clean_chain():
    ledger = ActionLedger(path=":memory:")
    for i in range(5):
        ledger.append("E", {"i": i})
    assert ledger.verify()["ok"] is True


def test_verify_detects_tamper():
    ledger = ActionLedger(path=":memory:")
    ledger.append("A", {"x": 1})
    ledger.append("B", {"x": 2})
    ledger._entries[0].payload["x"] = 999
    report = ledger.verify()
    assert report["ok"] is False
    assert report["at"] == 0


def test_flush_and_load_roundtrip(tmp_path):
    ledger_path = str(tmp_path / "led.jsonl")
    ledger = ActionLedger(path=ledger_path)
    ledger.append("A", {"x": 1})
    ledger.append("B", {"x": 2})
    ledger.flush()

    loaded = ActionLedger.load(ledger_path)
    assert len(loaded) == 2
    assert loaded.verify()["ok"] is True


def test_flush_then_append_keeps_chain(tmp_path):
    """Regression: index and prev_hash must survive a flush."""
    ledger_path = str(tmp_path / "led.jsonl")
    ledger = ActionLedger(path=ledger_path)
    ledger.append("A", {"x": 1})
    ledger.flush()
    ledger.append("B", {"x": 2})
    ledger.flush()

    loaded = ActionLedger.load(ledger_path)
    assert loaded.verify()["ok"] is True
    assert len(loaded) == 2


def test_runtime_logs_start_and_end(tmp_path):
    ledger_path = str(tmp_path / "rt.jsonl")
    rt = Node5Runtime(ledger_path=ledger_path)
    result = rt.execute("double", lambda x: x * 2, 21)
    assert result == 42

    loaded = ActionLedger.load(ledger_path)
    actions = [e.action for e in loaded._entries]
    assert "BOOT" in actions
    assert any("ACTION_START::double" in a for a in actions)
    assert any("ACTION_END::double" in a for a in actions)
    assert loaded.verify()["ok"] is True


def test_runtime_logs_errors(tmp_path):
    ledger_path = str(tmp_path / "err.jsonl")
    rt = Node5Runtime(ledger_path=ledger_path)

    def boom():
        raise ValueError("bang")

    try:
        rt.execute("boom", boom)
    except ValueError:
        pass

    loaded = ActionLedger.load(ledger_path)
    actions = [e.action for e in loaded._entries]
    assert any("ACTION_ERROR::boom" in a for a in actions)
    assert loaded.verify()["ok"] is True
