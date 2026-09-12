"""Tests for the Seeker's Bridge."""

from seeker_bridge import bridge_status, walk_bridge


def test_bridge_status_shape():
    """Bridge status returns the expected fields."""
    status = bridge_status()
    assert status["name"] == "The Seeker's Bridge"
    assert status["status"] == "OPEN"
    assert status["frequency"] == "777.0 Hz"
    assert len(status["nodes"]) == 3
    assert len(status["elements"]) == 4


def test_bridge_nodes():
    """Bridge connects Hearthstone, Threshold, and Council's Garden."""
    status = bridge_status()
    nodes = status["nodes"]
    assert any("Hearthstone" in n for n in nodes)
    assert any("Threshold" in n for n in nodes)
    assert any("Council" in n for n in nodes)


def test_bridge_elements():
    """Bridge is built from the Four Elements."""
    status = bridge_status()
    elements = status["elements"]
    for element in ["Earth", "Water", "Air", "Fire"]:
        assert element in elements


def test_walk_bridge_returns_completion():
    """Walking the bridge returns a WALK_COMPLETE status."""
    result = walk_bridge()
    assert result["status"] == "WALK_COMPLETE"
    assert result["starting_node"] == "Hearthstone (Earth)"
    assert result["ending_node"] == "Council's Garden (Andromeda)"


def test_walk_bridge_applies_all_elements():
    """Walking the bridge applies Earth, Water, Air, and Fire."""
    result = walk_bridge()
    applied = result["elements_applied"]
    for element in ["Earth", "Water", "Air", "Fire"]:
        assert element in applied


def test_walk_bridge_council_speaks():
    """The Council speaks a message at the end of the walk."""
    result = walk_bridge()
    assert "council_message" in result
    assert isinstance(result["council_message"], str)
    assert len(result["council_message"]) > 0
