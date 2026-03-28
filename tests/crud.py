import app.db as db
import app.tools as tools

# set paths
write_path = "app/tmp/vax"
file_seq   = "/home/daniel/Projects/vaxbr/app/data/.seq_vax"

id = db.GenID(file_seq, delta_table_path=write_path, id_column="vax_id")

def print_version(dt: db.DeltaTable, label: str = ""):
    v = dt.version()
    history = dt.history(limit=1)[0]
    op      = history.get("operation", "N/A")
    ts      = history.get("timestamp", "N/A")
    tag     = f"[{label}] " if label else ""
    print(f"{tag}Versão atual: {v} | Operação: {op} | Timestamp: {ts}")

def print_count(dt: db.DeltaTable):
    df = dt.to_pandas()
    print(f"Total de registros : {len(df)}")
    print(f"Colunas            : {list(df.columns)}")
    print(f"Contagem por coluna:\n{df.count()}\n")

# lê a última versão
def read_latest(path: str):
    return db.DeltaTable(path)

def read_version(path: str, version: int):
    return db.DeltaTable(path, version=version)

def print_full_history(path: str):
    dt = read_latest(path)
    print("\n── Histórico completo de versões ──────────────────────────────")
    for entry in reversed(dt.history()):
        v   = entry.get("version", "?")
        op  = entry.get("operation", "N/A")
        ts  = entry.get("timestamp", "N/A")
        print(f"  v{v} | {op} | {ts}")
    print("───────────────────────────────────────────────────────────────\n")


print("\n── WRITE ───────────────────────────────────────────────────────")
df = db.pd.DataFrame(
    {
        "vax_id":     [id.get_next(), id.get_next(), id.get_next(), id.get_next()],
        "name":       ["CoronaVac", "Pfizer-BioNTech", "Janssen", "AstraZeneca"],
        "target":     ["SARS-CoV-2"] * 4,
        "illness":    ["COVID-19"] * 4,
        "quantity":   [10000, 25000, 8000, 15000],
        "id_manufac": [1, 2, 3, 4],
    }
)
df.columns = df.columns.str.lower()
db.write_deltalake(write_path, df)

dt = read_latest(write_path)
print_version(dt, "após write")
print(dt.to_pandas().head(100))
print_count(dt)

# ── UPDATE — todos os registros (v1) ──────────────────────────────────────────
print("\n── UPDATE (quantity > 0 → 5000) ────────────────────────────────")
dt = read_latest(write_path)
dt.update(updates={"quantity": "5000"}, predicate="quantity > 0")

dt = read_latest(write_path)
print_version(dt, "após update geral")
print(dt.to_pandas().head(100))

# ── UPDATE — registro específico (v2) ─────────────────────────────────────────
print("\n── UPDATE (vax_id = 1 → quantity = 99999) ──────────────────────")
dt = read_latest(write_path)
dt.update(updates={"quantity": "99999"}, predicate="vax_id = 1")

dt = read_latest(write_path)
print_version(dt, "após update específico")
print(dt.to_pandas().head(100))

# ── INSERT / APPEND (v3) ──────────────────────────────────────────────────────
print("\n── INSERT (append) ─────────────────────────────────────────────")
df_new = db.pd.DataFrame(
    {
        "vax_id":     [id.get_next(), id.get_next()],
        "name":       ["Moderna", "Sputnik V"],
        "target":     ["SARS-CoV-2"] * 2,
        "illness":    ["COVID-19"] * 2,
        "quantity":   [20000, 12000],
        "id_manufac": [5, 6],
    }
)
df_new.columns = df_new.columns.str.lower()
db.write_deltalake(write_path, df_new, mode="append")

dt = read_latest(write_path)
print_version(dt, "após append")
print(dt.to_pandas().head(100))
print_count(dt)

# ── MERGE / UPSERT (v4) ───────────────────────────────────────────────────────
print("\n── MERGE (upsert) ──────────────────────────────────────────────")
dt = read_latest(write_path)

df_merge = db.pd.DataFrame(
    {
        "vax_id":     [id.get_next(), id.get_next(), 1, 2],
        "name":       ["Covaxin", "Nuvaxovid", "CoronaVac", "Pfizer-BioNTech"],
        "target":     ["SARS-CoV-2"] * 4,
        "illness":    ["COVID-19"] * 4,
        "quantity":   [7000, 9000, 50000, 60000],
        "id_manufac": [7, 8, 1, 2],
    }
)
table = db.pyarrow.Table.from_pandas(df_merge, preserve_index=False)

(
    dt.merge(
        source=table,
        predicate="s.vax_id = t.vax_id",
        source_alias="s",
        target_alias="t",
    )
    .when_matched_update_all()
    .when_not_matched_insert_all()
    .execute()
)

dt = read_latest(write_path)
print_version(dt, "após merge")
print(dt.to_pandas().head(100))
print_count(dt)

# ── TIME TRAVEL ───────────────────────────────────────────────────────────────
print("\n── TIME TRAVEL ─────────────────────────────────────────────────")
latest_version = read_latest(write_path).version()

for v in range(latest_version + 1):
    dt_v = read_version(write_path, version=v)
    history_entry = dt_v.history(limit=latest_version + 1)
    # pega a entrada correspondente à versão v
    entry = next((e for e in history_entry if e.get("version") == v), {})
    op = entry.get("operation", "N/A")
    print(f"  v{v} ({op}): {len(dt_v.to_pandas())} registros")

# ── HISTÓRICO COMPLETO ────────────────────────────────────────────────────────
print_full_history(write_path)

# ── VACUUM ────────────────────────────────────────────────────────────────────
print("\n── VACUUM ──────────────────────────────────────────────────────")
dt = read_latest(write_path)

# dry_run: lista arquivos que seriam deletados sem apagar nada
files_to_delete = dt.vacuum(dry_run=True)
print(f"Arquivos que seriam deletados (dry_run): {len(files_to_delete)}")
for f in files_to_delete:
    print(f"  {f}")

# ATENÇÃO: vacuum apaga versões antigas — time travel anterior fica indisponível
# O retention padrão é 7 dias; forçar retention_hours=0 apaga tudo imediatamente
deleted_files = dt.vacuum(
    dry_run=False,
    retention_hours=0,
    enforce_retention_duration=False
)
print(f"\nArquivos deletados: {len(deleted_files)}")

dt = read_latest(write_path)
print_version(dt, "após vacuum")
print_count(dt)
print(dt.to_pandas().head(100))