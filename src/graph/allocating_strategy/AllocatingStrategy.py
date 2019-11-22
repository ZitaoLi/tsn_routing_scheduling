import abc

from src.graph.Flow import Flow
from src.graph.TimeSlotAllocator import TimeSlotAllocator


class AllocatingStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def allocate(self, flow: Flow, allocator: TimeSlotAllocator, arrival_time_offset: int, *args, **kwargs):
        pass
