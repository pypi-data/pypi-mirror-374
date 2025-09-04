import csv
from pathlib import Path
from diablo2_mod_sql.data.table import DataTable, DataRow, DataColumnCollection, DataColumnType
from .column_spec import txt_columns_map


class D2TxtTable(DataTable):
    def __init__(self, path: Path):
        super().__init__(path)

        self.columns = txt_columns_map[self.name]
        self.rows = []

        with path.open('r', encoding='utf-8') as fp:
            reader = csv.reader(
                fp, dialect="excel-tab", quoting=csv.QUOTE_NONE, quotechar=None
            )

            next(iter(reader))
            for row in reader:
                self.rows.append(DataRow(row, self.columns))

        super().__post_init__()
