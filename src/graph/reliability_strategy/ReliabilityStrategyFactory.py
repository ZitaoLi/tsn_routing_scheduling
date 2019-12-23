from src.graph.Graph import Graph
from src.graph.reliability_strategy.EnumerationMethodReliabilityStrategy import EnumerationMethodReliabilityStrategy
from src.graph.reliability_strategy.MultiRoutesReliabilityStrategy import MultiRoutesReliabilityStrategy
from src.graph.reliability_strategy.ReliabilityStrategy import ReliabilityStrategy
from src.type import  RELIABILITY_STRATEGY


class ReliabilityStrategyFactory(object):

    @staticmethod
    def get_instance(strategy_name: str, graph: Graph, *args, **kwargs) -> ReliabilityStrategy:
        if strategy_name == RELIABILITY_STRATEGY.MULTI_ROUTES_RELIABILITY_STRATEGY:
            return MultiRoutesReliabilityStrategy(graph.nodes, graph.edges, graph.flows, graph.node_mapper,
                                                  graph.edge_mapper, graph.flow_mapper)
        elif strategy_name == RELIABILITY_STRATEGY.ENUMERATION_METHOD_RELIABILITY_STRATEGY:
            return EnumerationMethodReliabilityStrategy(graph.nodes, graph.edges, graph.flows, graph.node_mapper,
                                                        graph.edge_mapper, graph.flow_mapper)
        else:
            raise RuntimeError("reliability strategy doesn't exist")
