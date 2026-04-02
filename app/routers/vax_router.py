from fastapi import APIRouter, HTTPException, Query
from app.schemas.vax import VaxCreate, VaxUpdate, VaxOut
import app.repositories.vax_repo as repo

router = APIRouter(prefix="/vax", tags=["vax"])

# Static routes

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

@router.get("/count")
async def count():
    return {"count": repo.count()}



@router.delete("/vacuum")
async def vacuum(retention_hours: int = Query(168, ge=0)):
    try:
        files = repo.vacuum(dry_run=True, retention_hours=retention_hours)
        print("would_delete:", files, "total: ", len(files))
        
        files = repo.vacuum(dry_run=False, retention_hours=retention_hours)

        return {"deleted": files, "total": len(files)}
    except FileNotFoundError:
        raise HTTPException(status_code=405, detail="No such table")

# Dynamic routes

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

# Optinals

# @router.get("/")
# def home():
#     return {"et-varginha": "Olá, mundo! Busquem conhecimento!"}

# @router.get("/history")
# def history():
#     return repo.history()

# @router.get("/version/{version}")
# def time_travel(version: int):
#     return repo.get_version(version)