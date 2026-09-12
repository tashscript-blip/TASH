"""
__main__.py - Verifiable Digital Legacy CLI.

Usage:
    python -m digital_legacy demo       run a live demonstration
    python -m digital_legacy report <path>   show legacy report
"""

import sys
import tempfile
from pathlib import Path

from .core import DigitalLegacyRegistry


def cmd_demo(args):
    print("\nVerifiable Digital Legacy - Live Demonstration\n")

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "digital_legacy.jsonl")
        reg = DigitalLegacyRegistry(path=path)

        print("-> Registering digital assets...")
        a1 = reg.register_asset(
            name="TASH Source Code",
            asset_type="source_code",
            owner="Tash-Raheem Joyner",
            successor="Hakem Nadir Harris",
            payload={"repo": "github.com/tashscript-blip/TASH", "version": "4.3.0"},
        )
        a2 = reg.register_asset(
            name="Sovereign Digital Codex Manuscript",
            asset_type="creative_work",
            owner="Tash-Raheem Joyner",
            successor="Hakem Nadir Harris",
            payload={"title": "The Sovereign Digital Codex", "words": 82000},
        )
        a3 = reg.register_asset(
            name="Legacy Grove Codex Trademark",
            asset_type="trademark",
            owner="Legacy Grove Codex LLC",
            payload={"mark": "LEGACY GROVE CODEX", "class": "042"},
        )
        print("   Registered " + str(len(reg.assets())) + " assets")

        print("\n-> Issuing deeds...")
        d1 = reg.issue_deed(a1.asset_id)
        d2 = reg.issue_deed(a2.asset_id)
        d3 = reg.issue_deed(a3.asset_id)
        print("   Deed 1: " + d1.deed_id + "  (successor: " + str(d1.successor) + ")")
        print("   Deed 2: " + d2.deed_id + "  (successor: " + str(d2.successor) + ")")
        print("   Deed 3: " + d3.deed_id + "  (successor: " + str(d3.successor) + ")")

        print("\n-> Verifying deeds...")
        r1 = reg.verify_deed(d1.deed_id, {"repo": "github.com/tashscript-blip/TASH", "version": "4.3.0"})
        print("   Deed 1 valid: " + str(r1["ok"]))

        r2 = reg.verify_deed(d2.deed_id, {"title": "TAMPERED", "words": 82000})
        print("   Deed 2 after tamper: " + str(r2["ok"]) + " (" + r2.get("reason", "") + ")")

        print("\n-> Recording succession transfers...")
        t1 = reg.transfer(a1.asset_id, "Hakem Nadir Harris", reason="Article II succession")
        print("   Transfer 1: " + t1.from_party + " -> " + t1.to_party)
        t2 = reg.transfer(a2.asset_id, "Hakem Nadir Harris", reason="Article II succession")
        print("   Transfer 2: " + t2.from_party + " -> " + t2.to_party)

        print("\n-> Verifying transfer chain...")
        chain = reg.verify_chain()
        print("   Chain valid: " + str(chain["ok"]) + "  (length: " + str(chain.get("length", 0)) + ")")

        print("\n-> Tamper test on transfer chain...")
        reg._transfers[0].to_party = "TAMPERED"
        chain2 = reg.verify_chain()
        print("   Chain valid: " + str(chain2["ok"]) + " (" + chain2.get("reason", "") + ")")

        print("\n-> Legacy report:")
        report = reg.legacy_report()
        print("   Total assets:     " + str(report["total_assets"]))
        print("   Total deeds:      " + str(report["total_deeds"]))
        print("   Total transfers:  " + str(report["total_transfers"]))
        print("   With successor:   " + str(report["assets_with_successor"]))

        reg.flush()
        reloaded = DigitalLegacyRegistry.load(path)
        print("\n-> Reloaded from disk:")
        print("   Assets:    " + str(len(reloaded.assets())))
        print("   Deeds:     " + str(len(reloaded.deeds())))
        print("   Transfers: " + str(len(reloaded.transfers())))
        print()

    return 0


def cmd_report(args):
    if not args:
        print("Usage: python -m digital_legacy report <path>")
        return 1
    path = args[0]
    if not Path(path).exists():
        print("X File not found: " + path)
        return 1
    reg = DigitalLegacyRegistry.load(path)
    report = reg.legacy_report()
    print("Total assets:    " + str(report["total_assets"]))
    print("Total deeds:     " + str(report["total_deeds"]))
    print("Total transfers: " + str(report["total_transfers"]))
    print("With successor:  " + str(report["assets_with_successor"]))
    print("Assets by type:")
    for typ, count in report["assets_by_type"].items():
        if count > 0:
            print("  " + typ.ljust(22) + " " + str(count))
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
