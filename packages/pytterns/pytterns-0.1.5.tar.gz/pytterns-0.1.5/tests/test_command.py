import pytest
from pytterns import command, load
from pytterns.core.decorators import COMMANDS


@pytest.fixture(autouse=True)
def reset_commands():
    orig = COMMANDS.copy()
    COMMANDS.clear()
    try:
        yield
    finally:
        COMMANDS.clear()
        COMMANDS.update(orig)


def test_command_function_and_class_handlers():
    called = []

    @command('run')
    def fn(x):
        called.append(('fn', x))
        return 'f'

    @command('run')
    class C:
        def execute(self, x):
            called.append(('C', x))
            return 'c'

    results = load.command('run').execute(5)
    assert any(s and r == 'f' for s, r in results)
    assert any(s and r == 'c' for s, r in results)
    assert ('fn', 5) in called and ('C', 5) in called


def test_command_missing_raises():
    with pytest.raises(ValueError):
        load.command('nope').execute()


def test_command_unregister():
    @command('xx')
    def a():
        return 1

    @command('xx')
    class B:
        def execute(self):
            return 2

    loader = load.command('xx')
    # remove function handler
    loader.unregister(a)
    res = loader.execute()
    assert any(s and r == 2 for s, r in res)
    # remove class handler by class
    loader.unregister(B)
    # now command should be empty and calling execute still returns [] (no handlers)
    assert load.command('xx').execute() == []
