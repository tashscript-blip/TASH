"""
__main__.py - Supply Chain Integrity CLI.

Usage:
    python -m supply_chain demo       run a live demonstration
    python -m supply_chain report <path>   show integrity report
"""

import sys
import tempfile
from pathlib import Path

from .core import SupplyChainRegistry


def cmd_demo(args):
    print("\nSupply Chain Integrity - Live Demonstration\n")

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "supply_chain.jsonl")
        reg = SupplyChainRegistry(path=path)

        print("-> Registering components...")
        model = reg.register_component(
            name="TASH-Core",
            version="4.3.0",
            component_type="model",
            source="github.com/tashscript-blip/TASH",
            payload={"weights_hash": "abc123", "params": 125000000},
        )
        lib = reg.register_component(
            name="numpy",
            version="2.5.1",
            component_type="library",
            source="pypi.org",
            payload={"sha256": "deadbeef", "size": 18500000},
            auto_approve=True,
        )
        vendor = reg.register_component(
            name="Anthropic-Claude",
            version="4.5",
            component_type="vendor_artifact",
            source="anthropic.com",
            payload={"api_version": "2024-10", "region": "us-east"},
        )
        print("   Registered " + str(len(reg.components())) + " components")

        print("\n-> Approving critical components...")
        reg.approve(model.component_id, reviewer="Tash Joyner", reason="Verified by PI")
        print("   Approved: " + model.name)
        print("   Pending:  " + vendor.name)

        print("\n-> Verifying component integrity...")
        result = reg.verify(model.component_id, {"weights_hash": "abc123", "params": 125000000})
        print("   Original payload: " + str(result["ok"]))

        print("\n-> Tamper test...")
        result = reg.verify(model.component_id, {"weights_hash": "TAMPERED", "params": 125000000})
        print("   Tampered payload: " + str(result["ok"]) + " (" + result.get("reason", "") + ")")

        print("\n-> Simulating model update...")
        reg.update_component(model.component_id, {"weights_hash": "newXYZ", "params": 130000000}, new_version="4.4.0")
        print("   Update resets approval: " + reg.get_component(model.component_id).approval_status)

        print("\n-> Integrity report:")
        report = reg.integrity_report()
        print("   Total components:  " + str(report["total_components"]))
        print("   Approved:          " + str(report["by_status"]["approved"]))
        print("   Pending:           " + str(report["by_status"]["pending"]))
        print("   Pending critical:  " + str(report["pending_critical"]))
        print("   Verify OK:         " + str(report["verify_ok"]))
        print("   Verify FAIL:       " + str(report["verify_fail"]))

        reg.flush()
        reloaded = SupplyChainRegistry.load(path)
        print("\n-> Reloaded from disk:")
        print("   Components: " + str(len(reloaded.components())))
        print("   Approvals:  " + str(len(reloaded.approvals())))
        print()

    return 0


def cmd_report(args):
    if not args:
        print("Usage: python -m supply_chain report <path>")
        return 1
    path = args[0]
    if not Path(path).exists():
        print("X File not found: " + path)
        return 1
    reg = SupplyChainRegistry.load(path)
    report = reg.integrity_report()
    print("Total components: " + str(report["total_components"]))
    print("Approved:         " + str(report["by_status"]["approved"]))
    print("Pending:          " + str(report["by_status"]["pending"]))
    print("Rejected:         " + str(report["by_status"]["rejected"]))
    print("Verify failures:  " + str(report["verify_fail"]))
    print("Pending critical: " + str(report["pending_critical"]))
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "demo":
        return cmd_demo(rest)
    if cmd == "report":
        return cmd_report(rest)
    print("Unknown command: " + cmd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
