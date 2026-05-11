"""
hash-service — Serveur FastAPI de calcul d'empreinte SHA-256
Module Blockchain d'Intégrité (Groupe 8) — Sentinelle Numérique
Port : 8081
"""

import hashlib
import json

from fastapi import FastAPI
from pydantic import BaseModel

# ──────────────────────────────────────────────
# Initialisation de l'application FastAPI
# ──────────────────────────────────────────────
app = FastAPI(
    title="Hash Service — Sentinelle Numérique",
    description="Calcule l'empreinte SHA-256 d'un rapport JSON (canonicalisé).",
    version="1.0.0",
)


# ──────────────────────────────────────────────
# Schéma de la requête entrante
# Le body attendu contient un champ "rapport_json"
# qui est un dictionnaire JSON arbitraire.
# ──────────────────────────────────────────────
class HashRequest(BaseModel):
    rapport_json: dict


# ──────────────────────────────────────────────
# Schéma de la réponse retournée
# ──────────────────────────────────────────────
class HashResponse(BaseModel):
    hash: str        # ex. "sha256:a3f1..."
    algorithm: str   # toujours "SHA-256"


# ──────────────────────────────────────────────
# Endpoint principal : POST /hash
# ──────────────────────────────────────────────
@app.post("/hash", response_model=HashResponse)
def calculer_hash(body: HashRequest) -> HashResponse:
    """
    Reçoit un rapport JSON, le canonicalise (tri alphabétique des clés),
    calcule son empreinte SHA-256 et retourne le hash préfixé "sha256:".

    Étapes :
      1. Sérialisation JSON avec tri des clés (sort_keys=True) — canonicalisation
      2. Encodage en UTF-8 pour obtenir des bytes
      3. Calcul SHA-256 avec hashlib (bibliothèque native Python)
      4. Retour du digest hexadécimal préfixé "sha256:"
    """

    # Étape 1 — Canonicalisation : tri alphabétique des clés, séparateurs compacts
    json_canonique: str = json.dumps(
        body.rapport_json,
        sort_keys=True,       # garantit un ordre déterministe des clés
        ensure_ascii=False,   # préserve les caractères Unicode (accents, etc.)
        separators=(",", ":") # supprime les espaces superflus → empreinte stable
    )

    # Étape 2 — Encodage en bytes UTF-8 (requis par hashlib)
    donnees_bytes: bytes = json_canonique.encode("utf-8")

    # Étape 3 — Calcul du hash SHA-256 via le module hashlib natif
    empreinte = hashlib.sha256(donnees_bytes)

    # Étape 4 — Formatage du résultat : "sha256:<digest_hex>"
    hash_final: str = f"sha256:{empreinte.hexdigest()}"

    return HashResponse(hash=hash_final, algorithm="SHA-256")


# ──────────────────────────────────────────────
# Route de santé — utile pour les checks Docker
# ──────────────────────────────────────────────
@app.get("/health")
def health_check():
    """Vérifie que le service est opérationnel."""
    return {"status": "ok", "service": "hash-service"}
