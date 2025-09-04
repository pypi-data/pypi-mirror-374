from __future__ import annotations

import re
from typing import TextIO

from .instruction import InstructionParser, Instruction, InstructionInvoker
from .strings import StringTable, LanguageTag
from .utils import filter_irrelevant_lines, split_text

_RE_VARIABLE = re.compile(r"{([\w-]+)}")


class Recipe:
    instructions: list[Instruction]
    tags: dict[str, str]

    def __init__(self, instructions: list[Instruction], tags: dict[str, str]):
        self.instructions = instructions
        self.tags = tags

    @classmethod
    def load(cls, fp: TextIO) -> Recipe:
        lines = [line.strip() for line in fp.readlines()]
        instructions = [InstructionParser.parse(line) for line in filter_irrelevant_lines(lines)]
        tags = {}

        for line in filter(lambda line: line != '' and line[0:2] == '##', lines):
            fds = split_text(line, ':')
            tags[fds[0][2:].strip()] = fds[1].strip()

        return Recipe(instructions=instructions, tags=tags)


class RecipeBuilder:
    _invoker: InstructionInvoker
    _variable_tables: dict

    def __init__(self, invoker: InstructionInvoker = InstructionInvoker.default(), variable_tables: dict = None):
        self._invoker = invoker
        self._variable_tables = variable_tables or {}

    def build(self, recipe: Recipe, tbl: StringTable):
        for inst in recipe.instructions:
            if inst.lang:
                langs = [inst.lang]
            elif 'Language' in recipe.tags:
                langs = [recipe.tags['Language']]
            else:
                langs = LanguageTag.tags()

            for item in tbl.findall(inst.query):
                for lang in langs:
                    text = self._invoker.invoke(inst, getattr(item, lang))

                    setattr(item, lang, self._apply_variables(item.Key, text))

    def set_variable_table(self, key: str, var_table: dict):
        self._variable_tables[key] = var_table

    def _apply_variables(self, key: str, text: str):
        m = re.findall(_RE_VARIABLE, text)

        if not m:
            return text

        for name in map(lambda v: v.strip('{}'), m):
            if name not in self._variable_tables or key not in self._variable_tables[name]:
                var = ''
            else:
                var = self._variable_tables[name][key]

            text = text.replace('{%s}' % name, var)

        return text.strip()
