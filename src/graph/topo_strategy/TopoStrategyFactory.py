from src.graph.topo_strategy.TopoStrategy import TopoStrategy
from src.type import TOPO_STRATEGY


class TopoStrategyFactory(object):

    @staticmethod
    def get_instance(strategy_name: str, *args, **kwargs) -> TopoStrategy:
        # TODO topology strategy factory method
        if strategy_name == TOPO_STRATEGY.ER_STRATEGY:
            pass
        else:
            raise RuntimeError("allocating strategy doesn't exist")
