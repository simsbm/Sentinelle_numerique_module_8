
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [verify-service] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Verify Service",
    description="Service de vérification d'intégrité des médias via blockchain",
    version="1.0.0"
)

# URLs des services dépendants (utiliser les noms de services Docker)
HASH_SERVICE_URL = "http://hash-service:8081"
LEDGER_SERVICE_URL = "http://ledger-service:8082"

# Timeout pour les appels HTTP inter-services (en secondes)
HTTP_TIMEOUT = 10.0


class VerifyRequest(BaseModel):
    #Corps de la requête de vérification.
    rapport_json: dict[str, Any]


class VerifyResponse(BaseModel):
    #Réponse de vérification d'intégrité.
    valid: bool
    message: str
    certified_at: str | None = None
    hash: str | None = None
    tx_id: str | None = None




@app.post("/verify/{media_id}", response_model=VerifyResponse)
async def verify_media(media_id: str, body: VerifyRequest):
    
    logger.info(f"Vérification demandée pour media_id={media_id}")

    # calcul du hash du rapport JSON via hash-service
    hash_actuel = await _appeler_hash_service(body.rapport_json, media_id)

    
    # Comparer le hash avec la blockchain via ledger-service
    
    resultat = await _appeler_ledger_service(media_id, hash_actuel)

    # Reponse
    if resultat.get("valid"):
        logger.info(f"✅ media_id={media_id} — Média AUTHENTIQUE")
        return VerifyResponse(
            valid=True,
            message="Média authentique",
            certified_at=resultat.get("certified_at"),
            hash=hash_actuel,
            tx_id=resultat.get("tx_id")
        )
    else:
        logger.warning(f"media_id={media_id}: Média MODIFIÉ ou INCONNU")
        return VerifyResponse(
            valid=False,
            message="Alerte : média modifié ou inconnu",
            hash=hash_actuel
        )


async def _appeler_hash_service(rapport_json: dict, media_id: str) -> str:
    
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            logger.info(f"Appel hash-service: POST {HASH_SERVICE_URL}/hash")
            response = await client.post(
                f"{HASH_SERVICE_URL}/hash",
                json=rapport_json
            )
            response.raise_for_status()
            data = response.json()
            hash_value = data.get("hash")
            logger.info(f"hash-service a retourné le hash: {hash_value[:16]}...")
            return hash_value

    except httpx.ConnectError:
        logger.error("hash-service inaccessible (ConnectError)")
        raise HTTPException(
            status_code=502,
            detail="hash-service inaccessible. Vérifiez que hash-service est lancé sur le port 8081."
        )
    except httpx.TimeoutException:
        logger.error("hash-service timeout")
        raise HTTPException(status_code=504, detail="hash-service timeout")
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'appel à hash-service: {e}")
        raise HTTPException(status_code=502, detail=f"Erreur hash-service: {str(e)}")


async def _appeler_ledger_service(media_id: str, hash_actuel: str) -> dict:

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            url = f"{LEDGER_SERVICE_URL}/verify/{media_id}"
            logger.info(f"→ Appel ledger-service: GET {url}?hash={hash_actuel[:16]}...")
            response = await client.get(
                url,
                params={"hash": hash_actuel}
            )

            
            if response.status_code == 404:
                logger.info(f"ledger-service: media_id={media_id} non trouvé en blockchain")
                return {"match": False}

            response.raise_for_status()
            data = response.json()
            logger.info(f"ledger-service: match={data.get('match')}")
            return data

    except httpx.ConnectError:
        logger.error("ledger-service inaccessible (ConnectError)")
        raise HTTPException(
            status_code=502,
            detail="ledger-service inaccessible. Vérifiez que ledger-service est lancé sur le port 8082."
        )
    except httpx.TimeoutException:
        logger.error("ledger-service timeout")
        raise HTTPException(status_code=504, detail="ledger-service timeout")
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'appel à ledger-service: {e}")
        raise HTTPException(status_code=502, detail=f"Erreur ledger-service: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "verify-service", "port": 8083}