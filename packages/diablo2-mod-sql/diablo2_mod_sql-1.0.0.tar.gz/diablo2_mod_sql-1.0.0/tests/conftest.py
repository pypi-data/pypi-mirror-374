from pathlib import Path

import pytest

from diablo2_mod_sql.data import D2Database
from diablo2_mod_sql.data.d2string import D2StringTable
from diablo2_mod_sql.data.d2txt import D2TxtTable


@pytest.fixture(scope='module')
def data_dir() -> Path:
    return Path(__file__).parent / 'assets' / 'data'


@pytest.fixture(scope='module')
def d2database(data_dir) -> D2Database:
    return D2Database(data_dir)


@pytest.fixture(scope='function')
def presence_states_table(data_dir):
    tb = D2StringTable(data_dir / 'local/lng/strings/presence-states.json')

    assert len(tb.rows) == 16
    assert tb.rows[0][0] == tb.rows[0]['id'] == 26047
    assert tb.rows[15][1] == tb.rows[15]['Key'] == 'presenceA5Hell'

    return tb


@pytest.fixture(scope='function')
def actinfo_table(data_dir):
    tb = D2TxtTable(Path(data_dir / 'data/global/excel/actinfo.txt'))

    assert len(tb.rows) == 5
    return tb
