from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#teste de boite noire
def hash_nominal:
    reponse = client.post(
        "/hash",
        json={
            "rapport_json": {"key1": "value1", "key2": "value2"},
            "media_id": "media123"
        }
    )
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["media_id"] == "media123"
    assert data["algorithm"] == "SHA-256"
    assert len(data["hash"]) == 71

#test de cas limite
def hash_rapport_vide:
    reponse = client.post(
        "/hash",
        json={
            "rapport_json": {},
            "media_id": "media123"

        }
    )
    assert reponse.status_code == 400
    assert "vide" in response.json()["detail"]

#test de cannocalisation du json

def test_hash_cannocalisation():
    response_a = client.post(
        "/hash",
        json={
            "rapport_json": {"key1": "value1", "key2": "value2"},
            "media_id": "media123"
        })
    response_b = client.post(
        "/hash",
        json={
            "rapport_json": {"key2": "value2", "key1": "value1"},
            "media_id": "media123"
        })

    assert response_a.status_code = 200
    assert response_b.status_code = 200
    assert response_a.json()["hash"] == response_b.json()["hash"]

#Test determinisme
def test_hash_deterministe:
    response_a = client.post(
        "/hash",
        json={
            "rapport_json": {"key1": "value1", "key2": "value2"},
            "media_id": "media123"
        })
    response_b = client.post(
        "/hash",
        json={
            "rapport_json": {"key1": "value1", "key2": "value2"},
            "media_id": "media123"
        })

    assert response_a.status_code == 200
    assert response_b.status_code == 200
    assert response_a.json()["hash"] == response_b.json()["hash"]

#test de santé du service

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.json()["service"] == "hash-service"

