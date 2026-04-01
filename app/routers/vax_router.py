from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from app.schemas.vax import VaxCreate, VaxUpdate, VaxOut
import app.repositories.vax_repo as repo

router = APIRouter(prefix="/vax", tags=["vax"])

@router.get("/")
def home():
    return {"et-varginha": "Olá, mundo! Busquem conhecimento!"}

# Static routes

@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    # 1. Verifica se o arquivo é CSV (opcional, mas recomendado)
    if not file.filename.endswith('.csv'):
        return {"error": "Formato inválido. Envie um arquivo CSV."}
    
    # 2. Lê o conteúdo do arquivo
    content = await file.read()
    
    return repo.insert(content)


@router.post("/insert", response_model=VaxOut, status_code=201)
def create(data: VaxCreate):
    return repo.insert(data)

@router.get("/all")
def list_vax(
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

@router.get("/count")
def count():
    return {"count": repo.count()}

@router.get("/history")
def history():
    return repo.history()

@router.get("/version/{version}")
def time_travel(version: int):
    return repo.get_version(version)

@router.get("/vacuum")
def vacuum_dry(retention_hours: int = Query(168, ge=0)):
    files = repo.vacuum(dry_run=True, retention_hours=retention_hours)
    return {"would_delete": files, "total": len(files)}

@router.delete("/vacuum")
def vacuum_run(retention_hours: int = Query(168, ge=0)):
    files = repo.vacuum(dry_run=False, retention_hours=retention_hours)
    return {"deleted": files, "total": len(files)}

# Dynamic routes

@router.get("/{vax_id}", response_model=list[VaxOut])
def get(vax_id: int):
    record = repo.get_by_id(vax_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Vax not found")
    
    print("retornando...",type(record))
    return record

@router.patch("/{vax_id}")
def update(vax_id: int, data: VaxUpdate):
    updated = repo.update(vax_id, data)
    if not updated:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    return {"updated": True}

@router.put("/{vax_id}")
def upsert(vax_id: int, data: VaxCreate):
    return repo.upsert(data, vax_id=vax_id)

@router.delete("/{vax_id}")
def delete(vax_id: int):
    repo.delete(vax_id)
    return {"deleted": True}