"""
__main__.py - AI Discovery & Security Posture CLI.

Usage:
    python -m ai_discovery demo       run a live demonstration
    python -m ai_discovery posture <path>   show posture from saved file
"""

import sys
import tempfile
from pathlib import Path

from .core import AIDiscoveryRegistry


def cmd_demo(args):
    print("\nAI Discovery & Security Posture - Live Demonstration\n")

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "ai_discovery.jsonl")
        reg = AIDiscoveryRegistry(path=path)

        print("-> Registering vendors...")
        v1 = reg.register_vendor(
            name="Anthropic",
            country="US",
            services=["LLM API"],
            verification_status="verified",
        )
        v2 = reg.register_vendor(
            name="Legacy Grove Codex LLC",
            country="US",
            services=["In-house inference"],
            verification_status="verified",
        )
        v3 = reg.register_vendor(
            name="Third-Party Cloud",
            country="IE",
            services=["GPU hosting"],
            verification_status="unverified",
        )
        print("   Registered " + str(len(reg.vendors())) + " vendors")

        print("\n-> Registering AI models...")
        reg.register_model(
            name="TASH-Core",
            provider="LGC",
            version="4.3.0",
            purpose="Deterministic decision support",
            risk_class="limited",
            deployment_scope="internal",
            vendor_id=v2.vendor_id,
        )
        reg.register_model(
            name="Claude-Agent",
            provider="Anthropic",
            version="4.5",
            purpose="Agentic task execution",
            risk_class="high",
            deployment_scope="internal",
            vendor_id=v1.vendor_id,
        )
        reg.register_model(
            name="Legacy-Experimental",
            provider="LGC",
            version="0.1.0",
            purpose="Autonomous targeting prototype",
            risk_class="unacceptable",
            deployment_scope="research-only",
            vendor_id=v2.vendor_id,
        )
        print("   Registered " + str(len(reg.models())) + " models")

        print("\n-> Inventory report:")
        inv = reg.inventory_report()
        print("   Models:  " + str(inv["model_count"]))
        print("   Vendors: " + str(inv["vendor_count"]))
        for rc, count in inv["models_by_risk"].items():
            print("     " + rc.ljust(14) + " " + str(count))
        for st, count in inv["vendors_by_status"].items():
            print("     " + st.ljust(14) + " " + str(count))

        print("\n-> Security posture:")
        posture = reg.security_posture()
        print("   Posture: " + posture["posture"])
        print("   Score:   " + str(posture["score"]))
        if posture["findings"]:
            print("   Findings:")
            for f in posture["findings"]:
                print("     [" + f["severity"].upper() + "] " + f["message"])

        print("\n-> Mitigating: marking Legacy-Experimental as suspended...")
        reg._models = {
            k: m for k, m in reg._models.items()
            if m.name != "Legacy-Experimental"
        }
        posture2 = reg.security_posture()
        print("   Posture: " + posture2["posture"])
        print("   Score:   " + str(posture2["score"]))

        reg.flush()
        reloaded = AIDiscoveryRegistry.load(path)
        print("\n-> Reloaded from disk:")
        print("   Vendors: " + str(len(reloaded.vendors())))
        print("   Models:  " + str(len(reloaded.models())))
        print()

    return 0


def cmd_posture(args):
    if not args:
        print("Usage: python -m ai_discovery posture <path>")
        return 1
    path = args[0]
    if not Path(path).exists():
        print("X File not found: " + path)
        return 1
    reg = AIDiscoveryRegistry.load(path)
    posture = reg.security_posture()
    print("Posture: " + posture["posture"])
    print("Score:   " + str(posture["score"]))
    for f in posture["findings"]:
        print("  [" + f["severity"].upper() + "] " + f["message"])
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "demo":
        return cmd_demo(rest)
    if cmd == "posture":
        return cmd_posture(rest)
    print("Unknown command: " + cmd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
