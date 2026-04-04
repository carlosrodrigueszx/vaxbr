from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.schemas.vax import VaxCreate, VaxUpdate, VaxOut
from app.core.logger import get_logger
import app.repositories.vax_repo as repo

logger = get_logger(__name__)
router = APIRouter(prefix="/vax", tags=["vax"])

READPATH = "app/tmp/vax"


# Rotas estáticas

@router.post("/insert", response_model=VaxOut, status_code=201)
async def create(data: VaxCreate):
    logger.info("Inserindo nova vacina: %s", data.model_dump())
    result = repo.insert(data)
    logger.info("Vacina inserida com sucesso: vax_id=%s", result["vax_id"])
    return result


@router.get("/all")
async def list_all(
    page:      int       = Query(1,    ge=1),
    page_size: int       = Query(10,   ge=1, le=100),
    illness:   str | None = Query(None),
    target:    str | None = Query(None),
):
    logger.info("Listando vacinas — page=%s page_size=%s illness=%s target=%s",
                page, page_size, illness, target)
    return repo.list_all(page=page, page_size=page_size, illness=illness, target=target)


@router.get("/count")
async def count():
    total = repo.count()
    logger.info("Contagem de vacinas: %s", total)
    return {"count": total}


@router.get("/export/csv")
def export_csv(filename: str):
    logger.info("Exportando CSV: %s.csv", filename)
    return StreamingResponse(
        repo.parquet_to_csv_stream(READPATH),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
    )


@router.get("/export/zip")
def export_zip(filename: str):
    logger.info("Exportando ZIP: %s.zip", filename)
    return StreamingResponse(
        repo.parquet_to_zip_stream(READPATH),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}.zip"},
    )


@router.get("/vacuum")
async def vacuum_preview(retention_hours: int = Query(168, ge=0)):
    logger.info("Inspecionando vacuum — retention_hours=%s", retention_hours)
    try:
        files = repo.vacuum(dry_run=True, retention_hours=retention_hours)
        logger.info("Vacuum (dry_run): %s arquivos seriam deletados", len(files))
        return {"would_delete": files, "total": len(files)}
    except Exception as e:
        logger.error("Erro no vacuum (dry_run): %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vacuum")
async def vacuum_run(
    retention_hours: int  = Query(168, ge=0),
    enforce:         bool = Query(False),
):
    if retention_hours == 0 and not enforce:
        logger.warning("Vacuum bloqueado: retention_hours=0 sem enforce=true")
        raise HTTPException(
            status_code=400,
            detail="retention_hours=0 apaga todo o histórico. Passe enforce=true para confirmar.",
        )
    logger.info("Executando vacuum — retention_hours=%s enforce=%s", retention_hours, enforce)
    try:
        files = repo.vacuum(dry_run=False, retention_hours=retention_hours)
        logger.info("Vacuum concluído: %s arquivos deletados", len(files))
        return {"deleted": files, "total": len(files)}
    except Exception as e:
        logger.error("Erro no vacuum: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Rotas dinâmicas (com {vax_id}) 

@router.get("/{vax_id}", response_model=list[VaxOut])
async def get(vax_id: int):
    logger.info("Buscando vacina vax_id=%s", vax_id)
    record = repo.get_by_id(vax_id)
    if not record:
        logger.warning("Vacina não encontrada: vax_id=%s", vax_id)
        raise HTTPException(status_code=404, detail="Vax not found")
    logger.info("Vacina encontrada: vax_id=%s", vax_id)
    return record


@router.patch("/{vax_id}")
async def update(vax_id: int, data: VaxUpdate):
    logger.info("Atualizando vacina vax_id=%s — campos: %s", vax_id, data.model_dump(exclude_none=True))
    updated = repo.update(vax_id, data)
    if not updated:
        logger.warning("Atualização falhou: vax_id=%s não encontrado ou sem campos", vax_id)
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    logger.info("Vacina atualizada com sucesso: vax_id=%s", vax_id)
    return {"updated": True}


@router.put("/{vax_id}")
async def upsert(vax_id: int, data: VaxCreate):
    logger.info("Upsert na vacina vax_id=%s", vax_id)
    result = repo.upsert(data, vax_id=vax_id)
    logger.info("Upsert concluído: vax_id=%s", vax_id)
    return result


@router.delete("/{vax_id}")
async def delete(vax_id: int):
    logger.info("Deletando vacina vax_id=%s", vax_id)
    if not repo._exists(vax_id):
        logger.warning("Vacina não encontrada para deletar: vax_id=%s", vax_id)
        raise HTTPException(status_code=404, detail="Vax not found")
    repo.delete(vax_id)
    logger.info("Vacina deletada com sucesso: vax_id=%s", vax_id)
    return {"deleted": True}
