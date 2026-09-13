"""Tests for the ACI Dashboard Flask app."""

import html as html_module
import pytest
from aci_dashboard import create_app
from aci_dashboard.app import DOMAINS, TOTAL_TESTS


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "ACI Dashboard" in html
    assert "Eight-Domain Stack" in html


def test_index_lists_all_eight_domains(client):
    r = client.get("/")
    # Flask/Jinja auto-escapes "&" to "&amp;" — unescape before matching
    html_text = html_module.unescape(r.get_data(as_text=True))
    for d in DOMAINS:
        assert d["name"] in html_text


def test_domain_view_loads(client):
    r = client.get("/domain/governance")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Governance" in html
    assert "Run Demo" in html


def test_domain_view_404_for_unknown(client):
    r = client.get("/domain/not_a_real_domain")
    assert r.status_code == 404


def test_run_demo_returns_output(client):
    r = client.post("/run/governance")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Governance" in html


def test_run_demo_all_domains_execute(client):
    for d in DOMAINS:
        r = client.post("/run/" + d["id"])
        assert r.status_code == 200, "Failed for: " + d["id"]
        html = r.get_data(as_text=True)
        assert "Exception" not in html, "Exception raised for: " + d["id"]


def test_api_status(client):
    r = client.get("/api/status")
    assert r.status_code == 200
    data = r.get_json()
    assert data["total_domains"] == 8
    assert len(data["domains"]) == 8
    assert data["total_tests"] == TOTAL_TESTS


def test_api_status_domain_shape(client):
    r = client.get("/api/status")
    data = r.get_json()
    for d in data["domains"]:
        assert "id" in d
        assert "name" in d
        assert "module" in d
        assert "tests" in d
        assert d["status"] == "implemented"


def test_total_tests_matches_sum():
    assert TOTAL_TESTS == sum(d["tests"] for d in DOMAINS)
    assert TOTAL_TESTS >= 96
