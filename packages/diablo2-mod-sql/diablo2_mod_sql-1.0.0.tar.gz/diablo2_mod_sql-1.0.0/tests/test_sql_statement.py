from diablo2_mod_sql.sql.statement import SelectStatement, UpdateStatement, DeleteStatement, InsertStatement, parse_statement

TB_NAME = 'local/lng/strings/presence-states.json'


def test_select_statement(presence_states_table):
    stmt = SelectStatement(presence_states_table, {
        'select': '*',
        'from': 'presence-states.json',
        'where': {
            'or': [
                {
                    'eq': ['id', 26047]
                },
                {
                    'eq': ['id', {'echo': 26048}]
                }
            ]
        }
    })

    rows = list(stmt.execute())
    assert len(rows) == 2
    assert rows[0]['id'] == 26047
    assert rows[0]['Key'] == 'presenceMenus'
    assert rows[1]['id'] == 26048
    assert rows[1]['Key'] == 'presenceA1Normal'

    stmt = SelectStatement(presence_states_table, {
        'select': '*',
        'from': 'presence-states.json',
        'where': {
            'and': [
                {
                    'eq': ['id', 26047]
                },
                {
                    'eq': ['Key', {'literal': 'presenceMenus'}]
                },
                {
                    'literal': True
                }
            ]
        }
    })

    rows = list(stmt.execute())
    assert len(rows) == 1
    assert rows[0]['id'] == 26047
    assert rows[0]['Key'] == 'presenceMenus'


def test_update_statement(presence_states_table):
    stmt = UpdateStatement(presence_states_table, {
        'update': 'presence-states.json',
        'set': {'Key': {'literal': 'for_testing'}, 'enUS': 'zhCN'},
        'where': {
            'or': [
                {
                    'eq': ['id', 26047]
                },
                {
                    'eq': ['id', 26048]
                },
                {
                    'literal': False
                }
            ]
        }
    })

    c = stmt.execute()
    assert c == 2

    rows = presence_states_table.rows
    assert rows[0]['Key'] == 'for_testing'
    assert rows[1]['Key'] == 'for_testing'
    assert rows[0]['enUS'] == rows[0]['zhCN']
    assert rows[1]['enUS'] == rows[1]['zhCN']


def test_insert_statement(presence_states_table):
    stmt = InsertStatement(presence_states_table, {
        'insert': 'presence-states.json',
        'columns': ['id', 'Key'],
        'query': {
            'select': [
                {'value': 88888},
                {'value': {'literal': 'new_item'}}
            ]
        }
    })

    stmt.execute()

    rows = presence_states_table.rows

    assert len(rows) == 17
    assert rows[16]['id'] == 88888
    assert rows[16]['Key'] == 'new_item'


def test_delete_statement(presence_states_table):
    stmt = DeleteStatement(presence_states_table, {
        'delete': 'presence-states.json',
        'where': {
            'or': [
                {
                    'eq': ['id', 26047]
                },
                {
                    'eq': ['id', 26048]
                }
            ]
        }
    })

    c = stmt.execute()
    rows = presence_states_table.rows
    assert c == 2
    assert len(rows) == 14


def test_select_sql(d2database):
    stmt = parse_statement(d2database, f'SELECT * FROM {TB_NAME}')
    rows = list(stmt.execute())

    assert len(rows) == 16
    assert rows[0][0] == 26047
    assert rows[0][1] == 'presenceMenus'
    assert rows[15][0] == 26062
    assert rows[15][1] == 'presenceA5Hell'

    stmt = parse_statement(d2database, f'SELECT * FROM {TB_NAME} WHERE id in (26058, 26059)')
    rows = list(stmt.execute())

    assert len(rows) == 2
    assert rows[0][0] == 26058
    assert rows[1][0] == 26059


def test_update_sql(d2database):
    stmt = parse_statement(d2database, f"UPDATE {TB_NAME} SET id = 12345 WHERE id = 26047")
    c = stmt.execute()

    assert c == 1
    rows = stmt.table.rows
    assert rows[0][0] == 12345


def test_insert_sql(d2database):
    stmt = parse_statement(d2database, f"INSERT INTO {TB_NAME} (id, Key) VALUES(12345, 'test_key1')")
    stmt.execute()

    rows = stmt.table.rows
    assert len(rows) == 17
    assert rows[16][0] == 12345
    assert rows[16][1] == 'test_key1'

    stmt = parse_statement(d2database, f"INSERT INTO {TB_NAME} VALUES(54321, 'test_key2')")
    stmt.execute()

    rows = stmt.table.rows
    assert len(rows) == 17
    assert rows[16][0] == 54321
    assert rows[16][1] == 'test_key2'


def test_delete_sql(d2database):
    stmt = parse_statement(d2database, f"DELETE FROM {TB_NAME} WHERE Key = 'presenceMenus'")
    c = stmt.execute()

    rows = stmt.table.rows
    assert c == 1
    assert len(rows) == 15
    assert rows[0][0] == 26048

    stmt = parse_statement(d2database, f"DELETE FROM {TB_NAME}")
    c = stmt.execute()
    rows = stmt.table.rows
    assert c == 16
    assert len(rows) == 0
