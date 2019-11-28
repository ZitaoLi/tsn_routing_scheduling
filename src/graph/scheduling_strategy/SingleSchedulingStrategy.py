import abc
from typing import List

from src.graph.scheduling_strategy.SchedulingStrategy import SchedulingStrategy
from src.type import FlowId


class SingleSchedulingStrategy(SchedulingStrategy, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def schedule(self, flow_id_list: List[FlowId], *args, **kwargs):
        pass
