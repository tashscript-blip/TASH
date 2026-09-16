# TASH — Tactical Artificial System Hierarchy

**Open-source compliance infrastructure for autonomous AI systems.**
**Legacy Grove Codex LLC | MIT License**

[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-4.5-brightgreen)](https://github.com/tashscript-blip/TASH/releases)
[![Tests](https://img.shields.io/badge/tests-124%20passing-success)](https://github.com/tashscript-blip/TASH)
[![CI](https://github.com/tashscript-blip/TASH/actions/workflows/ci.yml/badge.svg)](https://github.com/tashscript-blip/TASH/actions/workflows/ci.yml)

---

## What This Is

TASH is a Python platform that helps organizations deploy autonomous AI agents in regulated environments. It ships as **eight independent compliance modules** — from tamper-evident audit ledgers to supply chain integrity — each with its own tests and a runnable demo.

Everything is local-first, MIT-licensed, and runs with plain Python.

---

## Where To Start

TASH serves two audiences, each with a dedicated overview:

### 🔧 For Engineers, Federal Reviewers, and Procurement

**→ [Technical & Compliance Overview](docs/compliance/README.md)**

Everything you need to evaluate the platform: module inventory, standards alignment (NIST AI RMF, OWASP Agentic Top 10, EU AI Act), test counts, CI status, federal entity credentials, and the NASA REDDI-2026 readiness brief.

### 🌉 For Collaborators Curious About the Design

**→ [The Seeker\'s Framework](docs/narrative/README.md)**

The design philosophy behind the platform — the Seven Keys, the Bridge, and why compliance tooling deserves a soul.

---

## Quick Start

    git clone https://github.com/tashscript-blip/TASH.git
    cd TASH
    pip install -e ".[dev]"
    python -m pytest tests/ -q

Then try any of the eight domain demos:

    python -m node5_runtime demo           # SHA-256 hash-chained action ledger
    python -m lineage demo                 # Content-hash provenance chain
    python -m agent_orchestration demo     # Authorization scope + audit report
    python -m identity demo                # HMAC-signed action trail
    python -m governance demo              # Risk register and coverage
    python -m ai_discovery demo            # NIST AI RMF posture score
    python -m supply_chain demo            # Component fingerprint verification
    python -m digital_legacy demo          # Digital deeds and succession

Or launch the web dashboard:

    python -m aci_dashboard.app

Then open http://127.0.0.1:5000

---

## The Platform At A Glance

| Layer | Contents | Status |
| :--- | :--- | :--- |
| **Compliance domains** | 8 modules (governance through digital_legacy) | 96 tests passing |
| **Runtime ledger** | node5_runtime — SHA-256 hash chain | Tamper-evident |
| **Web dashboard** | aci_dashboard — Flask UI for all eight domains | 9 tests passing |
| **CLI** | tash — narrative and governance commands | v4.5.0 |
| **Federal readiness** | docs/nasa_reddi_readiness.md | Current |

**Total: 124 tests passing, CI green on Python 3.11 / 3.12 / 3.13.**

---

## Entity

| Field | Value |
| :--- | :--- |
| Legal Entity | Legacy Grove Codex LLC |
| UEI | D43ZB3D7QTW1 |
| CAGE | 23DZ6 |
| SAM.gov | Active (expires Jul 25, 2027) |
| Socio-economic | Self-Certified Small Disadvantaged Business |

---

## License

MIT License. Copyright © 2026 LEGACY GROVE CODEX LLC | tashscript-blip.

See [LICENSE](LICENSE) for terms.

---

*This README is intentionally brief. The technical and creative details live in the two sub-READMEs above.*
