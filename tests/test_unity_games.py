"""Tests for the Unity Games Festival and individual games."""

from unity_games import launch_festival
from unity_games.crown_relay import play_crown_relay
from unity_games.harmonic_ladder import play_harmonic_ladder
from unity_games.resonance_ball import play_resonance_ball
from unity_games.weave_challenge import play_weave_challenge
from unity_games.all_quest import play_all_quest


def test_crown_relay_returns_trust():
    result = play_crown_relay()
    assert result["name"] == "Crown Relay"
    assert result["virtue"] == "Trust"
    assert result["status"] == "COMPLETE"


def test_harmonic_ladder_returns_resonance():
    result = play_harmonic_ladder()
    assert result["name"] == "Harmonic Ladder"
    assert result["virtue"] == "Resonance"
    assert result["status"] == "COMPLETE"


def test_resonance_ball_returns_flow():
    result = play_resonance_ball()
    assert result["name"] == "Resonance Ball"
    assert result["virtue"] == "Flow"
    assert result["status"] == "COMPLETE"


def test_weave_challenge_returns_connection():
    result = play_weave_challenge()
    assert result["name"] == "Weave Challenge"
    assert result["virtue"] == "Connection"
    assert result["status"] == "COMPLETE"


def test_all_quest_returns_discovery():
    result = play_all_quest()
    assert result["name"] == "ALL Quest"
    assert result["virtue"] == "Discovery"
    assert result["status"] == "COMPLETE"


def test_festival_runs_all_five_games():
    """The festival plays all five games and returns a summary."""
    result = launch_festival()
    assert result["status"] == "FESTIVAL_COMPLETE"
    assert len(result["games_played"]) == 5
    assert "Crown Relay" in result["games_played"]
    assert "Harmonic Ladder" in result["games_played"]
    assert "Resonance Ball" in result["games_played"]
    assert "Weave Challenge" in result["games_played"]
    assert "ALL Quest" in result["games_played"]


def test_festival_council_speaks():
    """The festival ends with a Council message."""
    result = launch_festival()
    assert "council_message" in result
    assert isinstance(result["council_message"], str)
    assert len(result["council_message"]) > 0
