from __future__ import annotations

import json
import re
from enum import Enum
from typing import TextIO

from pydantic import BaseModel


class LanguageTag(Enum):
    enUS = 'enUS'
    zhTW = 'zhTW'
    deDE = 'deDE'
    esES = 'esES'
    frFR = 'frFR'
    itIT = 'itIT'
    koKR = 'koKR'
    plPL = 'plPL'
    esMX = 'esMX'
    jaJP = 'jaJP'
    ptBR = 'ptBR'
    ruRU = 'ruRU'
    zhCN = 'zhCN'

    @classmethod
    def tags(cls) -> list[str]:
        return [tag.value for tag in cls]


class StringItem(BaseModel):
    id: int
    Key: str
    enUS: str
    zhTW: str
    deDE: str
    esES: str
    frFR: str
    itIT: str
    koKR: str
    plPL: str
    esMX: str
    jaJP: str
    ptBR: str
    ruRU: str
    zhCN: str


class StringTable:
    _items: list[StringItem]
    _item_indices: dict[str, int]
    _alias: dict[str, str]

    def __init__(self, items: list[StringItem]):
        self._items = items
        self._item_indices = {items[i].Key: i for i in range(0, len(items))}
        self._alias = {}

    @classmethod
    def load(cls, fp: TextIO) -> StringTable:
        items = json.load(fp)
        return cls([StringItem(**it) for it in items])

    def write(self, fp: TextIO):
        json.dump([it.model_dump() for it in self._items], fp, ensure_ascii=False, indent=2)

    def find(self, key: str) -> StringItem:
        if key not in self._item_indices:
            raise KeyError(key)

        return self._items[self._item_indices[key]]

    def findall(self, query: str) -> list[StringItem]:
        if ',' in query:
            return [it for part in re.split(r'\s*,\s*', query) for it in self.findall(part)]

        if '~' in query:
            return self._range_query(query)

        if query in self._alias:
            return self.findall(self._alias[query])

        return [self.find(query)]

    def set_alias(self, table: dict[str, str]):
        self._alias = table

    def _range_query(self, expr: str):
        start_str, end_str = map(str.strip, expr.split('~', 1))

        try:
            start_idx = self._item_indices[start_str]
            end_idx = self._item_indices[end_str]
        except KeyError as e:
            raise KeyError(expr) from e

        if start_idx > end_idx:
            raise KeyError(f'Range start > end: {expr}')

        return self._items[start_idx: end_idx + 1]

    def __getitem__(self, key: str | int) -> StringItem:
        if isinstance(key, int):
            return self._items[key]

        return self.find(key)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)
