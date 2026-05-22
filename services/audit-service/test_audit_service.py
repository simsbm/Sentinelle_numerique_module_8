import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient
from main import app, AUDIT_FILE

client = TestClient(app)

def setup_function():
    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()

def teardown_function():
    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()

ENTREE_TEST = {
    "media_id": "MED-001",
    "hash": "sha256:abc123def456",
    "tx_id": "0xdeadbeef",
    "action": "certification"
}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "audit-service"

def test_enregistrer_log():
    response = client.post("/log", json=ENTREE_TEST)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["entry_id"] == 0

def test_log_timestamp_auto():
    entree = {
        "media_id": "MED-002",
        "hash": "sha256:xyz789",
        "tx_id": "0xABC",
        "action": "verification"
    }
    response = client.post("/log", json=entree)
    assert response.status_code == 200
    assert response.json()["success"] == True
    journal = json.loads(AUDIT_FILE.read_text())
    assert journal[0]["timestamp"] is not None

def test_audit_liste():
    client.post("/log", json=ENTREE_TEST)
    client.post("/log", json={**ENTREE_TEST, "media_id": "MED-002", "action": "verification"})
    response = client.get("/audit")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["entries"]) == 2

def test_audit_par_media():
    client.post("/log", json=ENTREE_TEST)
    client.post("/log", json={**ENTREE_TEST, "action": "verification"})
    response = client.get("/audit/MED-001")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for entry in data["entries"]:
        assert entry["media_id"] == "MED-001"

def test_audit_par_media_inexistant():
    response = client.get("/audit/MED-999")
    assert response.status_code == 404

def test_log_multiple_ordre_trie():
    client.post("/log", json={**ENTREE_TEST, "media_id": "MED-OLD", "timestamp": "2020-01-01T00:00:00Z"})
    client.post("/log", json={**ENTREE_TEST, "media_id": "MED-NEW", "timestamp": "2030-01-01T00:00:00Z"})
    response = client.get("/audit")
    data = response.json()
    assert data["entries"][0]["media_id"] == "MED-NEW"
    assert data["entries"][-1]["media_id"] == "MED-OLD"
