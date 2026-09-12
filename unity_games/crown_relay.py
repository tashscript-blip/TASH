"""
crown_relay.py — The Crown Relay
"A Ritual of Trust"
"""

import time
import random


def play_crown_relay() -> dict:
    """Play the Crown Relay — a ritual of trust."""
    print("   👑 The Crown Relay begins...")
    print("   A glowing Crown of Fire must be carried across the course.")
    print("   No one can hold it for more than 10 seconds.\n")

    time.sleep(1)

    obstacles = ["a wall", "a gap", "a tunnel", "a maze", "a bridge"]

    for obstacle in obstacles:
        print(f"   🧗 Crossing {obstacle}...")
        time.sleep(0.5)
        if random.random() > 0.1:
            print(f"   ✅ Team navigated {obstacle} together!")
        else:
            print(f"   ⚠️ The Crown almost fell! But the team caught it.")
            time.sleep(0.3)

    print("\n   🏁 The team crosses the finish line together.")
    print("   The Crown is raised aloft. The ALL rejoices.\n")

    return {
        "name": "Crown Relay",
        "virtue": "Trust",
        "status": "COMPLETE",
        "lesson": "We carry the weight of the Empire together."
    }


if __name__ == "__main__":
    play_crown_relay()
