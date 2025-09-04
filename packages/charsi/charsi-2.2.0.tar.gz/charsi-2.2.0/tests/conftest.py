import shutil
import tempfile
from pathlib import Path

import pytest

from charsi.recipe import Recipe
from typer.testing import CliRunner
from charsi.strings import StringTable


def copy_asset(filename: str, path: Path):
    dest_path = path / filename
    shutil.copy(Path(__file__).parent / 'assets' / filename, dest_path)

    return dest_path


@pytest.fixture(scope='module')
def runner():
    return CliRunner()


@pytest.fixture(scope='function')
def temp_dir() -> Path:
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture(scope='function')
def presence_states_path():
    return Path(__file__).parent / 'assets' / 'presence-states.json'


@pytest.fixture(scope='function')
def presence_states_tbl(presence_states_path):
    with open(presence_states_path, 'r', encoding='utf-8-sig') as fp:
        yield StringTable.load(fp)


@pytest.fixture(scope='function')
def instructions_lua(temp_dir):
    return copy_asset('instructions.lua', temp_dir)


@pytest.fixture(scope='function')
def recipe1_path():
    return Path(__file__).parent / 'assets' / 'recipe1.recipe'


@pytest.fixture(scope='function')
def recipe1_recipe(recipe1_path):
    with recipe1_path.open('r', encoding='utf-8') as fp:
        yield Recipe.load(fp)


@pytest.fixture(scope='function')
def recipe2_path():
    return Path(__file__).parent / 'assets' / 'recipe2.recipe'


@pytest.fixture(scope='function')
def recipe2_recipe(recipe2_path):
    with recipe2_path.open('r', encoding='utf-8') as fp:
        yield Recipe.load(fp)
