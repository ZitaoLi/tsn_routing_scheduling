import logging
from typing import List
from intervals import IntInterval

from math import ceil

from src.graph.Flow import Flow
from src.graph.TimeSlotAllocator import TimeSlotAllocator, AllocationBlock
from src.graph.allocating_strategy.AEAPAllocatingStrategy import AEAPAllocatingStrategy
from src.graph.allocating_strategy.AllocatingStrategy import AllocatingStrategy

logger = logging.getLogger(__name__)


class AEAPBFAllocatingStrategy(AEAPAllocatingStrategy):

    @staticmethod
    def _allocate(flow: Flow, allocator: TimeSlotAllocator,
                  arrival_time_offset: int, allocation_num: int, phase_num: int) -> int:
        free_blocks: List[IntInterval] = sorted(allocator.free_intervals, key=lambda b: b.lower)
        free_blocks.sort(key=lambda b: b.upper - b.lower + 1)
        if free_blocks is None or free_blocks.__len__() == 0:  # out of free blocks
            return -1
        free_blocks = list(filter(lambda b: b.upper - b.lower + 1 >= allocation_num, free_blocks))
        if free_blocks is None or free_blocks.__len__() == 0:  # no available free blocks
            return -1
        for block in free_blocks:
            send_time_offset: int = block.lower * allocator.time_slot_len
            for i in range(block.lower, block.upper - allocation_num):
                if allocator.try_allocate(send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period):
                    allocator.allocate(flow, arrival_time_offset, send_time_offset, phase_num, allocation_num)
                    return send_time_offset
                send_time_offset += allocator.time_slot_len
        return -1
