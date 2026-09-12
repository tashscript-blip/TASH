"""
runtime.py — Deterministic wrapper around TASH actions.

The Node5Runtime wraps any callable (TASH's execute, a game, a bridge walk)
and records:
  - when the action started (ACTION_START)
  - what the result was (ACTION_END)
  - any exception raised (ACTION_ERROR)

Every record is appended to the hash-chained ActionLedger, giving a
tamper-evident, deterministic audit trail of every action taken.
"""

import time
import traceback
from typing import Any, Callable, Dict

from .ledger import ActionLedger


class Node5Runtime:
    """Deterministic, auditable wrapper for TASH actions."""

    def __init__(self, ledger_path: str = "node5_ledger.jsonl"):
        self.ledger = ActionLedger(path=ledger_path)
        self.ledger_path = ledger_path
        # Seed the chain with a bootstrap entry so the head is deterministic.
        self.ledger.append("BOOT", {"runtime": "Node5", "version": "0.1.0"})

    def execute(self, action_name: str, fn: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute a callable with full deterministic logging.

        Returns the callable's return value unchanged.
        Raises whatever the callable raises (after logging).
        """
        start = time.perf_counter()
        self.ledger.append(
            f"ACTION_START::{action_name}",
            {"args_count": len(args), "kwargs_keys": sorted(kwargs.keys())},
        )

        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.ledger.append(
                f"ACTION_ERROR::{action_name}",
                {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback_head": traceback.format_exc().splitlines()[-1],
                    "elapsed_ms": round(elapsed_ms, 3),
                },
            )
            self.flush()
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.ledger.append(
            f"ACTION_END::{action_name}",
            {
                "elapsed_ms": round(elapsed_ms, 3),
                "result_type": type(result).__name__,
                "result_summary": self._summarize(result),
            },
        )
        self.flush()
        return result

    def verify(self) -> Dict[str, Any]:
        """Verify the on-disk ledger chain."""
        loaded = ActionLedger.load(self.ledger_path)
        return loaded.verify()

    def flush(self) -> int:
        """Force a flush of in-memory entries to disk."""
        return self.ledger.flush()

    @staticmethod
    def _summarize(result: Any) -> str:
        if isinstance(result, dict):
            keys = ", ".join(sorted(result.keys())[:5])
            return f"dict(keys=[{keys}])"
        if isinstance(result, (list, tuple)):
            return f"{type(result).__name__}(len={len(result)})"
        if isinstance(result, str):
            return result[:80]
        return str(result)[:80]
