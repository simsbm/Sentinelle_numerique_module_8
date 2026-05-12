"""
mock_hash_service.py — Sentinelle Numérique (Groupe 8)

Simulateur du hash-service pour tester verify-service
de manière INDÉPENDANTE, sans avoir besoin que hash-service
soit réellement lancé.

Utilisation :
    # Terminal 1 — lancer le mock sur le port 8081
    python mock_hash_service.py

    # Terminal 2 — lancer verify-service sur le port 8083
    uvicorn main:app --port 8083

    # Terminal 3 — tester
    curl -X POST http://localhost:8083/verify/media_001 \
         -H "Content-Type: application/json" \
         -d '{"rapport_json": {"url": "https://example.com", "score": 0.42}}'

Réponse du mock :
    Il calcule un vrai SHA-256 du JSON reçu avec hashlib,
    exactement comme le ferait le vrai hash-service.
"""

import hashlib
import json
import uvicorn
from fastapi import FastAPI, Request

# ─────────────────────────────────────────────────────────────
# Application FastAPI simulant hash-service
# ─────────────────────────────────────────────────────────────
mock_app = FastAPI(title="MOCK hash-service", description="Simulateur pour tests locaux")


@mock_app.post("/hash")
async def mock_hash(request: Request):
    """
    Simule l'endpoint POST /hash du vrai hash-service.
    Calcule un vrai SHA-256 du corps JSON reçu.
    """
    body = await request.json()

    # Sérialisation JSON déterministe (trié) pour SHA-256 reproductible
    json_bytes = json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    hash_value = hashlib.sha256(json_bytes).hexdigest()

    print(f"[MOCK hash-service] Hash calculé: {hash_value[:16]}... pour body={str(body)[:60]}")
    return {"hash": hash_value, "algorithm": "SHA-256", "source": "MOCK"}


@mock_app.get("/health")
async def health():
    return {"status": "ok", "service": "MOCK hash-service", "port": 8081}


if __name__ == "__main__":
    print("=" * 60)
    print("  MOCK hash-service démarré sur http://localhost:8081")
    print("  Utilisez ce mock pour tester verify-service sans")
    print("  avoir besoin que hash-service soit réellement lancé.")
    print("=" * 60)
    uvicorn.run(mock_app, host="0.0.0.0", port=8081)
