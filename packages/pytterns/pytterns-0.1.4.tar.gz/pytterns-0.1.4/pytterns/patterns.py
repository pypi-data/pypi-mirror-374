from pytterns.core.loaders import StrategyLoader, ChainLoader
from pytterns.core.loaders import ObserverLoader
from pytterns.core.loaders import FactoryLoader, CommandLoader

class load:
    @staticmethod
    def strategy(grouper):
        return StrategyLoader(grouper)
    
    @staticmethod
    def chain(grouper):
        return ChainLoader(grouper)

    @staticmethod
    def observer(event):
        return ObserverLoader(event)

    @staticmethod
    def factory(name):
        return FactoryLoader(name)

    @staticmethod
    def command(name):
        return CommandLoader(name)
