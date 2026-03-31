import pandas
import time
import pyarrow.parquet
import pyarrow.csv
import pyarrow.dataset as pdt
from pyarrow import csv
from deltalake import DeltaTable, write_deltalake, WriterProperties
import pyarrow.compute as pc

class GenID:
    def __init__(self, seq_file: str, delta_table_path: str = None, id_column: str = "vax_id"):
        self.seq = seq_file
        self.delta_table_path = delta_table_path
        self.id_column = id_column
        self._current_id = self._resolve_last_id()

    def _resolve_last_id(self) -> int:
        """
        Fonte da verdade: MAX(id_column) da Delta Table.
        Fallback: arquivo .seq.
        Fallback final: 0 (tabela nova).
        """
        delta_max = self._get_max_from_delta()
        seq_val = self._read_seq_file()

        last_id = max(delta_max, seq_val)

        # Mantém o .seq sincronizado
        self._write_seq_file(last_id)

        print(f"[GenID] Iniciando a partir do ID: {last_id}")
        return last_id

    def _get_max_from_delta(self) -> int:
        if not self.delta_table_path:
            return 0
        try:
            dt = DeltaTable(self.delta_table_path)

            table = dt.to_pyarrow_table(columns=[self.id_column])

            if table.num_rows == 0:
                return 0
            max_id = pc.max(table.column(self.id_column)).as_py()
            
            return int(max_id) if max_id is not None else 0
        except Exception:
            # Tabela ainda não existe
            return 0

    def _read_seq_file(self) -> int:
        try:
            with open(self.seq, "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _write_seq_file(self, value: int):
        with open(self.seq, "w") as f:
            f.write(str(value))

    def get_next(self) -> int:
        self._current_id += 1
        self._write_seq_file(self._current_id)
        print(f"[GenID] Gerando ID: {self._current_id}")
        return self._current_id