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

    @abc.abstractmethod
    def route(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        pass

    def check_e2e_reliability(self, routes: List[List[EdgeId]], src: NodeId, dest: NodeId, *args, **kwargs) -> bool:
        return self._reliability_strategy.check_e2e_reliability(routes, src, dest, *args, **kwargs)
