import csv
import sys
import os
import pandas as pd
from deltalake import write_deltalake

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

WRITE_PATH = "app/tmp/vax"
FILE_SEQ   = "app/data/.seq"

def carregar_csv(caminho: str):
    print(f"Carregando dados de {caminho}...")

    rows = []
    max_id = 0

    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "vax_id":    int(row["vax_id"]),
                "name":      row["name"],
                "target":    row["target"],
                "illness":   row["illness"],
                "quantity":  int(row["quantity"]),
                "id_manufac": int(row["id_manufac"]),
            })
            max_id = max(max_id, int(row["vax_id"]))

    df = pd.DataFrame(rows)
    write_deltalake(WRITE_PATH, df, mode="overwrite")

    # Atualiza o .seq com o maior ID do CSV
    with open(FILE_SEQ, "w") as f:
        f.write(str(max_id))

    print(f"Concluído! {len(rows)} vacinas carregadas. Próximo ID: {max_id + 1}")

if __name__ == "__main__":
    carregar_csv("vax.csv")