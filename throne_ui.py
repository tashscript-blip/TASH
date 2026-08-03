# throne_ui.py - TASH v3.0 (Real Data Source Enabled)
from emperors_command_center import TashCommandCenter
import data_loader
import json
import re

def extract_numbers(text: str) -> dict:
    nums = re.findall(r'\d+\.?\d*', text)
    context = {}
    for i, n in enumerate(nums):
        context[f"param_{i+1}"] = float(n)
    return context

if __name__ == "__main__":
    print("\n🏛️  TASH v3.0 - The Multi-Facet Throne")
    print("📍 Facets: Intel, Capital, Logistics, Strategy, Society, Tech, Ethics, Cyber, Quantum, Diplomacy.")
    print("📊 Loading Real World Data Source...")

    # 1. Load the real data
    real_context = data_loader.load_real_data()
    print(f"✅ Real Data Loaded: {len(real_context)} parameters.")
    print("🚀 Pyramid Base: 10 Dimensions. Awaiting your void.\n")

    ecc = TashCommandCenter()

    while True:
        try:
            decree = input("📜 Decree > ")
            if decree.lower() in ["exit", "quit", "logout"]:
                print("🛡️ Shielding TASH. Goodbye.")
                break
            if decree.strip() == "":
                continue

            # 2. Extract numbers from the decree
            parsed_numbers = extract_numbers(decree)

            # 3. MERGE: Real data takes precedence if keys collide, otherwise combine.
            # We simply combine them. The Pyramid will handle the rest.
            context_data = {**real_context, **parsed_numbers}
            
            print(f"📊 [TASH Census] Merged {len(context_data)} data points.")
            response = ecc.execute(decree, context_data)

            print("\n" + "="*50)
            print("👑 TASH APEX VERDICT:")
            print(json.dumps(response, indent=2, default=str))
            print("="*50 + "\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚡ [TASH Glitch] {e}")
