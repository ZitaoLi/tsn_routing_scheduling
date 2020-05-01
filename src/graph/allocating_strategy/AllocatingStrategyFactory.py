from src.graph.Graph import Graph
from src.graph.allocating_strategy.AEAPBFAllocatingStrategy import AEAPBFAllocatingStrategy
from src.graph.allocating_strategy.AEAPWFAllocatingStrategy import AEAPWFAllocatingStrategy
from src.graph.allocating_strategy.AEAPAllocatingStrategy import AEAPAllocatingStrategy
from src.graph.allocating_strategy.AllocatingStrategy import AllocatingStrategy
from src.type import ALLOCATING_STRATEGY


class AllocatingStrategyFactory(object):

    @staticmethod
    def get_instance(strategy_name: str, *args, **kwargs) -> AllocatingStrategy:
        if strategy_name == ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY:
            return AEAPAllocatingStrategy()
        elif strategy_name == ALLOCATING_STRATEGY.AEAPBF_ALLOCATING_STRATEGY:
            return AEAPBFAllocatingStrategy()
        elif strategy_name == ALLOCATING_STRATEGY.AEAPWF_ALLOCATING_STRATEGY:
            return AEAPWFAllocatingStrategy()
        else:
            raise RuntimeError("allocating strategy doesn't exist")
