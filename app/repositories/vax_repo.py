import app.db as db
from app.schemas.vax import VaxCreate, VaxUpdate
import io

WRITE_PATH = "app/tmp/vax"
FILE_SEQ   = "app/data/.seq"
WRITER_PROP = "ZSTD"

_id = db.GenID(FILE_SEQ, delta_table_path=WRITE_PATH, id_column="vax_id")

def _latest() -> db.DeltaTable:
    return db.DeltaTable(WRITE_PATH)

def insert(data: VaxCreate) -> dict:
    df = db.pd.DataFrame([
        {
            "vax_id": _id.get_next(),
            **data.model_dump()
        }
    ])
    db.write_deltalake(WRITE_PATH, df, mode="append")
    return df.iloc[0].to_dict()

def get_by_id(vax_id: int):
    table = _latest().to_pyarrow_table(
        filters=[("vax_id", "=", vax_id)]
    )

    if table.num_rows == 0:
        return None
    
    return table.to_pylist()

def list_all(
    page: int = 1,
    page_size: int = 10,
    illness: str | None = None,
    target: str | None = None,
):

    expr = None

    if illness and target:
        expr = (db.pdt.field("illness") == illness) & (db.pdt.field("target") == target)
    elif illness:
        expr = db.pdt.field("illness") == illness
    elif target:
        expr = db.pdt.field("target") == target

    dataset = _latest().to_pyarrow_dataset()

    # lê em batches para não carregar tudo de uma vez
    batches = dataset.to_batches(
        batch_size=page_size,
        filter=expr,
    )

    # filtra batches vazios e concatena em uma tabela única
    batch_list = [b for b in batches if b.num_rows > 0]

    if not batch_list:
        return {
            "data": [],
            "page": page,
            "page_size": page_size,
            "total_records": 0,
            "total_pages": 0,
        }

    full_table   = db.pa.Table.from_batches(batch_list)

    total_records = full_table.num_rows
    total_pages   = max(1, -(-total_records // page_size))

    if page < 1 or page > total_pages:
        return {
            "data": [],
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages,
        }

    # fatiamento real por página
    start = (page - 1) * page_size
    # end   = start + page_size
    page_table = full_table.slice(start, min(page_size, total_records - start))

    return {
        "data": page_table.to_pylist(),
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": total_pages,
    }


def count() -> int:
    return _latest().to_pyarrow_table(columns=["vax_id"]).num_rows

def update(vax_id: int, data: VaxUpdate):
    dt = _latest()
    updates = {
        k: str(v)
        for k, v in data.model_dump(exclude_none=True).items()
    }
    if not updates:
        return False
    dt.update(updates=updates, predicate=f"vax_id = {vax_id}")
    return True

# UPSERT (merge)
def upsert(data: VaxCreate, vax_id: int | None = None):
    dt = _latest()
    row = {
            "vax_id": vax_id or _id.get_next(),
            **data.model_dump()
        }
    
    table = db.pa.Table.from_pandas(
        db.pd.DataFrame([row]),
        preserve_index=False
    )

    (
        dt.merge(source=table, predicate="s.vax_id = t.vax_id",
                 source_alias="s", target_alias="t")
        .when_matched_update_all()
        .when_not_matched_insert_all()
        .execute()
    )
    return row

def delete(vax_id: int):
    dt = _latest()
    dt.delete(predicate=f"vax_id = {vax_id}")
    return True

# HISTORY / TIME TRAVEL
# def history() -> list[dict]:
#     return _latest().history()

# def get_version(version: int):
#     dt = db.DeltaTable(WRITE_PATH, version=version)
#     return dt.to_pandas().to_dict(orient="records")

def vacuum(dry_run: bool = True, retention_hours: int = 168):
    dt = _latest()
    db.GenID.reset(_id, 0)
    return dt.vacuum(
        dry_run=dry_run,
        retention_hours=retention_hours,
        enforce_retention_duration=(retention_hours > 0)
    )