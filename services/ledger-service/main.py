from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from web3 import Web3
import json, os
from dotenv import load_dotenv

# Charger variables d'environnement
load_dotenv()

RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Connexion à la blockchain
def get_web3():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    return w3


def get_contract(w3):
    with open("MediaCertifierABI.json") as f:
        abi = json.load(f)
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    return contract

app = FastAPI(title="Ledger Service")

class Media(BaseModel):
    media_id: str
    hash: str
    score: float
    timestamp: str

@app.post("/register")
def register(media: Media):
    w3 = get_web3()
    if not w3.is_connected():
        raise HTTPException(status_code=503, detail="Blockchain inaccessible")
    contract = get_contract(w3)
    try:
        hash_str = media.hash.replace("sha256:","").replace("0x","")
        hash_bytes = bytes.fromhex(hash_str).ljust(32, b'\x00')[:32]
        account = w3.eth.account.from_key(PRIVATE_KEY)
        tx = contract.functions.certifierMedia(media.media_id, hash_bytes).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 2000000,
            "gasPrice": w3.to_wei("50", "gwei")
        })
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return {"tx_id": tx_hash.hex(), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la transaction: {str(e)}")

    
@app.get("/verify/{media_id}")
def verify(media_id: str, hash: str):
    w3 = get_web3()
    if not w3.is_connected():
        raise HTTPException(status_code=503, detail="Blockchain inaccessible")
    contract = get_contract(w3)
    try:
        hash_str = hash.replace("sha256:", "").replace("0x", "")
        hash_bytes = bytes.fromhex(hash_str).ljust(32, b"\x00")[:32]
        hash_bytes = hash_bytes.ljust(32, b'\x00')[:32]
        valid = contract.functions.verifierMedia(media_id, hash_bytes).call()
        return {"valid": valid} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification: {str(e)}")


@app.get("/health")
def health():
    w3 = get_web3()
    return {
        "status": "ok",
        "service": "Ledger Service",
        "blockchain_connected": w3.is_connected()
        }