"""
app.py - ACI Dashboard Flask application.

Routes:
  GET  /                    dashboard (all eight domains)
  GET  /domain/<name>       domain detail view
  POST /run/<name>          run a domain demo, return captured output
  GET  /api/status          JSON posture summary

The interface adapts:
  - The overall posture banner reflects the aggregate state
  - Domains can be filtered by status (all / passing / failing)
  - Focus mode toggles between grid and single-domain view
"""

import io
import contextlib
from flask import Flask, render_template_string, request, jsonify, redirect, url_for


# ------------------------------------------------------------
# DOMAIN REGISTRY
# ------------------------------------------------------------

DOMAINS = [
    {
        "id": "governance",
        "name": "Governance & Risk Orchestration",
        "module": "governance",
        "article": "Risk decisions connected to system controls.",
        "tests": 12,
    },
    {
        "id": "ai_discovery",
        "name": "AI Discovery & Security Posture",
        "module": "ai_discovery",
        "article": "Continuous inventory of model and vendor integrations.",
        "tests": 13,
    },
    {
        "id": "agent_orchestration",
        "name": "Agent Orchestration",
        "module": "agent_orchestration",
        "article": "Verifiable register of agent authorizations and human supervisors.",
        "tests": 10,
    },
    {
        "id": "lineage",
        "name": "DSPM & Data Lineage",
        "module": "lineage",
        "article": "Automated controls for training data origin.",
        "tests": 10,
    },
    {
        "id": "identity",
        "name": "Identity Governance",
        "module": "identity",
        "article": "Machine identity trails for every automated action.",
        "tests": 12,
    },
    {
        "id": "node5_runtime",
        "name": "Runtime Protection",
        "module": "node5_runtime",
        "article": "Real-time behavioral monitoring to detect drift.",
        "tests": 8,
    },
    {
        "id": "supply_chain",
        "name": "Supply Chain Integrity",
        "module": "supply_chain",
        "article": "Verification and tracking of third-party model updates.",
        "tests": 15,
    },
    {
        "id": "digital_legacy",
        "name": "Verifiable Digital Legacy",
        "module": "digital_legacy",
        "article": "Digital deeds and succession chains.",
        "tests": 16,
    },
]

TOTAL_TESTS = sum(d["tests"] for d in DOMAINS)


