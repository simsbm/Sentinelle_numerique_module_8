"""
audit-service — Sentinelle Numérique (Groupe 8)
Port : 8084

Rôle : Journal de toutes les certifications et vérifications effectuées
       par la plateforme Sentinelle Numérique.

Stockage : Fichier JSON local (audit.json) — sans base de données.

Endpoints :
  - POST /log  : Enregistrer une entrée d'audit
  - GET  /audit : Lister toutes les entrées (triées par timestamp décroissant)

Auteur : Groupe 8 — Blockchain d'Intégrité
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ─────────────────────────────────────────────────────────────
# Configuration du logger
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [audit-service] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Chemin du fichier de journal JSON
# ─────────────────────────────────────────────────────────────
AUDIT_FILE = Path("audit.json")


app = FastAPI(
    title="Audit Service — Sentinelle Numérique",
    description="Journal des certifications et vérifications de la plateforme",
    version="1.0.0"
)


# ─────────────────────────────────────────────────────────────
# Modèles Pydantic
# ─────────────────────────────────────────────────────────────

class LogEntry(BaseModel):
    """Entrée d'audit à enregistrer."""
    media_id: str
    hash: str
    tx_id: str
    action: str       # Ex: "CERTIFICATION", "VERIFICATION", "ECHEC_TRANSACTION"
    timestamp: Optional[str] = None  # ISO 8601 — auto-généré si absent


class LogResponse(BaseModel):
    """Réponse après enregistrement d'une entrée."""
    success: bool
    message: str
    entry_id: int     # Index de l'entrée dans le fichier JSON


# ─────────────────────────────────────────────────────────────
# Fonctions utilitaires de lecture/écriture du fichier audit.json
# ─────────────────────────────────────────────────────────────

def _lire_journal() -> list[dict]:
    """
    Lit le fichier audit.json et retourne la liste des entrées.
    Si le fichier n'existe pas, retourne une liste vide.

    Returns:
        Liste des entrées d'audit sous forme de dictionnaires
    """
    if not AUDIT_FILE.exists():
        logger.debug("audit.json non trouvé — initialisation avec liste vide")
        return []

    try:
        contenu = AUDIT_FILE.read_text(encoding="utf-8")
        if not contenu.strip():
            return []
        return json.loads(contenu)
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON dans audit.json: {e}")
        # En cas de fichier corrompu, on préserve le fichier et retourne vide
        return []


def _ecrire_journal(entries: list[dict]) -> None:
    """
    Écrit la liste des entrées dans audit.json.

    Args:
        entries : Liste complète des entrées à persister
    """
    AUDIT_FILE.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    logger.debug(f"audit.json mis à jour — {len(entries)} entrée(s)")


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Endpoint de santé pour Docker/orchestrateur."""
    nb_entrees = len(_lire_journal())
    return {
        "status": "ok",
        "service": "audit-service",
        "port": 8084,
        "audit_file": str(AUDIT_FILE.resolve()),
        "total_entries": nb_entrees
    }


@app.post("/log", response_model=LogResponse)
async def enregistrer_log(entry: LogEntry):
    """
    Enregistre une nouvelle entrée dans le journal d'audit.

    Si le timestamp n'est pas fourni, il est généré automatiquement
    au moment de la réception de la requête (UTC).

    Args:
        entry : L'entrée d'audit à enregistrer

    Returns:
        LogResponse confirmant l'enregistrement avec l'index de l'entrée
    """
    # Générer le timestamp automatiquement si absent
    if not entry.timestamp:
        entry.timestamp = datetime.now(timezone.utc).isoformat()

    # Lire le journal existant
    journal = _lire_journal()

    # Construire le dictionnaire de l'entrée à persister
    nouvelle_entree = {
        "media_id": entry.media_id,
        "hash": entry.hash,
        "tx_id": entry.tx_id,
        "action": entry.action,
        "timestamp": entry.timestamp
    }

    # Ajouter la nouvelle entrée
    journal.append(nouvelle_entree)
    index = len(journal) - 1

    # Persister dans audit.json
    try:
        _ecrire_journal(journal)
    except Exception as e:
        logger.error(f"Impossible d'écrire dans audit.json: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture du journal: {str(e)}")

    logger.info(
        f"✅ Log enregistré — action={entry.action}, "
        f"media_id={entry.media_id}, "
        f"hash={entry.hash[:16]}..., "
        f"tx_id={entry.tx_id}"
    )

    return LogResponse(
        success=True,
        message=f"Entrée enregistrée avec succès (index: {index})",
        entry_id=index
    )


@app.get("/audit")
async def lister_audit():
    """
    Retourne la liste complète des entrées du journal d'audit,
    triées par timestamp décroissant (plus récent en premier).

    Returns:
        Dictionnaire avec le nombre total d'entrées et la liste triée
    """
    journal = _lire_journal()

    # Trier par timestamp décroissant (ISO 8601 est triable lexicographiquement)
    journal_trie = sorted(
        journal,
        key=lambda e: e.get("timestamp", ""),
        reverse=True
    )

    logger.info(f"Consultation du journal — {len(journal_trie)} entrée(s) retournée(s)")

    return {
        "total": len(journal_trie),
        "entries": journal_trie
    }


@app.get("/audit/{media_id}")
async def lister_audit_par_media(media_id: str):
    """
    Retourne toutes les entrées d'audit pour un media_id spécifique.
    Utile pour tracer l'historique complet d'un média particulier.

    Args:
        media_id : Identifiant du média à rechercher

    Returns:
        Liste des entrées liées à ce media_id, triées par timestamp décroissant
    """
    journal = _lire_journal()

    # Filtrer les entrées pour ce media_id
    entrees_media = [e for e in journal if e.get("media_id") == media_id]

    # Trier par timestamp décroissant
    entrees_media = sorted(
        entrees_media,
        key=lambda e: e.get("timestamp", ""),
        reverse=True
    )

    if not entrees_media:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune entrée d'audit trouvée pour media_id='{media_id}'"
        )

    logger.info(f"Consultation pour media_id={media_id} — {len(entrees_media)} entrée(s)")

    return {
        "media_id": media_id,
        "total": len(entrees_media),
        "entries": entrees_media
    }
