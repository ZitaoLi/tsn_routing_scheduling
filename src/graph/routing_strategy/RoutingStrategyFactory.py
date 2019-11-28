from src.graph.Graph import Graph
from src.graph.routing_strategy.BackTrackingRedundantRoutingStrategy import BackTrackingRedundantRoutingStrategy
from src.graph.routing_strategy.RoutingStrategy import RoutingStrategy
from src.type import ROUTING_STRATEGY


class RoutingStrategyFactory(object):

    @staticmethod
    def get_instance(strategy_name: str, graph: Graph, *args, **kwargs) -> RoutingStrategy:
        if strategy_name == ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY:
            return BackTrackingRedundantRoutingStrategy(
                graph.nodes, graph.edges, graph.flows, graph.node_mapper, graph.edge_mapper, graph.flow_mapper)
        else:
            raise RuntimeError("routing strategy doesn't exist")
