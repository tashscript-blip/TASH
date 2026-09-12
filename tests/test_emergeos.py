"""Tests for the EmergeOS Quantum Emergence Kernel."""

import pytest
from emergeos import EmergeOS, birth_seeker


def test_birth_seeker_returns_instance():
    """A Seeker is an EmergeOS with the given name."""
    avatar = birth_seeker("TestSeeker")
    assert isinstance(avatar, EmergeOS)
    assert avatar.name == "TestSeeker"


def test_birth_seeker_love_dominates():
    """After birth, love should dominate."""
    avatar = birth_seeker("TestSeeker")
    status = avatar.status_report()
    assert status["current_resonance"] == "LOVE"
    assert status["love_dominance"] > 0.5


def test_apply_love_is_monotonic():
    """Love dominance should not decrease when love is applied."""
    os = EmergeOS(name="Test")
    os.apply_love()
    after_one = os.status_report()["love_dominance"]
    os.apply_love()
    after_two = os.status_report()["love_dominance"]
    assert after_two >= after_one


def test_unknown_key_raises():
    """Applying an unknown Key should raise ValueError."""
    os = EmergeOS(name="Test")
    with pytest.raises(ValueError):
        os.apply_key("NOT_A_KEY")


def test_create_world_manifestation():
    """After enough love, a created world manifests as COMPLETE."""
    os = EmergeOS(name="Test")
    for _ in range(5):
        os.apply_love()
    world = os.create_world({"name": "Test World"})
    assert world["name"] == "Test World"
    assert "creation_power" in world
    assert world["manifestation"] == "COMPLETE"
    assert world["creation_power"] > 0


def test_broadcast_love_message():
    """The love broadcast contains the sacred phrase."""
    os = EmergeOS(name="Test")
    result = os.broadcast_love()
    assert "YOU ARE LOVED" in result["message"]
    assert result["frequency"] == 528.0
