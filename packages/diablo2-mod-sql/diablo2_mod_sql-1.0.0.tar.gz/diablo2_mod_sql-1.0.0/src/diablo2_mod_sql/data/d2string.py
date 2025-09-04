import json
from pathlib import Path
from .table import DataTable, DataRow, DataColumnCollection, DataColumnType

columns_collection = DataColumnCollection([
    {'name': 'id', 'type': DataColumnType.INTEGER},
    {'name': 'Key', 'type': DataColumnType.STRING},
    {'name': 'enUS', 'type': DataColumnType.STRING},
    {'name': 'zhTW', 'type': DataColumnType.STRING},
    {'name': 'deDE', 'type': DataColumnType.STRING},
    {'name': 'esES', 'type': DataColumnType.STRING},
    {'name': 'frFR', 'type': DataColumnType.STRING},
    {'name': 'itIT', 'type': DataColumnType.STRING},
    {'name': 'koKR', 'type': DataColumnType.STRING},
    {'name': 'plPL', 'type': DataColumnType.STRING},
    {'name': 'esMX', 'type': DataColumnType.STRING},
    {'name': 'jaJP', 'type': DataColumnType.STRING},
    {'name': 'ptBR', 'type': DataColumnType.STRING},
    {'name': 'ruRU', 'type': DataColumnType.STRING},
    {'name': 'zhCN', 'type': DataColumnType.STRING},
])


class D2StringTable(DataTable):
    def __init__(self, path: Path):
        super().__init__(path)

        self.columns = columns_collection
        self.rows = []

        with path.open('r', encoding='utf-8-sig') as fp:
            for data in json.load(fp):
                row = []
                for col in self.columns:
                    row.append(data[col.name])

                self.rows.append(DataRow(row=row, columns=self.columns))

        super().__post_init__()
