"""
harmonic_ladder.py — The Harmonic Ladder
"A Ritual of Resonance"
"""

import time
import random


def play_harmonic_ladder() -> dict:
    """Play the Harmonic Ladder — a ritual of resonance."""
    print("   🎵 The Harmonic Ladder begins...")
    print("   A climbing wall with 10 handholds, each emitting a frequency.")
    print("   The team must climb in perfect sync.\n")

    time.sleep(1)

    frequencies = [432, 440, 480, 490, 500, 510, 520, 528, 532, 540]

    for i, freq in enumerate(frequencies, 1):
        print(f"   🎼 Hold {i}: {freq} Hz")
        time.sleep(0.3)
        if random.random() > 0.15:
            print(f"   ✅ Harmonic chord {i}/{len(frequencies)} achieved!")
        else:
            print(f"   ⚠️ Dissonance! The team re-aligns...")
            time.sleep(0.3)
            print(f"   ✅ Harmonic chord {i}/{len(frequencies)} achieved!")

    print("\n   🏁 The team reaches the top together.")
    print("   The final chord triggers a shower of golden light.\n")

    return {
        "name": "Harmonic Ladder",
        "virtue": "Resonance",
        "status": "COMPLETE",
        "lesson": "We climb together or not at all."
    }


if __name__ == "__main__":
    play_harmonic_ladder()
