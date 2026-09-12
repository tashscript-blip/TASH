"""
resonance_ball.py — The Resonance Ball
"A Ritual of Flow"
"""

import time
import random


def play_resonance_ball() -> dict:
    """Play the Resonance Ball — a ritual of flow."""
    print("   ⚽ The Resonance Ball begins...")
    print("   A glowing sphere floats in the center of a circular field.")
    print("   Players guide the ball through 9 gates using only their voices.\n")

    time.sleep(1)

    gates = ["Awareness", "Unity", "Resonance", "Creation",
             "Courage", "Forgiveness", "Faith", "Love", "The ALL"]

    for i, gate in enumerate(gates, 1):
        print(f"   🌀 Gate {i}: {gate}")
        time.sleep(0.4)
        if random.random() > 0.2:
            print(f"   ✅ The ball glides through Gate {i}!")
        else:
            print(f"   ⚠️ The ball wobbles! The voices re-align...")
            time.sleep(0.3)
            print(f"   ✅ The ball glides through Gate {i}!")

    print("\n   🏁 The ball passes through all 9 gates.")
    print("   It rises gently into the air, hovering above the team.\n")

    return {
        "name": "Resonance Ball",
        "virtue": "Flow",
        "status": "COMPLETE",
        "lesson": "We sing the future into being."
    }


if __name__ == "__main__":
    play_resonance_ball()
