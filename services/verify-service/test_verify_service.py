import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from main import app

client = TestClient(app)

RAPPORT_TEST = {"media_id": "MED-001", "score": 42, "verdict": "Faible"}
HASH_TEST = "sha256:abc123def456"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "verify-service"

@pytest.mark.anyio
async def test_verify_media_authentique():
    async def mock_hash(rapport_json, media_id):
        return HASH_TEST
    async def mock_ledger(media_id, hash_actuel):
        return {"valid": True, "certified_at": "2026-05-01"}
    with patch("main._appeler_hash_service", side_effect=mock_hash), \
         patch("main._appeler_ledger_service", side_effect=mock_ledger):
        response = client.post("/verify/MED-001", json={"rapport_json": RAPPORT_TEST})
        assert response.status_code == 200
        assert response.json()["valid"] == True

@pytest.mark.anyio
async def test_verify_media_modifie():
    async def mock_hash(rapport_json, media_id):
        return HASH_TEST
    async def mock_ledger(media_id, hash_actuel):
        return {"valid": False}
    with patch("main._appeler_hash_service", side_effect=mock_hash), \
         patch("main._appeler_ledger_service", side_effect=mock_ledger):
        response = client.post("/verify/MED-001", json={"rapport_json": RAPPORT_TEST})
        assert response.status_code == 200
        assert response.json()["valid"] == False

@pytest.mark.anyio
async def test_verify_hash_service_inaccessible():
    with patch("main._appeler_hash_service", new=AsyncMock(side_effect=HTTPException(status_code=502, detail="hash-service inaccessible."))):
        response = client.post("/verify/MED-001", json={"rapport_json": RAPPORT_TEST})
        assert response.status_code == 502

@pytest.mark.anyio
async def test_verify_rapport_vide():
    with patch("main._appeler_hash_service", new=AsyncMock(side_effect=HTTPException(status_code=502, detail="rapport vide"))):
        response = client.post("/verify/MED-001", json={"rapport_json": {}})
        assert response.status_code == 502
