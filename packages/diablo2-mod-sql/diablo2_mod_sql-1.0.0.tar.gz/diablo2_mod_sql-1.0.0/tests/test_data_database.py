from diablo2_mod_sql.data.d2string import D2StringTable


def test_d2database(d2database):
    tb = d2database.get_table('local/lng/strings/presence-states.json')

    assert isinstance(tb, D2StringTable)
