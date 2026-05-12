# ─────────────────────────────────────────────────────────────
# Dockerfile — audit-service
# Sentinelle Numérique | Groupe 8 — Blockchain d'Intégrité
# ─────────────────────────────────────────────────────────────

# Image de base légère Python 3.11
FROM python:3.11-slim

# Métadonnées du service
LABEL service="audit-service"
LABEL groupe="Groupe 8 — Blockchain d'Intégrité"
LABEL description="Journal des certifications et vérifications de la plateforme"

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier les dépendances en premier (optimise le cache Docker)
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY main.py .

# Créer le fichier audit.json vide si nécessaire au démarrage
# (sera créé automatiquement par l'app, mais bonne pratique)
RUN echo "[]" > audit.json

# Exposer le port du service
EXPOSE 8084

# Commande de démarrage du serveur FastAPI avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]
