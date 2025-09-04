from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional

from lupa import LuaRuntime

from .utils import split_text, COLOR_CODES


@dataclass(frozen=True, slots=True)
class Instruction:
    name: str
    query: str
    args: list[str]
    lang: Optional[str] = None


class InstructionParser:
    _RE_INSTRUCTION = re.compile(r'^\s*(\w+)\s*(\[[^]]+])\s*(\[[^]]+])?', re.VERBOSE)

    @classmethod
    def parse(cls, text: str) -> Instruction:
        text = split_text(text, '#')[0]
        head, *_ = split_text(text, ':')

        m = cls._RE_INSTRUCTION.match(head)

        if not m:
            raise ValueError(f'Invalid instruction head: {head!r}')

        name, query, lang = m.groups()
        raw_args = text[len(head) + 1:].strip()
        args = [arg.strip() for arg in raw_args.split(',')] if raw_args else []

        return Instruction(
            name=name,
            query=query.strip(' []') if query else '',
            args=args,
            lang=lang.strip(' []') if lang else None,
        )


class InstructionInvoker:
    _lua: LuaRuntime
    _handlers: dict[str, Callable[[str, ...], str]]

    _default: Optional[InstructionInvoker] = None

    def __init__(self) -> None:
        self._handlers = {}
        self._lua: LuaRuntime = LuaRuntime(
            unpack_returned_tuples=True, register_builtins=False
        )

        g = self._lua.globals()
        g['python'] = None
        g['RegisterInstruction'] = self.register
        g['UnregisterInstruction'] = self.unregister
        g['InstructionRegistered'] = self.is_registered

    @classmethod
    def default(cls) -> InstructionInvoker:
        if cls._default is None:
            cls._default = cls()
            cls._default._register_builtin_handlers()

        return cls._default

    def register(self, name: str, handler: Callable[[str, ...], str]) -> None:
        if name in self._handlers:
            raise ValueError(f'Instruction {name!r} already registered.')

        self._handlers[name] = handler

    def unregister(self, name: str) -> None:
        try:
            del self._handlers[name]
        except KeyError as e:
            raise ValueError(f'Instruction {name!r} not found.') from e

    def is_registered(self, name: str) -> bool:
        return name in self._handlers

    def invoke(self, inst: Instruction, text: str) -> str:
        try:
            handler = self._handlers[inst.name]
        except KeyError as e:
            raise ValueError(f'Instruction {inst.name!r} not defined.') from e

        return handler(text, *inst.args)

    def load_lua(self, codes: str) -> None:
        self._lua.execute(codes)

    def _register_builtin_handlers(self) -> None:
        self.register('Text', _replace_text_handler)
        self.register('Color', _color_handler)


def _replace_text_handler(_: str, *args: str) -> str:
    return args[0].replace(r'\n', '\n')


def _color_handler(text: str, *args: str) -> str:
    code = COLOR_CODES.get(args[0].upper())

    if code is None:
        raise ValueError(f'Unknown color: {args[0]!r}')

    return f'{code}{text}'
