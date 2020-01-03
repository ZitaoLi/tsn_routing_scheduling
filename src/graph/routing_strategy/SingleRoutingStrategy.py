import abc
from typing import List, Set, Dict

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Node import Node
from src.graph.reliability_strategy.UniRoutesReliabilityStrategy import UniRoutesReliabilityStrategy
from src.graph.routing_strategy.RoutingStrategy import RoutingStrategy
from src.type import FlowId


class SingleRoutingStrategy(RoutingStrategy, metaclass=abc.ABCMeta):

    def __init__(self, nodes: List[int], edges: List[int], flows: List[int], node_mapper: Dict[int, Node],
                 edge_mapper: Dict[int, Edge], flow_mapper: Dict[int, Flow]):
        super().__init__(nodes, edges, flows, node_mapper, edge_mapper, flow_mapper)
        # default reliability strategy is UniRoutesReliabilityStrategy
        self._reliability_strategy = \
            UniRoutesReliabilityStrategy(nodes, edges, flows, node_mapper, edge_mapper, flow_mapper)

    @abc.abstractmethod
    def route(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        pass
