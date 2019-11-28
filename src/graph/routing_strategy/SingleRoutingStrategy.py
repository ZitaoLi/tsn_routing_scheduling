import abc
from typing import List

from src.graph.routing_strategy.RoutingStrategy import RoutingStrategy
from src.type import FlowId


class SingleRoutingStrategy(RoutingStrategy, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def route(self, flow_id_list: List[FlowId], *args, **kwargs):
        pass
