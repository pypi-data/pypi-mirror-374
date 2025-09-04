import os
import shutil
import tempfile
from pathlib import Path

from charsi.__main__ import app
from charsi.strings import LanguageTag, StringTable


def test_cmd_imbue(runner, presence_states_path, recipe1_path):
    temp_dir = Path(tempfile.mkdtemp())

    strings_dir = temp_dir.joinpath('local', 'lng', 'strings')
    strings_dir.mkdir(parents=True)

    shutil.copy(presence_states_path, strings_dir)

    recipes_dir = temp_dir.joinpath('recipes')
    recipes_dir.mkdir(parents=True)

    shutil.copy(recipe1_path, recipes_dir.joinpath('presence-states.recipe'))

    with strings_dir.joinpath('presence-states.json').open('r', encoding='utf-8-sig') as fp:
        tbl = StringTable.load(fp)

    old_item = tbl.find('presenceMenus').model_copy()

    os.chdir(temp_dir)

    result = runner.invoke(app, ['imbue', '--target-dir', str(temp_dir)])

    if result.exception:
        raise result.exception

    with strings_dir.joinpath('presence-states.json').open('r', encoding='utf-8-sig') as fp:
        tbl = StringTable.load(fp)

    new_item = tbl.find('presenceMenus')

    for lang in LanguageTag.tags():
        if lang == 'zhCN':
            assert getattr(new_item, lang) == 'Replaced_presenceMenus'
        else:
            assert getattr(new_item, lang) == getattr(old_item, lang)

    for item in tbl.findall('presenceA1Normal~presenceA5Hell'):
        for lang in LanguageTag.tags():
            assert getattr(item, lang) == 'Replaced'
