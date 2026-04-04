import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/hash", tags=["hash"])

SUPPORTED_ALGORITHMS = {
    "MD5":    "md5",
    "SHA-1":  "sha1",
    "SHA-256": "sha256",
}


class HashRequest(BaseModel):
    value: str
    algorithm: str  # "MD5", "SHA-1" ou "SHA-256"


class HashResponse(BaseModel):
    value: str
    algorithm: str
    hash: str


@router.post("/", response_model=HashResponse)
def generate_hash(body: HashRequest):
    logger.info("Gerando hash — algorithm=%s", body.algorithm)

    if body.algorithm not in SUPPORTED_ALGORITHMS:
        logger.warning("Algoritmo inválido solicitado: %s", body.algorithm)
        raise HTTPException(
            status_code=400,
            detail=f"Algoritmo inválido: '{body.algorithm}'. Use MD5, SHA-1 ou SHA-256.",
        )

    h = hashlib.new(SUPPORTED_ALGORITHMS[body.algorithm], body.value.encode()).hexdigest()
    logger.info("Hash gerado com sucesso — algorithm=%s", body.algorithm)
    return HashResponse(value=body.value, algorithm=body.algorithm, hash=h)
