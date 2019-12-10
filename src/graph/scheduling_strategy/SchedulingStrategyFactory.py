from src.graph.Graph import Graph
from src.graph.scheduling_strategy.LRFRedundantScheduling import LRFRedundantSchedulingStrategy
from src.graph.scheduling_strategy.SchedulingStrategy import SchedulingStrategy
from src.type import  SCHEDULING_STRATEGY


class SchedulingStrategyFactory(object):

    @staticmethod
    def get_instance(strategy_name: str, graph: Graph, *args, **kwargs) -> SchedulingStrategy:
        if strategy_name == SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY:
            return LRFRedundantSchedulingStrategy(
                graph.nodes, graph.edges, graph.flows, graph.node_mapper, graph.edge_mapper, graph.flow_mapper)
        else:
            raise RuntimeError("scheduling strategy doesn't exist")
