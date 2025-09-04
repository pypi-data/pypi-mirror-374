from glob import glob
import typer
from pathlib import Path

from charsi.recipe import Recipe, RecipeBuilder
from charsi.strings import StringTable


def imbue_command(target_dir: Path = typer.Option(..., help="Directory to imbue with recipes")):
    """
    Build recipes by conventions under current directory.
    """

    builder = RecipeBuilder()

    for recipe_file in glob(str(Path.cwd().joinpath('**/*.recipe')), recursive=True):
        tbl_file = target_dir / 'local/lng/strings' / f'{Path(recipe_file).stem}.json'

        tbl = StringTable.load(tbl_file.open('r', encoding='utf-8-sig'))
        recipe = Recipe.load(Path(recipe_file).open('r', encoding='utf-8-sig'))

        builder.build(recipe, tbl)

        with tbl_file.open('w', encoding='utf-8-sig') as fp:
            tbl.write(fp)
