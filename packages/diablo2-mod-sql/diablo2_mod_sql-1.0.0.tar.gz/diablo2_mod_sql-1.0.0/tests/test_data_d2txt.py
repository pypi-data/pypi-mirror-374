from diablo2_mod_sql.sql.statement import parse_statement

TB_NAME = 'global/excel/actinfo.txt'


def test_d2txttable(d2database):
    stmt = parse_statement(d2database, f'SELECT * FROM {TB_NAME}')
    rows = list(stmt.execute())

    assert len(rows) == 5
    assert rows[0][0] == 1
    assert rows[0][1] == 'Act 1 - Town'
    assert rows[4][0] == 5
    assert rows[4][1] == 'Act 5 - Town'
