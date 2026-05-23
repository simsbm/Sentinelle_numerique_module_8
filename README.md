# Sentinelle Numérique (Blockchain d'intégrité)

## Description

Sentinelle Numérique est une application de preuve d'intégrité basée sur une architecture microservices et une blockchain Ethereum locale. Le projet vise à garantir qu'un média ou un rapport n'a pas été modifié après sa certification en stockant son empreinte cryptographique dans un smart contract.

## Architecture

L’application est composée de plusieurs services Docker orchestrés avec `docker compose` :

- `ganache` : blockchain Ethereum locale (RPC sur `7545`)
- `hash-service` : calcule l'empreinte SHA-256 d'un rapport JSON
- `ledger-service` : enregistre et vérifie des empreintes sur la blockchain
- `verify-service` : vérifie l'intégrité d'un média en orchestrant `hash-service` et `ledger-service`
- `audit-service` : journalise les certifications et les vérifications dans un `audit.json`
- `dashboard` : interface web statique front-end

## Prérequis

- Docker
- Docker Compose
- Python 3.11 (pour exécuter les tests localement)

## Installation et exécution

À la racine du projet :

```bash
docker compose up --build
```

Quand tous les services sont démarrés :

- Dashboard : http://localhost
- Ganache RPC : http://localhost:7545
- hash-service : http://localhost:8081
- ledger-service : http://localhost:8082
- verify-service : http://localhost:8083
- audit-service : http://localhost:8084

Pour arrêter et supprimer les conteneurs :

```bash
docker compose down
```

## Configuration du ledger-service

Le `ledger-service` nécessite quelques variables d'environnement :

- `BLOCKCHAIN_RPC_URL` : URL du noeud Ganache, par exemple `http://ganache:7545`
- `CONTRACT_ADDRESS` : adresse du contrat déployé
- `PRIVATE_KEY` : clé privée d'un compte Ganache valide

Ces valeurs sont définies dans l'environnement Docker et peuvent être fournies via un fichier `.env` ou directement dans `docker-compose.yml`.

## Services et endpoints

### hash-service (`8081`)

- `POST /hash`
  - Corps : `{ "rapport_json": {...}, "media_id": "..." }`
  - Retourne : `{ "media_id": "...", "hash": "sha256:...", "algorithm": "SHA-256" }`
- `GET /health`
  - Retourne l'état du service

### ledger-service (`8082`)

- `POST /register`
  - Corps : `{ "media_id": "...", "hash": "sha256:...", "score": ..., "timestamp": "..." }`
  - Enregistre l'empreinte dans le smart contract
- `GET /verify/{media_id}`
  - Paramètre query : `hash`
  - Vérifie si le hash correspond à la valeur stockée sur la blockchain
- `GET /health`

### verify-service (`8083`)

- `POST /verify/{media_id}`
  - Corps : `{ "rapport_json": {...} }`
  - Recalcule le hash via `hash-service`, puis consulte `ledger-service`
  - Retourne un verdict d'intégrité
- `GET /health`

### audit-service (`8084`)

- `POST /log`
  - Corps : `{ "media_id": "...", "hash": "...", "tx_id": "...", "action": "..." }`
  - Enregistre une entrée d'audit
- `GET /audit`
  - Retourne toutes les entrées d'audit
- `GET /audit/{media_id}`
  - Retourne l'historique d'un média spécifique
- `GET /health`

## Structure du projet

- `docker-compose.yml` : orchestration des conteneurs
- `dashboard/` : interface web statique
- `services/hash-service/` : service de calcul SHA-256
- `services/ledger-service/` : service de connexion à Ganache et au smart contract
- `services/verify-service/` : service de vérification d'intégrité
- `services/audit-service/` : service de journalisation
- `services/ledger-service/contracts/` : contrat Solidity
- `services/ledger-service/build/contracts/` : artefacts compilés

## Tests

Chaque service inclut des tests unitaires sous `services/*/test_*.py`.

Exemple pour un service :

```bash
cd services/hash-service
pytest
```

## Notes

- Le smart contract est déployé localement via Ganache.
- Le dashboard est une interface statique qui doit se connecter aux services backend appropriés.
- Si le service `hash-service` ou `ledger-service` est indisponible, `verify-service` renvoie une erreur 502 ou 504.
