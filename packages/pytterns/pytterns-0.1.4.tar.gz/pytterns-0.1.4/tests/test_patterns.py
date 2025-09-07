import pytest
from pytterns.patterns import load
from pytterns.core.decorators import strategy, chain

# Define a strategy for testing
@strategy("group_2")
class StrategyX:
    def check(self, value):
        return value == "X"

    def run(self):
        return "StrategyX"

# Ensure `load.strategy()` correctly finds and executes a strategy
def test_load_strategy():
    strategy_instance = load.strategy("group_2").check("X")
    assert strategy_instance.__class__.__name__ == "StrategyX"

# Ensure an error is raised when no strategy matches the filter criteria
def test_load_strategy_not_found():
    with pytest.raises(ValueError, match="No strategy in 'group_2' passed the 'check' filter"):
        load.strategy("group_2").check("Y").run()

# Define handlers for the test chain
@chain('test_chain', order=1)
class FirstHandler:
    def handle(self, value):
        print(f"FirstHandler processed {value}")

@chain('test_chain', order=2)
class SecondHandler:
    def handle(self, value):
        print(f"SecondHandler processed {value}")

# Ensure `load.chain()` correctly executes all handlers in the chain
def test_load_chain_execution(capsys):
    chain_instance = load.chain("test_chain")
    chain_instance.handle(42)

    captured = capsys.readouterr()
    assert "FirstHandler" in captured.out
    assert "SecondHandler" in captured.out

# Ensure an error is raised when trying to load a non-existent chain
def test_load_chain_not_found():
    with pytest.raises(ValueError, match="No chain found for: nonexistent_chain"):
        load.chain("nonexistent_chain")

# Ensure handlers are executed in the correct order
def test_load_chain_execution_order(capsys):
    # Define another ordered chain to check execution order
    @chain('ordered_chain', order=2)
    class SecondHandlerOrdered:
        def handle(self, value):
            print("SecondHandler")

    @chain('ordered_chain', order=1)
    class FirstHandlerOrdered:
        def handle(self, value):
            print("FirstHandler")
    
    chain_instance = load.chain("ordered_chain")
    chain_instance.handle(100)

    captured = capsys.readouterr()
    assert captured.out.strip().split("\n") == ["FirstHandler", "SecondHandler"]
