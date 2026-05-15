# ─────────────────────────────────────────────────────────────
# Dockerfile — verify-service
# Sentinelle Numérique | Groupe 8 — Blockchain d'Intégrité
# ─────────────────────────────────────────────────────────────

# Image de base légère Python 3.11
FROM python:3.11-slim

# Métadonnées du service
LABEL service="verify-service"
LABEL groupe="Groupe 8 — Blockchain d'Intégrité"
LABEL description="Service de vérification d'intégrité des médias via blockchain"

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier les dépendances en premier (optimise le cache Docker)
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY main.py .

# Exposer le port du service
EXPOSE 8083

# Commande de démarrage du serveur FastAPI avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8083"]
