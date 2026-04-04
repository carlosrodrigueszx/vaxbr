import app.db as db
from app.schemas.vax import VaxCreate, VaxUpdate
from app.core.logger import get_logger
import io
import zipstream
import math

logger = get_logger(__name__)

WRITE_PATH = "app/tmp/vax"
FILE_SEQ   = "app/data/.seq"

_id = db.GenID(FILE_SEQ, delta_table_path=WRITE_PATH, id_column="vax_id")


def _latest() -> db.DeltaTable:
    return db.DeltaTable(WRITE_PATH)


def _exists(vax_id: int) -> bool:
    dt = _latest().to_pandas()
    exists = vax_id in dt["vax_id"].values
    if exists:
        logger.info("Vacina encontrada: vax_id=%s", vax_id)
    else:
        logger.warning("Vacina não encontrada: vax_id=%s", vax_id)
    return exists


def insert(data: VaxCreate) -> dict:
    next_id = _id.get_next()
    logger.info("Inserindo vacina — vax_id=%s", next_id)
    df = db.pd.DataFrame([{"vax_id": next_id, **data.model_dump()}])
    db.write_deltalake(WRITE_PATH, df, mode="append")
    logger.info("Vacina inserida com sucesso — vax_id=%s", next_id)
    return df.iloc[0].to_dict()


def get_by_id(vax_id: int):
    logger.info("Buscando vacina — vax_id=%s", vax_id)
    table = _latest().to_pyarrow_table(filters=[("vax_id", "=", vax_id)])
    if table.num_rows == 0:
        logger.warning("Nenhum resultado para vax_id=%s", vax_id)
        return None
    logger.info("Vacina encontrada — vax_id=%s", vax_id)
    return table.to_pylist()


def list_all(
    page: int = 1,
    page_size: int = 10,
    illness: str | None = None,
    target: str | None = None,
):
    logger.info("Listando vacinas — page=%s page_size=%s illness=%s target=%s",
                page, page_size, illness, target)

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
        collected_batches.append(batch.slice(start_in_batch, take))
        remaining -= take
        skipped += batch.num_rows
        if remaining <= 0:
            break

    data = db.pa.Table.from_batches(collected_batches).to_pylist() if collected_batches else []
    total_records = dataset.count_rows(filter=expr)
    total_pages = max(1, math.ceil(total_records / page_size))

    logger.info("Listagem concluída — total_records=%s total_pages=%s", total_records, total_pages)

    return {
        "data": data,
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": total_pages,
    }


def count() -> int:
    total = _latest().to_pyarrow_table(columns=["vax_id"]).num_rows
    logger.info("Contagem total de vacinas: %s", total)
    return total


def update(vax_id: int, data: VaxUpdate):
    logger.info("Atualizando vacina — vax_id=%s", vax_id)
    if not _exists(vax_id):
        logger.warning("Atualização cancelada: vax_id=%s não encontrado", vax_id)
        return False

    updates = data.model_dump(exclude_none=True)
    if not updates:
        logger.warning("Atualização cancelada: nenhum campo enviado para vax_id=%s", vax_id)
        return False

    _latest().update(new_values=updates, predicate=f"vax_id = {vax_id}")
    logger.info("Vacina atualizada com sucesso — vax_id=%s campos=%s", vax_id, list(updates.keys()))
    return True


def upsert(data: VaxCreate, vax_id: int | None = None):
    resolved_id = vax_id or _id.get_next()
    logger.info("Upsert — vax_id=%s", resolved_id)

    row = {"vax_id": resolved_id, **data.model_dump()}
    table = db.pa.Table.from_pandas(db.pd.DataFrame([row]), preserve_index=False)

    (
        _latest()
        .merge(source=table, predicate="s.vax_id = t.vax_id",
               source_alias="s", target_alias="t")
        .when_matched_update_all()
        .when_not_matched_insert_all()
        .execute()
    )
    logger.info("Upsert concluído — vax_id=%s", resolved_id)
    return row


def delete(vax_id: int):
    logger.info("Deletando vacina — vax_id=%s", vax_id)
    _latest().delete(predicate=f"vax_id = {vax_id}")
    logger.info("Vacina deletada com sucesso — vax_id=%s", vax_id)
    return True


def vacuum(dry_run: bool = True, retention_hours: int = 168) -> list[str]:
    logger.info("Vacuum — dry_run=%s retention_hours=%s", dry_run, retention_hours)
    files = _latest().vacuum(
        dry_run=dry_run,
        retention_hours=retention_hours,
        enforce_retention_duration=(retention_hours > 0),
    )
    logger.info("Vacuum concluído — %s arquivos afetados", len(files))
    return files


def parquet_to_csv_stream(file_path):
    logger.info("Iniciando stream CSV — path=%s", file_path)
    parquet_file = db.pdt.dataset(file_path, format="parquet")
    first = True
    for batch in parquet_file.to_batches():
        table = batch.to_pandas()
        buffer = io.StringIO()
        table.to_csv(buffer, index=False, header=first)
        first = False
        yield buffer.getvalue()
    logger.info("Stream CSV concluído — path=%s", file_path)


def parquet_to_zip_stream(file_path):
    logger.info("Iniciando stream ZIP — path=%s", file_path)
    z = zipstream.ZipFile(mode="w", compression=zipstream.ZIP_DEFLATED)

    def _encoded_generator():
        parquet_file = db.pdt.dataset(file_path, format="parquet")
        first = True
        for batch in parquet_file.to_batches():
            table = batch.to_pandas()
            buffer = io.StringIO()
            table.to_csv(buffer, index=False, header=first)
            first = False
            yield buffer.getvalue().encode("UTF-8")
        logger.info("Stream ZIP concluído — path=%s", file_path)

    z.write_iter("dados.csv", _encoded_generator())
    return z
