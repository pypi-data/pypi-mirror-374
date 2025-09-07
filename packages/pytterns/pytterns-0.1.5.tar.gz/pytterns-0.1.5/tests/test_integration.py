import pytest
from pytterns import strategy, chain, load

@strategy("integration_test")
class IntegrationStrategyA:
    def check(self, value):
        return value == "A"
    def execute(self):
        return "IntegrationStrategyA executed"

@strategy("integration_test")
class IntegrationStrategyB:
    def check(self, value):
        return value == "B"
    def execute(self):
        return "IntegrationStrategyB executed"

@strategy("integration_without_check")
class IntegrationStrategyNoCheck:
    def execute(self):
        return "IntegrationStrategyNoCheck executed"

@strategy("integration_without_check_more_then_one")
class IntegrationStrategyNoCheckMoreThenOneA:
    def execute(self):
        return "IntegrationStrategyNoCheckMoreThenOneA executed"

@strategy("integration_without_check_more_then_one")
class IntegrationStrategyNoCheckMoreThenOneB:
    def execute(self):
        return "IntegrationStrategyNoCheckMoreThenOneB executed"

def test_full_integration():
    strategy_instance = load.strategy("integration_test").check("A")
    assert strategy_instance.__class__.__name__ == "IntegrationStrategyA"

def test_full_integration_not_found():
    with pytest.raises(ValueError, match="No strategy in 'integration_test' passed the 'check' filter"):
        load.strategy("integration_test").check("C")

def test_full_integration_execute():
    strategy_instance = load.strategy("integration_test").check("A").execute()
    assert strategy_instance == "IntegrationStrategyA executed"

def test_full_integration_no_check():
    strategy_value = load.strategy("integration_without_check").execute()
    assert strategy_value == "IntegrationStrategyNoCheck executed"

def test_full_integration_no_check_more_then_one_pick_first_one():
    strategy_value = load.strategy("integration_without_check_more_then_one").execute()
    assert strategy_value == "IntegrationStrategyNoCheckMoreThenOneA executed"
