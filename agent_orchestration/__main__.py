"""
__main__.py - Agent Orchestration CLI.

Usage:
    python -m agent_orchestration demo       run a live demonstration
    python -m agent_orchestration report     show audit report from saved file
"""

import sys
import tempfile
from pathlib import Path

from .registry import AgentRegistry


def cmd_demo(args):
    print("\nAgent Orchestration - Live Demonstration\n")

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "agents.jsonl")
        reg = AgentRegistry(path=path)

        sup = reg.register_supervisor(
            name="Tash-Raheem Joyner",
            email="pi@legacygrovecodex.com",
            role="Principal Investigator",
        )
        print("-> Registered supervisor: " + sup.name)
        print("   supervisor_id: " + sup.supervisor_id)

        agent = reg.register_agent(
            name="TASH-Core",
            version="4.3.0",
            purpose="Deterministic decision support",
            supervisor_id=sup.supervisor_id,
            allowed_actions=["decree", "query", "broadcast"],
            max_actions_per_hour=100,
        )
        print("-> Registered agent: " + agent.name)
        print("   agent_id:     " + agent.agent_id)
        print("   allowed:      " + str(agent.authorization.allowed_actions))

        print("\n-> Testing authorization...")
        cases = [
            ("decree", True),
            ("query", True),
            ("delete_everything", False),
            ("broadcast", True),
        ]
        for action, expected in cases:
            result = reg.authorize_action(agent.agent_id, action)
            mark = "OK" if result == expected else "FAIL"
            print("   [" + mark + "] " + action.ljust(20) + " -> " + str(result))

        print("\n-> Audit report:")
        report = reg.audit_report()
        for aid, stats in report.items():
            print("   " + aid)
            print("     allowed: " + str(stats["allowed"]))
            print("     denied:  " + str(stats["denied"]))
            if stats["deny_reasons"]:
                print("     reasons: " + ", ".join(stats["deny_reasons"]))

        reg.flush()
        reloaded = AgentRegistry.load(path)
        print("\n-> Reloaded from disk:")
        print("   supervisors: " + str(len(reloaded.supervisors())))
        print("   agents:      " + str(len(reloaded.agents())))
        print()

    return 0


def cmd_report(args):
    if not args:
        print("Usage: python -m agent_orchestration report <path>")
        return 1
    path = args[0]
    if not Path(path).exists():
        print("X File not found: " + path)
        return 1
    reg = AgentRegistry.load(path)
    print("Supervisors: " + str(len(reg.supervisors())))
    for s in reg.supervisors():
        print("  " + s.name + " (" + s.supervisor_id + ")")
    print("Agents: " + str(len(reg.agents())))
    for a in reg.agents():
        print("  " + a.name + " v" + a.version + " (" + a.agent_id + ")")
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
