from fastapi import FastAPI
from app.routers import vax_router
from app.routers import hash_router
from app.core.logger import get_logger 

logger = get_logger(__name__)

app = FastAPI(title="VaxBR API", swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}})

app.include_router(vax_router.router)
app.include_router(hash_router.router)

logger.info("VaxBR API iniciada com sucesso")
