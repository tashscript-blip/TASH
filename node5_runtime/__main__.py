"""
__main__.py - Node 5 Runtime CLI.
"""

import json as _json
import sys
import tempfile
from pathlib import Path

from .ledger import ActionLedger
from .runtime import Node5Runtime


def cmd_verify(args):
    if not args:
        print("Usage: python -m node5_runtime verify <ledger.jsonl>")
        return 1
    path = args[0]
    if not Path(path).exists():
        print("X Ledger not found: " + path)
        return 1
    report = ActionLedger.load(path).verify()
    if report["ok"]:
        print("OK Chain is valid. Entries: " + str(report["length"]))
        print("   Head hash: " + report["head"])
        return 0
    else:
        print("FAIL Chain is INVALID: " + report["reason"])
        return 2


def cmd_demo(args):
    print("\nNode 5 Runtime - Live Demonstration\n")

    with tempfile.TemporaryDirectory() as tmp:
        ledger_path = str(Path(tmp) / "demo.jsonl")
        runtime = Node5Runtime(ledger_path=ledger_path)

        def make_world(name):
            return {"name": name, "manifestation": "COMPLETE"}

        def fail_thing():
            raise ValueError("intentional failure for demo")

        print("-> Executing 'create_world'...")
        result = runtime.execute("create_world", make_world, "Seeker's Sanctuary")
        print("   Result: " + str(result))

        print("-> Executing 'fail_thing' (expected error)...")
        try:
            runtime.execute("fail_thing", fail_thing)
        except ValueError as e:
            print("   Caught: " + str(e))

        print("\n-> Verifying ledger chain...")
        report = runtime.verify()
        print("   " + str(report))

        print("\n-> Tamper test: modifying the ledger file on disk...")
        lines = Path(ledger_path).read_text(encoding="utf-8").splitlines()
        first = _json.loads(lines[0])
        first["payload"]["runtime"] = "TAMPERED"
        lines[0] = _json.dumps(first, sort_keys=True, default=str)
        Path(ledger_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
        report2 = runtime.verify()
        print("   " + str(report2))
        print()

    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "verify":
        return cmd_verify(rest)
    if cmd == "demo":
        return cmd_demo(rest)
    print("Unknown command: " + cmd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
