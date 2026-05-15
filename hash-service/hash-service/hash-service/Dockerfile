# ──────────────────────────────────────────────────────────────
# Dockerfile — hash-service
# Module Blockchain d'Intégrité (Groupe 8) — Sentinelle Numérique
# ──────────────────────────────────────────────────────────────

# Image de base : Python 3.11 en version "slim" (légère, sans outils inutiles)
FROM python:3.11-slim

# ── Métadonnées de l'image ─────────────────────────────────────
LABEL maintainer="Groupe 8 — Sentinelle Numérique"
LABEL description="Service de calcul d'empreinte SHA-256 pour la certification blockchain"

# ── Répertoire de travail dans le conteneur ────────────────────
WORKDIR /app

# ── Copie et installation des dépendances ──────────────────────
# On copie d'abord requirements.txt seul pour profiter du cache Docker :
# si requirements.txt ne change pas, cette couche ne sera pas reconstruite.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ── Copie du code source de l'application ──────────────────────
COPY main.py .

# ── Exposition du port d'écoute ────────────────────────────────
# Le service écoute sur le port 8081 comme défini dans les specs
EXPOSE 8081

# ── Commande de démarrage ──────────────────────────────────────
# uvicorn démarre l'application FastAPI :
#   - "main:app" pointe vers l'objet "app" dans main.py
#   - --host 0.0.0.0 rend le service accessible depuis l'extérieur du conteneur
#   - --port 8081 correspond au port exposé ci-dessus
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
