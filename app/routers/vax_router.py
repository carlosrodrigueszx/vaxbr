from fastapi import APIRouter, HTTPException, Query
from app.schemas.vax import VaxCreate, VaxUpdate, VaxOut
import app.repositories.vax_repo as repo
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/vax", tags=["vax"])

READPATH = "app/tmp/vax"

# Static

@router.post("/insert", response_model=VaxOut, status_code=201)
async def create(data: VaxCreate):
    return repo.insert(data)

@router.post("/create_items", response_model=VaxOut, status_code=201)
async def create_items(items: list[VaxCreate]):
    print(type(items))
    for item in items:
        yield repo.insert(item)
    return 

@router.get("/all")
async def all(
    page:      int            = Query(1,   ge=1),
    page_size: int            = Query(10,  ge=1, le=100),
    illness:   str  = Query(None),
    target:    str  = Query(None),
):
    return repo.list_all(
        page=page,
        page_size=page_size,
        illness=illness,
        target=target,
    )

@router.get("/export/csv")
def export_csv(filename: str):
    generator = repo.parquet_to_csv_stream(READPATH)

    return StreamingResponse(
        generator,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.csv"
        }
    )

@router.get("/export/zip")
def export_zip(filename: str):
    
    gen = repo.parquet_to_zip_stream(READPATH) 

    return StreamingResponse(
        gen,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.zip"
        }
    )

@router.get("/count")
async def count():
    return {"count": repo.count()}

# inspeciona
@router.get("/vacuum")
async def vacuum_preview(retention_hours: int = Query(168, ge=0)):
    try:
        files = repo.vacuum(dry_run=True, retention_hours=retention_hours)
        return {"would_delete": files, "total": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# deleta
@router.delete("/vacuum")
async def vacuum_run(
    retention_hours: int = Query(168, ge=0),
    enforce: bool        = Query(False),   # proteção extra: precisa passar enforce=true
):
    if retention_hours == 0 and not enforce:
        raise HTTPException(
            status_code=400,
            detail="retention_hours=0 apaga todo o histórico. Passe enforce=true para confirmar."
        )
    try:
        files = repo.vacuum(dry_run=False, retention_hours=retention_hours)
        return {"deleted": files, "total": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dynamic

@router.get("/{vax_id}", response_model=list[VaxOut])
async def get(vax_id: int):
    record = repo.get_by_id(vax_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Vax not found")
    
    print("retornando...",type(record))
    return record

@router.patch("/{vax_id}")
async def update(vax_id: int, data: VaxUpdate):
    updated = repo.update(vax_id, data)

    if not updated:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    return {"updated": True}

@router.put("/{vax_id}")
async def upsert(vax_id: int, data: VaxCreate):
    return repo.upsert(data, vax_id=vax_id)

@router.delete("/{vax_id}")
async def delete(vax_id: int):
    repo.delete(vax_id)
    return {"deleted": True}

