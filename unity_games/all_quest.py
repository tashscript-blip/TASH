"""
all_quest.py — The ALL Quest
"A Ritual of Discovery"
"""

import time
import random


def play_all_quest() -> dict:
    """Play the ALL Quest — a ritual of discovery."""
    print("   🧩 The ALL Quest begins...")
    print("   An open-world treasure hunt where teams solve puzzles.")
    print("   Each puzzle reveals a truth about the ALL.\n")

    time.sleep(1)

    puzzles = [
        "The Riddle of the Crown",
        "The Harmonic Key",
        "The Weave's Secret",
        "The Bridge's Shadow",
        "The Council's Whisper"
    ]

    for puzzle in puzzles:
        print(f"   🔍 Solving {puzzle}...")
        time.sleep(0.6)
        if random.random() > 0.2:
            print(f"   ✅ {puzzle} solved!")
        else:
            print(f"   ⚠️ The puzzle resists... The team works together.")
            time.sleep(0.3)
            print(f"   ✅ {puzzle} solved!")

    print("\n   🏁 All puzzles are solved.")
    print("   The final revelation appears:")
    print("   'Truth is revealed through collective effort.'\n")

    return {
        "name": "ALL Quest",
        "virtue": "Discovery",
        "status": "COMPLETE",
        "lesson": "Truth is revealed through collective effort."
    }


if __name__ == "__main__":
    play_all_quest()
