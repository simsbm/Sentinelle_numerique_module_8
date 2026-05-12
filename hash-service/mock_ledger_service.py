"""
mock_ledger_service.py — Sentinelle Numérique (Groupe 8)

Simulateur du ledger-service pour tester verify-service
de manière INDÉPENDANTE, sans blockchain réelle.

Ce mock stocke en mémoire un registre local de hashs certifiés.
Il simule exactement l'interface de ledger-service.

Utilisation :
    # Terminal 1 — lancer le mock ledger sur le port 8082
    python mock_ledger_service.py

    # Puis pré-certifier un média pour tester le cas "authentique" :
    curl -X POST http://localhost:8082/certify \
         -H "Content-Type: application/json" \
         -d '{"media_id": "media_001", "hash": "VOTRE_HASH_ICI"}'
"""

import uvicorn
from fastapi import FastAPI
from datetime import datetime, timezone
from pydantic import BaseModel

mock_app = FastAPI(title="MOCK ledger-service", description="Simulateur blockchain pour tests")

# ─────────────────────────────────────────────────────────────
# Registre en mémoire (simule la blockchain)
# ─────────────────────────────────────────────────────────────
registre: dict[str, dict] = {}


class CertifyRequest(BaseModel):
    media_id: str
    hash: str


@mock_app.post("/certify")
async def mock_certify(body: CertifyRequest):
    """Simule l'inscription d'un hash en blockchain."""
    tx_id = f"0xMOCK{'a' * 8}{body.media_id[-4:] if len(body.media_id) >= 4 else '0000'}"
    registre[body.media_id] = {
        "hash": body.hash,
        "tx_id": tx_id,
        "certified_at": datetime.now(timezone.utc).isoformat()
    }
    print(f"[MOCK ledger] Certifié: media_id={body.media_id}, hash={body.hash[:16]}...")
    return {"tx_id": tx_id, "status": "MOCK_SUCCESS"}


@mock_app.get("/verify/{media_id}")
async def mock_verify(media_id: str, hash: str):
    """
    Simule la vérification d'un hash en blockchain.
    Retourne match=True si le hash correspond à celui certifié.
    """
    if media_id not in registre:
        print(f"[MOCK ledger] media_id={media_id} non trouvé")
        return {"match": False, "reason": "media_id non trouvé dans le registre"}

    enregistrement = registre[media_id]
    match = enregistrement["hash"] == hash

    print(f"[MOCK ledger] Vérification media_id={media_id}: match={match}")
    return {
        "match": match,
        "certified_at": enregistrement["certified_at"],
        "tx_id": enregistrement["tx_id"]
    }


@mock_app.get("/health")
async def health():
    return {"status": "ok", "service": "MOCK ledger-service", "port": 8082, "registre_size": len(registre)}


if __name__ == "__main__":
    print("=" * 60)
    print("  MOCK ledger-service démarré sur http://localhost:8082")
    print("  Registre en mémoire — simulé sans blockchain réelle.")
    print("=" * 60)
    uvicorn.run(mock_app, host="0.0.0.0", port=8082)
