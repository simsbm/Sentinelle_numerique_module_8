from fastapi import FastAPI
from pydantic import BaseModel
from web3 import Web3
import json, os
from dotenv import load_dotenv

# Charger variables d'environnement
load_dotenv()

RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Connexion à Ganache
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise RuntimeError(
        "Impossible de se connecter à la blockchain"
        "Vérifiez que Ganache est en cours d'exécution et que l'URL RPC est correcte."
        )

# Charger ABI
with open("abi.json") as f:
    abi = json.load(f)
abi = abi["abi"] 
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

app = FastAPI(title="Ledger Service")

class Media(BaseModel):
    media_id: str
    hash: str
    score: float
    timestamp: str

@app.post("/register")
def register(media: Media):
    # Conversion hash en bytes32
    hash_bytes = bytes.fromhex(media.hash.replace("0x", ""))

    # Construire transaction
    account = w3.eth.account.from_key(PRIVATE_KEY)
    tx = contract.functions.certifierMedia(media.media_id, hash_bytes).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 2000000,
        "gasPrice": w3.to_wei("50", "gwei")
    })

    # Signer et envoyer
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return {"tx_id": tx_hash.hex(), "status": "success"}

@app.get("/verify/{media_id}")
def verify(media_id: str, hash: str):
    hash_bytes = bytes.fromhex(hash.replace("0x", ""))
    valid = contract.functions.verifierMedia(media_id, hash_bytes).call()
    return {"valid": valid}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Ledger Service",
        "blockchain_connected": w3.is_connected()
        }