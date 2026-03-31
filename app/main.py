from fastapi import FastAPI
from app.routers import vax_router

app = FastAPI(title="VaxBR Lakehouse API", swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}})

app.include_router(vax_router.router)
