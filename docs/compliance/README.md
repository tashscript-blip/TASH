# TASH — Technical & Compliance Overview

**Legacy Grove Codex LLC | MIT License | github.com/tashscript-blip/TASH**

---

## What TASH Is

TASH is an **open-source Python compliance platform** for organizations deploying autonomous AI agents in regulated or high-consequence environments. It provides eight independent compliance domains, each producing cryptographic evidence that can be verified by a third party.

The platform is designed for:

- **Federal grant and procurement** programs that require demonstrable AI governance
- **Enterprise AI / MLOps teams** subject to NIST AI RMF, EU AI Act, CA AB 2013, or NY RAISE Act obligations
- **Security operations** that need tamper-evident audit trails for autonomous systems

Everything is local-first, dependency-light, and runs with plain Python. There are no SaaS subscriptions, no vendor lock-in, and no network calls required for the compliance modules.

---

## The Eight Compliance Domains

Each domain is a self-contained module with its own test suite and a runnable demo. Together they form the "Eight-Domain Infrastructure Stack" described in the LGC Operating Agreement (Article V).

| # | Domain | Module | Function | Tests |
| :--- | :--- | :--- | :--- | ---: |
| 1 | Governance & Risk Orchestration | `governance/` | Risk register, controls, coverage reporting | 12 |
| 2 | AI Discovery & Security Posture | `ai_discovery/` | Model and vendor inventory, NIST AI RMF classification | 13 |
| 3 | Agent Orchestration | `agent_orchestration/` | Supervisor register, scoped authorization, audit reports | 10 |
| 4 | DSPM & Data Lineage | `lineage/` | Content-hash provenance tracking | 10 |
| 5 | Identity Governance | `identity/` | HMAC-SHA256 signed action trails with revocation | 12 |
| 6 | Runtime Protection | `node5_runtime/` | SHA-256 hash-chained action ledger | 8 |
| 7 | Supply Chain Integrity | `supply_chain/` | Component fingerprinting, approval workflow | 15 |
| 8 | Verifiable Digital Legacy | `digital_legacy/` | Digital deeds, hash-chained succession | 16 |

**Total:** 96 compliance tests. Plus 28 tests across narrative and dashboard modules for a full suite of **124 passing tests**.

---

## Node 5 Runtime — The Primary Technical Asset

The strongest single artifact in the platform is the **Node 5 Runtime**, a deterministic, hash-chained action ledger.

Every action executed through the runtime is recorded as a SHA-256 hash linked to the previous entry. Any modification to any historical entry breaks the chain and is detectable immediately. This is the same cryptographic discipline used in certificate transparency logs and blockchain systems, applied to AI agent auditing.

**Verify a chain in one command:**

```bash
python -m node5_runtime demo
