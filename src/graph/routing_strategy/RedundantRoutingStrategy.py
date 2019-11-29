import abc
from typing import List, Set

from src.graph.routing_strategy.RoutingStrategy import RoutingStrategy
from src.type import FlowId


class RedundantRoutingStrategy(RoutingStrategy, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def route(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        pass
