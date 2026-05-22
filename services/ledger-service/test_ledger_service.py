import pytest
import importlib
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

MEDIA_TEST = {
    "media_id": "MED-001",
    "hash": "sha256:" + "a" * 64,
    "score": 0.42,
    "timestamp": "2026-05-22T14:00:00Z"
}

def make_mock_w3(connected=True):
    mock_w3 = MagicMock()
    mock_w3.is_connected.return_value = connected
    mock_w3.eth.get_transaction_count.return_value = 1
    mock_w3.eth.account.from_key.return_value = MagicMock(address="0xABC")
    mock_w3.eth.account.sign_transaction.return_value = MagicMock(
        rawTransaction=bytes([0xde, 0xad, 0xbe, 0xef])
    )
    mock_w3.eth.send_raw_transaction.return_value = bytes([0xde, 0xad, 0xbe, 0xef])
    mock_w3.to_wei.return_value = 50000000000
    return mock_w3

def make_mock_contract():
    mock_contract = MagicMock()
    mock_contract.functions.certifierMedia.return_value.build_transaction.return_value = {}
    mock_contract.functions.verifierMedia.return_value.call.return_value = True
    return mock_contract

def test_health_connecte():
    mock_w3 = make_mock_w3(connected=True)
    with patch("main.get_web3", return_value=mock_w3):
        import main
        client = TestClient(main.app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["blockchain_connected"] == True

def test_health_deconnecte():
    mock_w3 = make_mock_w3(connected=False)
    with patch("main.get_web3", return_value=mock_w3):
        import main
        client = TestClient(main.app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["blockchain_connected"] == False

def test_register_nominal():
    mock_w3 = make_mock_w3(connected=True)
    mock_contract = make_mock_contract()
    with patch("main.get_web3", return_value=mock_w3),          patch("main.get_contract", return_value=mock_contract):
        import main
        client = TestClient(main.app)
        response = client.post("/register", json=MEDIA_TEST)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "tx_id" in response.json()

def test_register_blockchain_inaccessible():
    mock_w3 = make_mock_w3(connected=False)
    with patch("main.get_web3", return_value=mock_w3):
        import main
        client = TestClient(main.app)
        response = client.post("/register", json=MEDIA_TEST)
        assert response.status_code == 503

def test_verify_nominal():
    mock_w3 = make_mock_w3(connected=True)
    mock_contract = make_mock_contract()
    with patch("main.get_web3", return_value=mock_w3),          patch("main.get_contract", return_value=mock_contract):
        import main
        client = TestClient(main.app)
        response = client.get("/verify/MED-001", params={"hash": "sha256:" + "a" * 64})
        assert response.status_code == 200
        assert response.json()["valid"] == True

def test_verify_blockchain_inaccessible():
    mock_w3 = make_mock_w3(connected=False)
    with patch("main.get_web3", return_value=mock_w3):
        import main
        client = TestClient(main.app)
        response = client.get("/verify/MED-001", params={"hash": "sha256:" + "a" * 64})
        assert response.status_code == 503
