from charsi.recipe import RecipeBuilder
from charsi.strings import LanguageTag


def test_recipe_read(recipe1_recipe):
    assert len(recipe1_recipe.instructions) == 2
    assert recipe1_recipe.instructions[0].name == 'Text'
    assert recipe1_recipe.instructions[0].query == 'presenceMenus'
    assert len(recipe1_recipe.instructions[0].args) == 1
    assert recipe1_recipe.instructions[0].args[0] == 'Replaced_presenceMenus'

    assert recipe1_recipe.instructions[1].name == 'Text'
    assert recipe1_recipe.instructions[1].query == 'presenceA1Normal~presenceA5Hell'
    assert len(recipe1_recipe.instructions[1].args) == 1
    assert recipe1_recipe.instructions[1].args[0] == 'Replaced'


def test_recipe_build(presence_states_tbl, recipe1_recipe):
    old_item = presence_states_tbl.find('presenceMenus').model_copy()
    builder = RecipeBuilder()
    builder.build(recipe1_recipe, presence_states_tbl)

    new_item = presence_states_tbl.find('presenceMenus')
    for lang in LanguageTag.tags():
        if lang == 'zhCN':
            assert getattr(new_item, lang) == 'Replaced_presenceMenus'
        else:
            assert getattr(new_item, lang) == getattr(old_item, lang)

    for item in presence_states_tbl.findall('presenceA1Normal~presenceA5Hell'):
        for lang in LanguageTag.tags():
            assert getattr(item, lang) == 'Replaced'


def test_recipe_tag(presence_states_tbl, recipe2_recipe):
    old_item1 = presence_states_tbl.find('presenceMenus').model_copy()
    old_item2 = presence_states_tbl.find('presenceA1Normal').model_copy()

    builder = RecipeBuilder()
    builder.build(recipe2_recipe, presence_states_tbl)

    new_item1 = presence_states_tbl.find('presenceMenus')
    new_item2 = presence_states_tbl.find('presenceA1Normal')

    for lang in LanguageTag.tags():
        if lang == 'zhCN':
            assert getattr(new_item1, lang) == 'Replaced_presenceMenus'
        else:
            assert getattr(new_item1, lang) == getattr(old_item1, lang)

        if lang == 'enUS':
            assert getattr(new_item2, lang) == 'Replaced_presenceA1Normal'
        else:
            assert getattr(new_item2, lang) == getattr(old_item2, lang)