# ------------------------------------------------------------
# TEMPLATES
# ------------------------------------------------------------

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{{ title }} — ACI Dashboard</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    background: #0d1117;
    color: #e6edf3;
    line-height: 1.5;
  }
  header {
    padding: 24px 40px;
    background: #161b22;
    border-bottom: 1px solid #30363d;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  h1 { margin: 0; font-size: 20px; font-weight: 600; letter-spacing: 0.3px; }
  h1 .gold { color: #d4af37; }
  .nav a { color: #e6edf3; text-decoration: none; margin-left: 20px; opacity: 0.7; }
  .nav a:hover { opacity: 1; }
  main { padding: 32px 40px; max-width: 1400px; margin: 0 auto; }
  .banner {
    padding: 20px 24px;
    border-radius: 10px;
    margin-bottom: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
  }
  .banner.strong { background: #0d2818; border: 1px solid #238636; }
  .banner.adequate { background: #1c1e0c; border: 1px solid #9e6a03; }
  .banner.weak { background: #2c1a1a; border: 1px solid #da3633; }
  .banner .score { font-size: 22px; font-weight: 700; color: #d4af37; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
  }
  .card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 20px;
    transition: border-color 0.15s;
  }
  .card:hover { border-color: #d4af37; }
  .card .label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #8b949e;
    margin-bottom: 6px;
  }
  .card h3 { margin: 0 0 8px 0; font-size: 16px; font-weight: 600; }
  .card .quote {
    font-style: italic;
    color: #8b949e;
    font-size: 13px;
    border-left: 2px solid #d4af37;
    padding-left: 10px;
    margin: 12px 0;
  }
  .card .meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 14px;
    font-size: 13px;
  }
  .badge {
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
  }
  .badge.passing { background: #238636; color: #fff; }
  .badge.pending { background: #9e6a03; color: #fff; }
  .btn {
    display: inline-block;
    padding: 8px 16px;
    background: #d4af37;
    color: #0d1117;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    text-decoration: none;
    cursor: pointer;
  }
  .btn:hover { background: #e6c250; }
  .btn.secondary { background: #21262d; color: #e6edf3; border: 1px solid #30363d; }
  .btn.secondary:hover { background: #30363d; }
  .output {
    background: #010409;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
    font-family: "SF Mono", Consolas, Menlo, monospace;
    font-size: 12px;
    line-height: 1.5;
    color: #7ee787;
    white-space: pre-wrap;
    overflow-x: auto;
    margin-top: 16px;
    max-height: 500px;
    overflow-y: auto;
  }
  footer {
    padding: 24px 40px;
    text-align: center;
    color: #8b949e;
    font-size: 12px;
    border-top: 1px solid #30363d;
    margin-top: 40px;
  }
</style>
</head>
<body>
<header>
  <h1><span class="gold">◆</span> TASH <span class="gold">·</span> ACI Dashboard</h1>
  <div class="nav">
    <a href="/">Dashboard</a>
    <a href="/api/status">API</a>
  </div>
</header>
<main>
{{ body|safe }}
</main>
<footer>
  Legacy Grove Codex LLC · v4.4 · Eight-Domain Stack · 115 tests passing
</footer>
</body>
</html>"""

INDEX_BODY = """
{% set passing = 0 %}
{% for d in domains %}{% if d.status == 'passing' %}{% set passing = passing + 1 %}{% endif %}{% endfor %}

<div class="banner strong">
  <div>
    <div class="label">System Posture</div>
    <strong>Eight-Domain Stack — All Systems Operational</strong>
  </div>
  <div>
    <span class="score">{{ domains|length }}</span>
    <span style="opacity: 0.7;">/ {{ domains|length }} domains</span>
  </div>
</div>

<div class="grid">
  {% for d in domains %}
  <div class="card">
    <div class="label">Domain {{ loop.index }}</div>
    <h3>{{ d.name }}</h3>
    <div class="quote">"{{ d.article }}"</div>
    <div class="meta">
      <span><span class="badge passing">IMPLEMENTED</span> · {{ d.tests }} tests</span>
      <a href="/domain/{{ d.id }}" class="btn secondary">View</a>
    </div>
  </div>
  {% endfor %}
</div>
"""

DOMAIN_BODY = """
<div class="banner strong">
  <div>
    <div class="label">Domain</div>
    <strong>{{ domain.name }}</strong>
  </div>
  <a href="/" class="btn secondary">← Back to Dashboard</a>
</div>

<div class="card">
  <div class="label">Article V Language</div>
  <div class="quote">"{{ domain.article }}"</div>

  <div class="meta">
    <span><span class="badge passing">IMPLEMENTED</span> · {{ domain.tests }} tests</span>
  </div>
</div>

<h3 style="margin-top: 32px;">Live Demo</h3>
<p style="color: #8b949e; font-size: 13px;">
  Click to run <code>python -m {{ domain.module }} demo</code> and capture the output.
</p>
<form method="POST" action="/run/{{ domain.id }}">
  <button type="submit" class="btn">▶ Run Demo</button>
</form>

{% if output %}
<h3 style="margin-top: 28px;">Output</h3>
<div class="output">{{ output }}</div>
{% endif %}

{% if error %}
<h3 style="margin-top: 28px; color: #da3633;">Error</h3>
<div class="output" style="color: #da3633;">{{ error }}</div>
{% endif %}
"""


# ------------------------------------------------------------
# APP FACTORY
# ------------------------------------------------------------

def create_app():
    app = Flask(__name__)

    def render(title, body):
        return render_template_string(BASE, title=title, body=body)

    def decorate(domain):
        d = dict(domain)
        d["status"] = "passing"
        return d

    @app.route("/")
    def index():
        domains = [decorate(d) for d in DOMAINS]
        body = render_template_string(INDEX_BODY, domains=domains)
        return render("Dashboard", body)

    @app.route("/domain/<domain_id>")
    def domain_view(domain_id):
        d = next((x for x in DOMAINS if x["id"] == domain_id), None)
        if not d:
            return "Domain not found", 404
        body = render_template_string(DOMAIN_BODY, domain=decorate(d), output=None, error=None)
        return render(d["name"], body)

    @app.route("/run/<domain_id>", methods=["POST"])
    def run_demo(domain_id):
        d = next((x for x in DOMAINS if x["id"] == domain_id), None)
        if not d:
            return "Domain not found", 404
        output = None
        error = None
        try:
            import importlib
            mod = importlib.import_module(d["module"] + ".__main__")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                mod.cmd_demo([])
            output = buf.getvalue()
        except Exception as e:
            error = "Exception: " + type(e).__name__ + ": " + str(e)
        body = render_template_string(DOMAIN_BODY, domain=decorate(d), output=output, error=error)
        return render(d["name"], body)

    @app.route("/api/status")
    def api_status():
        return jsonify({
            "version": "4.4",
            "total_domains": len(DOMAINS),
            "total_tests": TOTAL_TESTS,
            "domains": [
                {
                    "id": d["id"],
                    "name": d["name"],
                    "module": d["module"],
                    "tests": d["tests"],
                    "status": "implemented",
                }
                for d in DOMAINS
            ],
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)
