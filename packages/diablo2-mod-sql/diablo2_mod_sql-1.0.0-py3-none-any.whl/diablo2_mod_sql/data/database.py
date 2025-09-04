from pathlib import Path
from .table import DataTable
from .d2string import D2StringTable
from .d2txt import D2TxtTable


class D2Database:
    base_dir: Path

    _table_types = {
        '.json': D2StringTable,
        '.txt': D2TxtTable
    }

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def get_table(self, path: str) -> DataTable:
        full_path = self.base_dir.joinpath(path)
        return D2Database._table_types[full_path.suffix.lower()](full_path)
