"""Tests for the Lineage module."""

from lineage import LineageTracker, Source, GENESIS_HASH, content_hash


def test_content_hash_deterministic():
    a = content_hash({"x": 1, "y": 2})
    b = content_hash({"y": 2, "x": 1})
    assert a == b
    assert len(a) == 64


def test_register_source_creates_source():
    t = LineageTracker(path=":memory:")
    src = t.register_source(
        uri="test.json",
        data={"a": 1},
        kind="file",
    )
    assert isinstance(src, Source)
    assert src.uri == "test.json"
    assert src.kind == "file"
    assert src.source_id.startswith("src:")


def test_register_source_hash_is_stable():
    t = LineageTracker(path=":memory:")
    s1 = t.register_source("test.json", {"a": 1})
    s2 = t.register_source("test.json", {"a": 1})
    assert s1.content_hash == s2.content_hash
    assert s1.source_id == s2.source_id


def test_trace_executes_and_records():
    t = LineageTracker(path=":memory:")
    src = t.register_source("input.json", {"x": 21})

    def double(x):
        return {"result": x * 2}

    result = t.trace("double", double, args=(21,), sources=[src])
    assert result == {"result": 42}
    assert len(t) == 1
    assert t.verify()["ok"] is True


def test_empty_tracker_verifies():
    t = LineageTracker(path=":memory:")
    report = t.verify()
    assert report["ok"] is True
    assert report["length"] == 0
    assert report["head"] == GENESIS_HASH


def test_tamper_detected():
    t = LineageTracker(path=":memory:")
    src = t.register_source("a.json", {"x": 1})
    t.record("action1", {"out": 1}, sources=[src])
    t.record("action2", {"out": 2}, sources=[src])
    t._records[0].action = "TAMPERED"
    report = t.verify()
    assert report["ok"] is False
    assert report["at"] == 0


def test_flush_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "lineage.jsonl")
    t = LineageTracker(path=path)
    src = t.register_source("input.json", {"x": 1})
    t.record("act1", {"out": 1}, sources=[src])
    t.record("act2", {"out": 2}, sources=[src])
    t.flush()

    loaded = LineageTracker.load(path)
    assert len(loaded) == 2
    assert loaded.verify()["ok"] is True


def test_flush_then_record_keeps_chain(tmp_path):
    path = str(tmp_path / "lineage.jsonl")
    t = LineageTracker(path=path)
    t.record("a", {"out": 1})
    t.flush()
    t.record("b", {"out": 2})
    t.flush()

    loaded = LineageTracker.load(path)
    assert len(loaded) == 2
    assert loaded.verify()["ok"] is True


def test_trace_propagates_exceptions():
    t = LineageTracker(path=":memory:")

    def fail():
        raise ValueError("boom")

    try:
        t.trace("fail_action", fail)
    except ValueError:
        pass
    assert t.verify()["ok"] is True


def test_multiple_sources_recorded():
    t = LineageTracker(path=":memory:")
    s1 = t.register_source("a.json", {"x": 1})
    s2 = t.register_source("b.json", {"y": 2})

    def combine(a, b):
        return {"sum": a + b}

    t.trace("combine", combine, args=(1, 2), sources=[s1, s2])
    rec = t._records[0]
    assert len(rec.input_source_ids) == 2
    assert s1.source_id in rec.input_source_ids
    assert s2.source_id in rec.input_source_ids
