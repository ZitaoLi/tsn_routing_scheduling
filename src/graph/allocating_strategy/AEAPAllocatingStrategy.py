import logging
from typing import List

from math import ceil

from src.graph.Flow import Flow
from src.graph.TimeSlotAllocator import TimeSlotAllocator, AllocationBlock
from src.graph.allocating_strategy.AllocatingStrategy import AllocatingStrategy

logger = logging.getLogger(__name__)


class AEAPAllocatingStrategy(AllocatingStrategy):

    @staticmethod
    def attempt_synchronize(flow: Flow, allocator: TimeSlotAllocator,
                            arrival_time_offset: int, allocation_num: int, phase_num: int) -> int:
        _B: List[AllocationBlock] = allocator.flow_times_mapper.get(flow.flow_id)
        if _B is None or _B.__len__() == 0:
            return -1
        _B = list(filter(lambda b: b.phase == 0, _B))
        if _B is not None and len(_B) != 0:
            for _b in _B:
                if arrival_time_offset <= _b.send_time_offset:
                    _send_time_offset: int = _b.send_time_offset
                    if allocator.try_allocate(_send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period,
                                              overlaped=True):
                        allocator.allocate(flow, arrival_time_offset, _send_time_offset, phase_num, allocation_num)
                        return _send_time_offset
                    else:
                        logger.error('allocate time slots error on edge [' + str(allocator.edge_id) + ']')
                        logger.error('send time offset: ' + str(_send_time_offset))
                        logger.error('error interval: ' + str([_b.interval.lower, _b.interval.upper]))
        return -1

    @staticmethod
    def _allocate(flow: Flow, allocator: TimeSlotAllocator,
                  arrival_time_offset: int, allocation_num: int, phase_num: int) -> int:
        _send_time_offset: int = arrival_time_offset
        # flow cannot be delayed more than (number of time slots on edge - number of needed time slots)
        for _i in range(allocator.time_slot_num - allocation_num):
            if allocator.try_allocate(_send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period):
                allocator.allocate(flow, arrival_time_offset, _send_time_offset, phase_num, allocation_num)
                return _send_time_offset
            _send_time_offset += allocator.time_slot_len
        return -1

    def allocate(self, flow: Flow, allocator: TimeSlotAllocator, arrival_time_offset: int, *args, **kwargs):
        allocation_num: int = ceil(flow.size / allocator.bandwidth / allocator.time_slot_len)  # needed time slots
        phase_num: int = ceil(allocator.hyper_period / flow.period)  # number of repetitions
        _send_time_offset: int = 0  # packet send time
        _next_arrival_time_offset: int = 0  # packet arrival time at next hop
        # if arrival time offset dost not exceed send time offset,
        # then we can delay it and make it overlapped fully
        # otherwise, we can just allocate it as early as possible
        _send_time_offset = self.attempt_synchronize(flow, allocator, arrival_time_offset, allocation_num, phase_num)
        if _send_time_offset == -1:
            _send_time_offset = self._allocate(flow, allocator, arrival_time_offset, allocation_num, phase_num)
        if _send_time_offset != -1:
            _next_arrival_time_offset = _send_time_offset + (allocation_num * allocator.time_slot_len) + \
                                        allocator.propagation_delay + allocator.process_delay
            logger.info(allocator.to_string())
            return _next_arrival_time_offset
        else:
            logger.info('allocate time slots for flow [' + str(flow.flow_id) + '] failure')
            return -1

        # _B: List[AllocationBlock] = allocator.flow_times_mapper.get(flow.flow_id)
        # _flag: bool = False
        # if _B is not None and len(_B) != 0:
        #     __B: List[AllocationBlock] = list(filter(lambda b: b.phase == 0, _B))
        #     if len(__B) != 0 and __B is not None:
        #         # TODO cannot cover every cases and need to add loop here
        #         _b: AllocationBlock = __B[0]
        #         # if arrival time offset dost not exceed send time offset,
        #         # then we can delay it and make it overlapped fully
        #         # otherwise, we can just allocate it as early as possible
        #         if arrival_time_offset <= _b.send_time_offset:
        #             _send_time_offset = _b.send_time_offset
        #             if allocator.try_allocate(_send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period,
        #                                       overlaped=True):
        #                 allocator.allocate(flow, arrival_time_offset, _send_time_offset, phase_num, allocation_num)
        #                 _flag = True
        #             else:
        #                 logger.error('allocate time slots error on edge [' + str(allocator.edge_id) + ']')
        #                 logger.error('send time offset: ' + str(_send_time_offset))
        #                 logger.error('error interval: ' + str([_b.interval.lower, _b.interval.upper]))
        #                 # self.to_string()
        #                 return -1
        # # cannot delay to save time slots
        # # search available time slot from first arrival time
        # if _flag is False:
        #     _send_time_offset = arrival_time_offset
        #     # flow cannot be delayed more than (number of time slots on edge - number of needed time slots)
        #     for _i in range(allocator.time_slot_num - allocation_num):
        #         if allocator.try_allocate(_send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period):
        #             allocator.allocate(flow, arrival_time_offset, _send_time_offset, phase_num, allocation_num)
        #             _flag = True
        #             break
        #         _send_time_offset += allocator.time_slot_len
        # if _flag is False:  # allocation failure
        #     logger.info('allocate time slots for flow [' + str(flow.flow_id) + '] failure')
        #     return -1
        # else:
        #     _next_arrival_time_offset = _send_time_offset + (allocation_num * allocator.time_slot_len) + \
        #                                 allocator.propagation_delay + allocator.process_delay
        #     allocator.to_string()
        #     return _next_arrival_time_offset
