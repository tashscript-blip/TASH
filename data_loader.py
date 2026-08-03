import json
import os

def load_real_data() -> dict:
    """Loads the real-world data source. Creates default if missing."""
    if os.path.exists("real_world_data.json"):
        with open("real_world_data.json", "r") as f:
            return json.load(f)
    # Fallback defaults if file is accidentally deleted
    default = {
        "society_population_billions": 8.0,
        "society_gdp_trillions": 100.0,
        "technology_readiness_level": 7.0,
        "ethics_corruption_index": 5.0,
        "cyber_threat_level": 5.0,
        "quantum_computing_power_qubits": 100.0,
        "diplomacy_relations_index": 5.0
    }
    with open("real_world_data.json", "w") as f:
        json.dump(default, f, indent=4)
    return default
