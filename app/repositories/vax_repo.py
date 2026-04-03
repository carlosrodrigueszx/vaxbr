import app.db as db
from app.schemas.vax import VaxCreate, VaxUpdate
import io
import zipstream
import math

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

    offset = (page - 1) * page_size
    remaining = page_size

    collected_batches = []
    skipped = 0

    for batch in dataset.to_batches(filter=expr):
        if batch.num_rows == 0:
            continue

        if skipped + batch.num_rows <= offset:
            skipped += batch.num_rows
            continue

        start_in_batch = max(0, offset - skipped)

        take = min(batch.num_rows - start_in_batch, remaining)

        sliced = batch.slice(start_in_batch, take)
        collected_batches.append(sliced)

        remaining -= take
        skipped += batch.num_rows

        if remaining <= 0:
            break

    if collected_batches:
        page_table = db.pa.Table.from_batches(collected_batches)
        data = page_table.to_pylist()
    else:
        data = []

    total_records = dataset.count_rows(filter=expr)
    total_pages = max(1, math.ceil(total_records / page_size))

    return {
        "data": data,
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
