import pytest

from charsi.strings import LanguageTag, StringTable


def test_language_tag():
    assert LanguageTag.tags() == ['enUS', 'zhTW', 'deDE', 'esES', 'frFR', 'itIT', 'koKR', 'plPL', 'esMX', 'jaJP',
                                  'ptBR', 'ruRU', 'zhCN']


def test_read_and_write_string_table(presence_states_tbl, temp_dir):
    assert len(presence_states_tbl) == 16
    assert presence_states_tbl[0].id == 26047
    assert presence_states_tbl[0].Key == 'presenceMenus'
    assert presence_states_tbl['presenceMenus'].id == 26047
    assert presence_states_tbl['presenceMenus'].Key == 'presenceMenus'

    presence_states_tbl[0].id = 12345
    presence_states_tbl[0].Key = 'TestKey'

    new_file = temp_dir / 'presence-states.json'

    with new_file.open('w', encoding='utf-8-sig') as fp:
        presence_states_tbl.write(fp)

    with new_file.open('r', encoding='utf-8-sig') as fp:
        new_tbl = StringTable.load(fp)

    assert len(new_tbl) == 16
    assert new_tbl[0].id == 12345
    assert new_tbl[0].Key == 'TestKey'


def test_find_string_item(presence_states_tbl):
    item = presence_states_tbl.find('presenceMenus')
    assert item.id == 26047 and item.Key == 'presenceMenus'

    with pytest.raises(KeyError) as exc:
        presence_states_tbl.find('nonExists')

    assert 'nonExists' in str(exc.value)


def test_findall_string_items(presence_states_tbl):
    sl = presence_states_tbl.findall('presenceMenus, presenceA1Normal~presenceA5Hell')

    assert len(sl) == 16
    assert sl[0].Key == 'presenceMenus'
    assert sl[1].Key == 'presenceA1Normal'
    assert sl[6].Key == 'presenceA1Nightmare'
    assert sl[11].Key == 'presenceA1Hell'
    assert sl[15].Key == 'presenceA5Hell'

    with pytest.raises(KeyError) as exc:
        presence_states_tbl.findall('notExists1~notExists2')

    assert 'notExists1~notExists2' in str(exc.value)

    sl = presence_states_tbl.findall('presenceMenus')
    assert len(sl) == 1
    assert sl[0].Key == 'presenceMenus'

    with pytest.raises(LookupError) as exc:
        presence_states_tbl.findall('nonExists')

    assert 'nonExists' in str(exc.value)

    with pytest.raises(KeyError) as exc:
        presence_states_tbl.findall('presenceA5Hell~presenceA1Normal')

    assert 'presenceA5Hell~presenceA1Normal' in str(exc.value)


def test_findall_by_alias(presence_states_tbl):
    presence_states_tbl.set_alias({
        'presenceNormal': 'presenceA1Normal~presenceA5Normal'
    })

    sl = presence_states_tbl.findall('presenceNormal')
    assert len(sl) == 5
    assert sl[0].Key == 'presenceA1Normal'
    assert sl[4].Key == 'presenceA5Normal'
