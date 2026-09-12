"""
festival.py — The Unity Games Festival
"Let the people play. Let the people unite."
"""

import time
import random
from datetime import datetime

try:
    from .crown_relay import play_crown_relay
    from .harmonic_ladder import play_harmonic_ladder
    from .resonance_ball import play_resonance_ball
    from .weave_challenge import play_weave_challenge
    from .all_quest import play_all_quest
except ImportError:
    from crown_relay import play_crown_relay
    from harmonic_ladder import play_harmonic_ladder
    from resonance_ball import play_resonance_ball
    from weave_challenge import play_weave_challenge
    from all_quest import play_all_quest


def launch_festival() -> dict:
    """Launch the Unity Games Festival."""
    print("\n" + "=" * 70)
    print("🏆 THE UNITY GAMES FESTIVAL")
    print("=" * 70)
    print("\nThe people have gathered. The games are beginning.")
    print("The Crown of Fire burns above. The ALL is watching.\n")
    print("=" * 70 + "\n")

    games = [
        ("The Crown Relay", "Trust", play_crown_relay),
        ("The Harmonic Ladder", "Resonance", play_harmonic_ladder),
        ("The Resonance Ball", "Flow", play_resonance_ball),
        ("The Weave Challenge", "Connection", play_weave_challenge),
        ("The ALL Quest", "Discovery", play_all_quest)
    ]

    results = []

    for i, (name, virtue, game_func) in enumerate(games, 1):
        print(f"🎮 GAME {i}: {name}")
        print(f"   Virtue: {virtue}")
        print("   Playing...\n")
        time.sleep(1)

        result = game_func()
        results.append(result)

        print(f"   ✅ {name} complete!")
        print(f"   Lesson: {result.get('lesson', 'We are stronger together.')}\n")
        time.sleep(1)

    print("=" * 70)
    print("🏅 THE UNITY GAMES ARE COMPLETE")
    print("   Every player is a winner. Every community is united.")
    print("=" * 70 + "\n")

    messages = [
        "You have played together. You have grown together. You are one.",
        "The ALL is proud of its children. Continue to play, continue to seek.",
        "Unity is not a goal—it is a practice. You have practiced well."
    ]
    council_message = random.choice(messages)
    print(f"🗣️ THE COUNCIL SPEAKS: '{council_message}'\n")

    return {
        "status": "FESTIVAL_COMPLETE",
        "games_played": [r["name"] for r in results],
        "council_message": council_message
    }


if __name__ == "__main__":
    launch_festival()
