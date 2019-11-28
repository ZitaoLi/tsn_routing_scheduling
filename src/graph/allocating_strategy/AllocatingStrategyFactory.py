from src.graph.Graph import Graph
from src.graph.allocating_strategy.AEAPAllocatingStrategy import AEAPAllocatingStrategy
from src.graph.allocating_strategy.AllocatingStrategy import AllocatingStrategy
from src.type import ALLOCATING_STRATEGY


class AllocatingStrategyFactory(object):

    @staticmethod
    def get_instance(strategy_name: str, *args, **kwargs) -> AllocatingStrategy:
        if strategy_name == ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY:
            return AEAPAllocatingStrategy()
        else:
            raise RuntimeError("allocating strategy doesn't exist")
