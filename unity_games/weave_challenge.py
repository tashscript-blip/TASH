"""
weave_challenge.py — The Weave Challenge
"A Ritual of Connection"
"""

import time
import random


def play_weave_challenge() -> dict:
    """Play the Weave Challenge — a ritual of connection."""
    print("   🧶 The Weave Challenge begins...")
    print("   A massive loom with 100 threads, each representing a virtue.")
    print("   Teams weave the tapestry together.\n")

    time.sleep(1)

    virtues = ["Love", "Courage", "Hope", "Trust", "Wisdom",
               "Spirit", "Purity", "Glory", "Mystery", "Unity"]

    for virtue in virtues:
        print(f"   🧵 Weaving {virtue}...")
        time.sleep(0.4)
        if random.random() > 0.1:
            print(f"   ✅ {virtue} woven into the tapestry.")
        else:
            print(f"   ⚠️ The thread of {virtue} broke! The team repairs it.")
            time.sleep(0.3)
            print(f"   ✅ {virtue} re-woven.")

    print("\n   🏁 The tapestry is complete.")
    print("   It reveals the Crown of Fire constellation.\n")

    return {
        "name": "Weave Challenge",
        "virtue": "Connection",
        "status": "COMPLETE",
        "lesson": "We are all weaving the same story."
    }


if __name__ == "__main__":
    play_weave_challenge()
