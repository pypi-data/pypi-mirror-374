from __future__ import annotations
from typing import Union, Iterable
from abc import ABC, abstractmethod
import mo_sql_parsing
from diablo2_mod_sql.data import D2Database
from diablo2_mod_sql.data.table import DataTable, DataRow
from diablo2_mod_sql.sql.operand import operand_map, Operand

table_mask = {
    '/': '__SEP__',
    '-': '__HYPHEN__'
}


def mask_table_name(sql: str) -> str:
    for k, v in table_mask.items():
        sql = sql.replace(k, v)

    return sql


def unmask_table_name(name: str) -> str:
    for k, v in table_mask.items():
        name = name.replace(v, k)

    return name


def parse_statement(db: D2Database, sql: str) -> SQLStatement:
    sql_tree = mo_sql_parsing.parse(mask_table_name(sql))

    if 'select' in sql_tree:
        stmt = SelectStatement(db.get_table(unmask_table_name(sql_tree['from'])), sql_tree)
    elif 'update' in sql_tree:
        stmt = UpdateStatement(db.get_table(unmask_table_name(sql_tree['update'])), sql_tree)
    elif 'insert' in sql_tree:
        stmt = InsertStatement(db.get_table(unmask_table_name(sql_tree['insert'])), sql_tree)
    elif 'delete' in sql_tree:
        stmt = DeleteStatement(db.get_table(unmask_table_name(sql_tree['delete'])), sql_tree)
    else:
        raise SyntaxError(sql)  # pragma: no cover

    return stmt


class SQLStatement(ABC):
    table: DataTable
    where: Union[None, Operand]
    sql_tree: dict

    def __init__(self, table: DataTable, sql_tree: dict):
        self.table = table
        self.where = None
        self.sql_tree = sql_tree

        if 'where' in sql_tree:
            self.where = self.parse_op_tree(sql_tree['where'])

    def parse_op_tree(self, op_tree: dict) -> Operand:
        def parse_op(arg):
            if isinstance(arg, dict):
                if 'literal' in arg:
                    return {
                        'type': 'literal',
                        'value': arg['literal']
                    }

                return {
                    'type': 'operand',
                    'value': self.parse_op_tree(arg)
                }

            if isinstance(arg, str):
                return {
                    'type': 'column',
                    'value': self.table.columns.index(arg)
                }

            return {
                'type': 'literal',
                'value': arg
            }

        op_code = next(iter(op_tree))
        result = operand_map[op_code]()

        if not isinstance(op_tree[op_code], list):
            result.args.append(parse_op(op_tree[op_code]))

            return result

        for arg in op_tree[op_code]:
            result.args.append(parse_op(arg))

        return result

    @abstractmethod
    def execute(self):  # pragma: no cover
        ...


class SelectStatement(SQLStatement):
    def execute(self) -> Union[DataRow, Iterable[DataRow]]:
        if self.where is None:
            return self.table.rows

        return filter(lambda row: self.where.test(row) is True, self.table.rows)


class UpdateStatement(SQLStatement):
    set: dict

    def __init__(self, table: DataTable, sql_tree: dict):
        super().__init__(table, sql_tree)

        if 'set' in sql_tree:
            self.set = sql_tree['set']

    def execute(self) -> int:
        i = 0

        for row in self.table.rows:
            if self.where is not None and not self.where.test(row):
                continue

            for key in self.set:
                value = self.set[key]

                if isinstance(value, dict) and 'literal' in value:
                    row[key] = value['literal']
                elif isinstance(value, str):
                    row[key] = row[value]
                else:
                    row[key] = value

            i += 1

        return i


class InsertStatement(SQLStatement):
    def execute(self) -> None:
        row = [''] * len(self.table.columns)

        for i in range(len(self.sql_tree['query']['select'])):
            if 'columns' in self.sql_tree:
                column_index = self.table.columns.index(self.sql_tree['columns'][i])
            else:
                column_index = i

            value = self.sql_tree['query']['select'][i]['value']

            if isinstance(value, dict) and 'literal' in value:
                row[column_index] = value['literal']
            else:
                row[column_index] = value

        self.table.rows.append(DataRow(row, self.table.columns))


class DeleteStatement(SQLStatement):
    def execute(self) -> int:
        i = len(self.table.rows)

        if self.where is None:
            self.table.rows = []

            return i

        self.table.rows = [row for row in self.table.rows if not self.where.test(row)]

        return i - len(self.table.rows)
