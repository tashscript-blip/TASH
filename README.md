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

**→ [The Seeker's Framework](docs/narrative/README.md)**

The design philosophy behind the platform — the Seven Keys, the Bridge, and why compliance tooling deserves a soul.

---

## Quick Start

```bash
git clone https://github.com/tashscript-blip/TASH.git
cd TASH
pip install -e ".[dev]"
python -m pytest tests/ -q
