# Sentinelle Numérique — Groupe 8 | Branche `feature/verify-service`

> **Blockchain d'Intégrité** — Services de vérification et d'audit  
> Auteur : HAPPI | Groupe 8

---

## Services implémentés

### 1. `verify-service` — Port 8083

Compare le hash SHA-256 d'un rapport JSON avec celui enregistré en blockchain.

**Dépendances** :
- `hash-service` (port 8081) — fourni par MBEI
- `ledger-service` (port 8082) — fourni par MBEI

**Endpoint principal** :
```
POST /verify/{media_id}
Body: { "rapport_json": { ...le rapport du média... } }
```

**Réponse si média authentique** :
```json
{
  "valid": true,
  "message": "Média authentique",
  "certified_at": "2026-05-12T10:30:00+00:00",
  "hash": "a3f1...",
  "tx_id": "0xabc123..."
}
```

**Réponse si média modifié** :
```json
{
  "valid": false,
  "message": "Alerte : média modifié ou inconnu"
}
```

---

### 2. `audit-service` — Port 8084

Journal persistant (fichier `audit.json`) de toutes les certifications et vérifications.

**Endpoints** :

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/log` | Enregistre une entrée d'audit |
| `GET` | `/audit` | Liste toutes les entrées (timestamp décroissant) |
| `GET` | `/audit/{media_id}` | Entrées pour un média spécifique |
| `GET` | `/health` | Statut du service |

**Exemple POST /log** :
```json
{
  "media_id": "media_001",
  "hash": "a3f1c2d4...",
  "tx_id": "0xabc123...",
  "action": "CERTIFICATION",
  "timestamp": "2026-05-12T10:30:00+00:00"
}
```

---

## Tester sans hash-service ni ledger-service (mode mock)

Si MBEI n'a pas encore fini ses services, utilise les mocks fournis :

```bash
# Terminal 1 — Mock hash-service (port 8081)
cd verify-service
pip install fastapi uvicorn httpx
python mock_hash_service.py

# Terminal 2 — Mock ledger-service (port 8082)
python mock_ledger_service.py

# Terminal 3 — verify-service réel (port 8083)
uvicorn main:app --port 8083 --reload

# Terminal 4 — Tester !
# Étape 1 : Pré-certifier un média dans le mock ledger
curl -X POST http://localhost:8082/certify \
     -H "Content-Type: application/json" \
     -d '{"media_id": "media_001", "hash": "HASH_A_REMPLIR"}'

# Étape 2 : Vérifier via verify-service
curl -X POST http://localhost:8083/verify/media_001 \
     -H "Content-Type: application/json" \
     -d '{"rapport_json": {"url": "https://example.com", "score": 0.42}}'
```

---

## Lancer avec Docker

```bash
# verify-service
cd verify-service
docker build -t verify-service .
docker run -p 8083:8083 verify-service

# audit-service
cd audit-service
docker build -t audit-service .
docker run -p 8084:8084 audit-service
```

---

## Structure des fichiers

```
feature/verify-service/
├── verify-service/
│   ├── main.py                  # FastAPI — endpoint POST /verify/{media_id}
│   ├── requirements.txt         # fastapi, uvicorn, httpx
│   ├── Dockerfile               # python:3.11-slim, port 8083
│   ├── mock_hash_service.py     # Simulateur hash-service pour tests locaux
│   └── mock_ledger_service.py   # Simulateur ledger-service pour tests locaux
│
└── audit-service/
    ├── main.py                  # FastAPI — POST /log + GET /audit
    ├── requirements.txt         # fastapi, uvicorn
    └── Dockerfile               # python:3.11-slim, port 8084
```

---

## Choix techniques (conformes au Livrable 1)

- **httpx** : Bibliothèque async HTTP pour les appels inter-services (imposé par le projet)
- **FastAPI** : Framework REST rapide avec validation Pydantic automatique
- **json + pathlib** : Stockage fichier local pour audit-service (sans base de données)
- **Aucune dépendance externe** pour audit-service : 100% stdlib Python + FastAPI

---

## Pull Request

**Branche source** : `feature/verify-service`  
**Branche cible** : `develop`  
**Prévenir** : L'équipe dès la PR créée ✅
