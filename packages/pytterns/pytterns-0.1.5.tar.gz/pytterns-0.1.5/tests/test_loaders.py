import pytest
from pytterns.core.loaders import StrategyLoader, ChainLoader
from pytterns.core.decorators import strategy, STRATEGIES, chain, CHAINS

@strategy("group_1")
class StrategyA:
    def check(self, value):
        return value == "A"
    def run(self):
        return "StrategyA"

@strategy("group_1")
class StrategyB:
    def check(self, value):
        return value == "B"
    def run(self):
        return "StrategyB"

def test_strategy_loader_found():
    loader = StrategyLoader("group_1")
    assert loader.check("A").__class__.__name__ == "StrategyA"
    assert loader.check("B").__class__.__name__ == "StrategyB"

def test_strategy_loader_not_found():
    loader = StrategyLoader("group_1")
    with pytest.raises(ValueError, match="No strategy in 'group_1' passed the 'check' filter"):
        loader.check("C")

@pytest.fixture(autouse=True)
def reset_chains():
    # Save and restore CHAINS to avoid interfering with other test modules
    orig = CHAINS.copy()
    CHAINS.clear()
    try:
        yield
    finally:
        CHAINS.clear()
        CHAINS.update(orig)

def test_chain_execution(capsys):
    @chain('test_chain', order=1)
    class FirstHandler:
        def handle(self, value):
            print(f"FirstHandler processed {value}")

    @chain('test_chain', order=2)
    class SecondHandler:
        def handle(self, value):
            print(f"SecondHandler processed {value}")

    obj = ChainLoader("test_chain")
    obj.handle(42)

    captured = capsys.readouterr()
    assert "FirstHandler processed 42" in captured.out
    assert "SecondHandler processed 42" in captured.out

def test_chain_not_found():
    with pytest.raises(ValueError, match="No chain found for: nonexistent_chain"):
        ChainLoader("nonexistent_chain")

def test_handler_without_handle():
    @chain('test_chain', order=1)
    class InvalidHandler:
        def process(self, value):
                print(f"Invalid processing {value}")
    with pytest.raises(TypeError, match="Class 'InvalidHandler' does not have the 'handle' method."):
        obj = ChainLoader("test_chain")
        obj.handle(42)

def test_chain_execution_order(capsys):
    @chain('test_chain', order=2)
    class SecondHandler:
        def handle(self, value):
            print("SecondHandler")

    @chain('test_chain', order=1)
    class FirstHandler:
        def handle(self, value):
            print("FirstHandler")

    obj = ChainLoader("test_chain")
    obj.handle(100)

    captured = capsys.readouterr()
    assert captured.out.strip().split("\n") == ["FirstHandler", "SecondHandler"]


def test_empty_strategy_group_raises():
    with pytest.raises(ValueError, match="No strategy found for strategy: nonexistent"):
        StrategyLoader("nonexistent")


def test_strategy_single_method_called_via_loader():
    @strategy("solo_group")
    class Solo:
        def execute(self):
            return "solo_result"

    loader = StrategyLoader("solo_group")
    assert loader.execute() == "solo_result"


def test_strategy_single_method_return_none():
    @strategy("solo_none")
    class SoloNone:
        def execute(self):
            return None

    loader = StrategyLoader("solo_none")
    assert loader.execute() is None


def test_chain_handle_with_args_and_kwargs(capsys):
    results = []

    @chain('args_chain', order=1)
    class HandlerArgs:
        def handle(self, a, b=0):
            print(f"handled {a} {b}")
            results.append((a, b))

    obj = ChainLoader('args_chain')
    obj.handle(7, b=9)

    captured = capsys.readouterr()
    assert "handled 7 9" in captured.out
    assert results == [(7, 9)]


def test_chain_same_order_preserves_registration_order(capsys):
    @chain('same_order', order=1)
    class First:
        def handle(self, value):
            print("First")

    @chain('same_order', order=1)
    class Second:
        def handle(self, value):
            print("Second")

    obj = ChainLoader('same_order')
    obj.handle(None)

    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == ["First", "Second"]
