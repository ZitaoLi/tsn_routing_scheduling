import abc

from src.graph.scheduling_strategy.SchedulingStrategy import SchedulingStrategy


class SingleSchedulingStrategy(SchedulingStrategy, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def schedule(self, flow_id_list: List[FlowId], *args, **kwargs):
        pass
