from pathlib import Path

import pytest

from charsi.instruction import InstructionInvoker, InstructionParser


def test_instruction_parse():
    inst = InstructionParser.parse('TestInstruction[query][lang1]: arg1, arg2, arg3 # comment')
    assert inst.name == 'TestInstruction'
    assert inst.query == 'query'
    assert inst.lang == 'lang1'
    assert len(inst.args) == 3
    assert inst.args[0] == 'arg1' and inst.args[1] == 'arg2' and inst.args[2] == 'arg3'

    with pytest.raises(ValueError) as exc:
        InstructionParser.parse('Invalid Instruction')

    assert 'Invalid instruction head:' in str(exc.value)

    with pytest.raises(ValueError) as exc:
        InstructionParser.parse('Invalid Instruction:')

    assert 'Invalid instruction head:' in str(exc.value)


def test_instruction_invoker():
    def handler(text: str, *args):
        return f'{text}:{"_".join(args)}'

    invoker = InstructionInvoker()
    inst = InstructionParser.parse('TestInstruction[query]: arg1, arg2')

    invoker.register('TestInstruction', handler)
    assert invoker.is_registered('TestInstruction')

    with pytest.raises(ValueError) as exc:
        invoker.register('TestInstruction', handler)
    assert 'already registered' in str(exc.value)

    invoker.unregister('TestInstruction')
    assert not invoker.is_registered('TestInstruction')

    with pytest.raises(ValueError) as exc:
        invoker.invoke(inst, '')
    assert 'not defined' in str(exc.value)

    with pytest.raises(ValueError) as exc:
        invoker.unregister('TestInstruction')
    assert 'not found' in str(exc.value)

    invoker.register('TestInstruction', handler)
    assert invoker.invoke(inst, 'TestString') == 'TestString:arg1_arg2'


def test_default_instruction_invoker():
    invoker = InstructionInvoker.default()

    inst = InstructionParser.parse('Text[query]: text-replaced')
    result = invoker.invoke(inst, 'origin-text')
    assert result == 'text-replaced'

    inst = InstructionParser.parse('Color[query]: White')
    result = invoker.invoke(inst, 'origin-text')
    assert result == 'ÿc0origin-text'


def test_instruction_invoker_lua(instructions_lua):
    invoker = InstructionInvoker()
    invoker.load_lua(instructions_lua.read_text(encoding='utf-8'))

    inst = InstructionParser.parse('LuaInstruction[test]: target-text')
    assert invoker.invoke(inst, 'origin-text') == 'LuaInstruction:origin-text:target-text'
