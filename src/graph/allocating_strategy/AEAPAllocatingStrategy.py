import logging
from typing import List

from math import ceil

from src.graph.Flow import Flow
from src.graph.TimeSlotAllocator import TimeSlotAllocator, AllocationBlock
from src.graph.allocating_strategy.AllocatingStrategy import AllocatingStrategy

logger = logging.getLogger(__name__)


class AEAPAllocatingStrategy(AllocatingStrategy):

    def allocate(self, flow: Flow, allocator: TimeSlotAllocator, arrival_time_offset: int, *args, **kwargs):
        allocation_num: int = ceil(flow.size / allocator.bandwidth / allocator.time_slot_len)  # needed time slots
        phase_num: int = ceil(allocator.hyper_period / flow.period)  # number of repetitions
        _send_time_offset: int = 0  # packet send time
        _next_arrival_time_offset: int = 0  # packet arrival time at next hop
        _B: List[AllocationBlock] = allocator.flow_times_mapper.get(flow.flow_id)
        _flag: bool = False
        if _B is not None:
            _b: AllocationBlock = list(filter(lambda b: b.phase == 0, _B))[0]
            # if arrival time offset dost not exceed send time offset, then we can delay it and make it overlapped fully
            # otherwise, we can just allocate it as early as possible
            if arrival_time_offset <= _b.send_time_offset:
                _send_time_offset = _b.send_time_offset
                if allocator.try_allocate(_send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period,
                                          overlaped=True):
                    allocator.allocate(flow, arrival_time_offset, _send_time_offset, phase_num, allocation_num)
                    _flag = True
                else:
                    logger.error('allocate time slots error on edge [' + str(allocator.edge_id) + ']')
                    logger.error('send time offset: ' + str(_send_time_offset))
                    logger.error('error interval: ' + str([_b.interval.lower, _b.interval.upper]))
                    # self.to_string()
                    return -1
        if _flag is False:
            _send_time_offset = arrival_time_offset
            # flow cannot be delayed more than (number of time slots on edge - number of needed time slots)
            for _i in range(allocator.time_slot_num - allocation_num):
                if allocator.try_allocate(_send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period):
                    allocator.allocate(flow, arrival_time_offset, _send_time_offset, phase_num, allocation_num)
                    _flag = True
                    break
                _send_time_offset += allocator.time_slot_len
        # allocation failure
        if _flag is False:
            logger.info('allocate time slots for flow [' + str(flow.flow_id) + '] failure')
            return -1
        else:
            _next_arrival_time_offset = _send_time_offset + (allocation_num * allocator.time_slot_len) + \
                                        allocator.propagation_delay + allocator.process_delay
            allocator.to_string()
            return _next_arrival_time_offset
