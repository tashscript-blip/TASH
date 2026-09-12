"""
__main__.py - Identity Governance CLI.

Usage:
    python -m identity demo       run a live demonstration
    python -m identity verify <path>   verify all signatures in a file
"""

import sys
import tempfile
from pathlib import Path

from .core import IdentityRegistry


def cmd_demo(args):
    print("\nIdentity Governance - Live Demonstration\n")

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "identities.jsonl")
        reg = IdentityRegistry(path=path)

        ident = reg.register(name="TASH-Core", role="decision_agent")
        print("-> Registered identity: " + ident.name)
        print("   identity_id:  " + ident.identity_id)
        print("   fingerprint:  " + ident.public_fingerprint[:16] + "...")

        action = reg.sign_action(
            ident.identity_id,
            action="decree",
            payload={"text": "Broadcast the Love Protocol"},
        )
        print("\n-> Signed action: " + action.action)
        print("   signature:    " + action.signature[:16] + "...")

        print("\n-> Verifying signature...")
        print("   valid: " + str(reg.verify_action(action)))

        print("\n-> Tamper test: modifying payload...")
        action.payload["text"] = "TAMPERED"
        print("   valid: " + str(reg.verify_action(action)))

        print("\n-> Revoking identity...")
        reg.revoke(ident.identity_id)
        try:
            reg.sign_action(ident.identity_id, "anything")
            print("   [FAIL] Revoked identity was able to sign")
        except ValueError:
            print("   [OK] Revoked identity blocked from signing")

        reg.flush()
        reloaded = IdentityRegistry.load(path)
        print("\n-> Reloaded from disk:")
        print("   identities: " + str(len(reloaded.identities())))
        print("   actions:    " + str(len(reloaded.actions())))
        print()

    return 0


def cmd_verify(args):
    if not args:
        print("Usage: python -m identity verify <path>")
        return 1
    path = args[0]
    if not Path(path).exists():
        print("X File not found: " + path)
        return 1
    reg = IdentityRegistry.load(path)
    if not reg.actions():
        print("No actions in file.")
        return 0
    all_valid = reg.verify_all()
    print("Actions: " + str(len(reg.actions())))
    if all_valid:
        print("OK All signatures valid.")
        return 0
    print("FAIL Signature verification failed.")
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
