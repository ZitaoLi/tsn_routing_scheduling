import abc
from typing import List, Set, Dict

from src.graph.Node import Node
from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.reliability_strategy.MultiRoutesReliabilityStrategy import MultiRoutesReliabilityStrategy
from src.graph.reliability_strategy.ReliabilityStrategy import ReliabilityStrategy
from src.graph.routing_strategy.RoutingStrategy import RoutingStrategy
from src.type import FlowId, EdgeId, NodeId


class RedundantRoutingStrategy(RoutingStrategy, metaclass=abc.ABCMeta):

    def __init__(self, nodes: List[int], edges: List[int], flows: List[int], node_mapper: Dict[int, Node],
                 edge_mapper: Dict[int, Edge], flow_mapper: Dict[int, Flow]):
        super().__init__(nodes, edges, flows, node_mapper, edge_mapper, flow_mapper)
        self._reliability_strategy = \
            MultiRoutesReliabilityStrategy(nodes, edges, flows, node_mapper, edge_mapper, flow_mapper)

    @abc.abstractmethod
    def route(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        pass
