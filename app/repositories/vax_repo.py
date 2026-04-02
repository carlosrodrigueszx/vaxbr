import app.db as db
from app.schemas.vax import VaxCreate, VaxUpdate
import io
import zipstream
import hashlib

WRITE_PATH = "app/tmp/vax"
FILE_SEQ   = "app/data/.seq"

_id = db.GenID(FILE_SEQ, delta_table_path=WRITE_PATH, id_column="vax_id")

def _latest() -> db.DeltaTable:
    return db.DeltaTable(WRITE_PATH)

def _exists(vax_id: int) -> bool:
    dt = _latest()

    dt = dt.to_pandas()

    if vax_id not in dt['vax_id'].values:
        print("\nexiste não kkk...")
        return False

    print("\nexiste sim pae confia kk...")
    return True

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
    total_pages   = max(1, (total_records // page_size))

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
    print("\nverificando...")
    if(_exists(vax_id=vax_id)):
        dt = _latest()
        updates = data.model_dump(exclude_none=True)

        if not updates:
            return False
    
        dt.update(new_values=updates, predicate=f"vax_id = {vax_id}")

        return True
    return False

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

def vacuum(dry_run: bool = True, retention_hours: int = 168) -> list[str]:
    dt = _latest()
    return dt.vacuum(
        dry_run=dry_run,
        retention_hours=retention_hours,
        enforce_retention_duration=(retention_hours > 0)
    )

def parquet_to_csv_stream(file_path):
    parquet_file = db.pdt.dataset(file_path, format="parquet")

    # Header só uma vez
    first = True

    for batch in parquet_file.to_batches():
        table = batch.to_pandas()  # ou use pyarrow.csv se quiser evitar pandas

        buffer = io.StringIO()
        table.to_csv(buffer, index=False, header=first)

        first = False
        yield buffer.getvalue()

import zipstream

def parquet_to_zip_stream(file_path):
    z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

    def _encoded_generator():
        parquet_file = db.pdt.dataset(file_path, format="parquet")
        first = True

        for batch in parquet_file.to_batches():
            table = batch.to_pandas()
            buffer = io.StringIO()
            table.to_csv(buffer, index=False, header=first)
            first = False
            yield buffer.getvalue().encode("UTF-8")

    z.write_iter("dados.csv", _encoded_generator())

    return z

import hashlib

def stream_with_hash(generator):
    hasher = hashlib.sha256()

    for chunk in generator:
        if isinstance(chunk, str):
            chunk = chunk.encode("utf-8")

        hasher.update(chunk)
        yield chunk

    # ⚠️ hash só fica pronto no final
    print("HASH:", hasher.hexdigest())