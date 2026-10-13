import hashlib
import os
import uuid

from fastapi.testclient import TestClient

# Configure a deterministic lab-only token before the settings module is imported.
TOKEN = "test-only-ps033-token"
os.environ["PS033_TOKEN_POLICIES_JSON"] = __import__("json").dumps({hashlib.sha256(TOKEN.encode()).hexdigest(): ["latency", "connectivity"]})

from src.services.app import app  # noqa: E402

client = TestClient(app)


def test_protected_endpoint_rejects_missing_token():
    response = client.post("/v1/diagnostics/latency", json={"request_id": str(uuid.uuid4())})
    assert response.status_code == 401


def test_protected_endpoint_rejects_invalid_token():
    response = client.post("/v1/diagnostics/latency", headers={"Authorization": "Bearer wrong"}, json={})
    assert response.status_code == 401


def test_authorized_latency_returns_explicit_simulation():
    response = client.post("/v1/diagnostics/latency", headers={"Authorization": f"Bearer {TOKEN}"}, json={})
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "latency"
    assert body["mode"] == "simulated"
    assert body["details"]["measurement"] == "simulated_fixture"


def test_token_cannot_invoke_service_outside_its_permissions():
    response = client.post("/v1/diagnostics/routing", headers={"Authorization": f"Bearer {TOKEN}"}, json={})
    assert response.status_code == 403


def test_connectivity_rejects_unapproved_target():
    response = client.post("/v1/diagnostics/connectivity", headers={"Authorization": f"Bearer {TOKEN}"}, json={"target": "example.com"})
    assert response.status_code == 422


def test_unknown_route_is_not_success():
    response = client.post("/v1/diagnostics/not-a-service", headers={"Authorization": f"Bearer {TOKEN}"}, json={})
    assert response.status_code == 404
