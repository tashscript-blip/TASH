"""
__main__.py - Lineage CLI.

Usage:
    python -m lineage demo              run a live demonstration
    python -m lineage verify <path>     verify a lineage file
"""

import sys
import tempfile
from pathlib import Path

from .core import LineageTracker


def cmd_demo(args):
    print("\nData Lineage - Live Demonstration\n")
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "lineage.jsonl")
        tracker = LineageTracker(path=path)

        src = tracker.register_source(
            uri="real_world_data.json",
            data={"population_b": 8.3, "gdp_t": 112.4},
            kind="file",
        )
        print("-> Registered source: " + src.uri)
        print("   source_id:    " + src.source_id)
        print("   content_hash: " + src.content_hash[:16] + "...")

        def double(x):
            return {"result": x * 2}

        result = tracker.trace("double", double, args=(21,), sources=[src])
        print("-> Traced action 'double' -> " + str(result))

        tracker.flush()

        loaded = LineageTracker.load(path)
        report = loaded.verify()
        print("\n-> Verify: " + str(report))

        print("\n-> Tamper test...")
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        lines[0] = lines[0].replace("double", "TAMPERED")
        Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
        report2 = LineageTracker.load(path).verify()
        print("   " + str(report2))
        print()
    return 0


def cmd_verify(args):
    if not args:
        print("Usage: python -m lineage verify <path>")
        return 1
    path = args[0]
    if not Path(path).exists():
        print("X File not found: " + path)
        return 1
    report = LineageTracker.load(path).verify()
    if report["ok"]:
        print("OK Chain is valid. Records: " + str(report["length"]))
        print("   Head hash: " + report["head"])
        return 0
    print("FAIL Chain is INVALID: " + report["reason"])
    return 2


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "demo":
        return cmd_demo(rest)
    if cmd == "verify":
        return cmd_verify(rest)
    print("Unknown command: " + cmd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
