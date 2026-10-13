import hashlib
import json
import os
import uuid

from fastapi.testclient import TestClient

TOKEN = "test-only-ps033-token"
os.environ["PS033_TOKEN_POLICIES_JSON"] = json.dumps({hashlib.sha256(TOKEN.encode()).hexdigest(): ["latency", "connectivity"]})

from src.services.app import app  # noqa: E402

client = TestClient(app)


def test_extra_request_fields_are_rejected():
    response = client.post("/v1/diagnostics/connectivity", headers={"Authorization": f"Bearer {TOKEN}"}, json={"request_id": str(uuid.uuid4()), "target": "lab-target.ps033.test", "url": "http://127.0.0.1/"})
    assert response.status_code == 422


def test_invalid_request_id_is_rejected():
    response = client.post("/v1/diagnostics/connectivity", headers={"Authorization": f"Bearer {TOKEN}"}, json={"request_id": "not-a-uuid"})
    assert response.status_code == 422
