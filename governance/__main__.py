"""
__main__.py - Governance & Risk Orchestration CLI.

Usage:
    python -m governance demo       run a live demonstration
    python -m governance coverage <path>   show coverage report
"""

import sys
import tempfile
from pathlib import Path

from .core import GovernanceOrchestrator


def cmd_demo(args):
    print("\nGovernance & Risk Orchestration - Live Demonstration\n")

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "governance.jsonl")
        gov = GovernanceOrchestrator(path=path)

        print("-> Registering controls across domains...")
        c1 = gov.register_control(
            name="Hash-chained action ledger",
            domain="runtime_protection",
            description="Every action produces a SHA-256 chained record",
            status="implemented",
        )
        c2 = gov.register_control(
            name="Source provenance tracking",
            domain="dspm_lineage",
            description="Every input registered with content hash",
            status="implemented",
        )
        c3 = gov.register_control(
            name="Supervisor authorization register",
            domain="agent_orchestration",
            description="Every agent has a human supervisor and scope",
            status="implemented",
        )
        c4 = gov.register_control(
            name="Machine identity signatures",
            domain="identity_governance",
            description="HMAC-signed action trail per agent",
            status="implemented",
        )
        c5 = gov.register_control(
            name="Third-party model verification",
            domain="supply_chain",
            description="Track and verify external model updates",
            status="planned",
        )
        print("   Registered 5 controls across 5 domains")

        print("\n-> Registering a risk...")
        risk = gov.register_risk(
            title="Unverified agent action in denied environment",
            severity="high",
            likelihood="medium",
            domain="runtime_protection",
            control_ids=[c1.control_id],
        )
        print("   Risk: " + risk.title)
        print("   severity: " + risk.severity)
        print("   likelihood: " + risk.likelihood)

        print("\n-> Recording decision...")
        d = gov.decide(
            risk.risk_id,
            decision="mitigated",
            evidence={
                "control": c1.control_id,
                "test_file": "tests/test_node5_runtime.py",
                "test_count": 8,
                "all_passing": True,
            },
        )
        print("   Decision: " + d.decision)
        print("   Evidence keys: " + ", ".join(d.evidence.keys()))

        print("\n-> Coverage report:")
        report = gov.coverage_report()
        for dom, stats in report.items():
            bar = "#" * stats["implemented"] + "-" * stats["planned"]
            print("   " + dom.ljust(22) + " " + stats["coverage"].ljust(10) + " " + bar)

        print("\n-> Risk summary:")
        summary = gov.risk_summary()
        for sev, stats in summary.items():
            if stats["total"] > 0:
                print("   " + sev.ljust(10) + " total=" + str(stats["total"])
                      + " mitigated=" + str(stats["mitigated"])
                      + " accepted=" + str(stats["accepted"])
                      + " escalated=" + str(stats["escalated"]))

        gov.flush()
        reloaded = GovernanceOrchestrator.load(path)
        print("\n-> Reloaded from disk:")
        print("   controls:  " + str(len(reloaded.controls())))
        print("   risks:     " + str(len(reloaded.risks())))
        print("   decisions: " + str(len(reloaded.decisions())))
        print()

    return 0


def cmd_coverage(args):
    if not args:
        print("Usage: python -m governance coverage <path>")
        return 1
    path = args[0]
    if not Path(path).exists():
        print("X File not found: " + path)
        return 1
    gov = GovernanceOrchestrator.load(path)
    report = gov.coverage_report()
    for dom, stats in report.items():
        print(dom.ljust(22) + " " + stats["coverage"].ljust(10)
              + " (impl=" + str(stats["implemented"])
              + " partial=" + str(stats["partial"])
              + " planned=" + str(stats["planned"]) + ")")
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "demo":
        return cmd_demo(rest)
    if cmd == "coverage":
        return cmd_coverage(rest)
    print("Unknown command: " + cmd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
