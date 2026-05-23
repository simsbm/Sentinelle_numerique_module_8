

import hashlib
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import HTTPException


# Initialisation de l'application FastAPI

app = FastAPI(
    title="Hash Service Sentinelle Numérique",
    description="Calcule l'empreinte SHA-256 d'un rapport JSON .",
    version="1.0.0",
)

# Ajouter CORS pour permettre les appels du dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser tous les domaines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schéma de la requête entrante

class HashRequest(BaseModel):
    rapport_json: dict
    media_id: str



# Schéma de la réponse retournée

class HashResponse(BaseModel):
    media_id: str
    hash: str        
    algorithm: str   



# Endpoint principal : POST /hash
@app.post("/hash", response_model=HashResponse)
def calculer_hash(body: HashRequest) -> HashResponse:
    
    #Verifier que le rapport n'est pas vide
    if not body.rapport_json:
        raise HTTPException(
            status_code=400,
            detail="Le champ 'rapport_json' ne peut pas être vide.")
    
    # tri alphabétique des clés, séparateurs compacts

    json_canonique: str = json.dumps(
        body.rapport_json,
        sort_keys=True,       
        ensure_ascii=False,   
        separators=(",", ":") 
    )

    # Encodage en bytes UTF-8 
    donnees_bytes: bytes = json_canonique.encode("utf-8")

    # Calcul du hash SHA-256 via le module hashlib natif
    empreinte = hashlib.sha256(donnees_bytes)

    # Formatage du résultat : "sha256:<hex>"
    hash_final: str = f"sha256:{empreinte.hexdigest()}"

    return HashResponse(
        media_id=body.media_id,
        hash=hash_final,
        algorithm="SHA-256"
    )


# Route de santé 

@app.get("/health")
def health_check():
    """Vérifie que le service est opérationnel."""
    return {"status": "ok", "service": "hash-service"}

