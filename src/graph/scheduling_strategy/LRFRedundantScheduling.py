import copy
import logging
from typing import List, Set

from math import ceil

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.TimeSlotAllocator import TimeSlotAllocator, AllocationBlock
from src.graph.scheduling_strategy.RedundantSchedulingStrategy import RedundantSchedulingStrategy
from src.graph.scheduling_strategy.SchedulingStrategy import SchedulingStrategy
from src.type import FlowId

logger = logging.getLogger(__name__)


# long-routes-first redundant scheduling strategy
class LRFRedundantSchedulingStrategy(RedundantSchedulingStrategy):

    @staticmethod
    def sort_route(routes: List[List[int]]) -> List[List[int]]:
        """
        sort flows list by priority from <sum of edge delay> to <period> to <hops> [NOTED]
        :param routes: flow routes to sort
        :return: sorted flow routes
        """
        # TODO sort routes of flow
        _routes = sorted(routes, key=lambda r: len(r), reverse=True)
        return _routes

    def schedule(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        sorting_enabled: bool = True
        if 'sorting_enabled' in kwargs.keys():
            sorting_enabled = kwargs['sorting_enabled']
            assert type(sorting_enabled) is bool, 'parameter "sorting_enabled" type must be bool'
        if sorting_enabled:
            flow_id_list = self.sort_flows_id_list(flow_id_list)
        for _fid in flow_id_list:
            if not self.schedule_single_flow(self.flow_mapper[_fid]):
                self.failure_queue.add(_fid)
                logger.info('add flow [' + str(_fid) + '] into failure queue')
        logger.info('FAILURE QUEUE:' + str(self.failure_queue))
        return self.failure_queue

    def schedule_single_flow(self, flow: Flow) -> bool:
        logger.info('schedule flow [' + str(flow.flow_id) + ']...')
        _all_routes: List[List[List[int]]] = flow.get_routes()
        _union_routes: List[List[int]] = []
        for _e2e_routes in _all_routes:
            for _e2e_route in _e2e_routes:
                _union_routes.append(_e2e_route)
        _union_routes = LRFRedundantSchedulingStrategy.sort_route(_union_routes)
        _ER: List[int] = []  # recover list
        for _e2e_route in _union_routes:
            if not self.schedule_end2end(flow, _e2e_route):
                logger.info('scheduling flow [' + str(flow.flow_id) + '] failure')
                # TODO recover time slots allocation on edge
                for __e2e_route in _ER:
                    for _eid in __e2e_route:
                        self.edge_mapper[_eid].time_slot_allocator.recover_scene()
                return False
            else:
                _ER.append(_e2e_route)
        logger.info('scheduling flow [' + str(flow.flow_id) + '] successful')
        return True

    def schedule_end2end(self, flow: Flow, route: List[int]) -> bool:
        _arrival_time_offset: int = 0
        _E: List[Edge] = []
        for _eid in route:
            _e: Edge = self.edge_mapper[_eid]  # get edge
            _E.append(_e)
            _allocator: TimeSlotAllocator = _e.time_slot_allocator  # get time slot allocator
            _allocator.save_scene()  # save scene
            # _arrival_time_offset: int = self.allocate_aeap_overlap(flow, _allocator, _arrival_time_offset)
            _arrival_time_offset: int = self.allocate(flow, _allocator, _arrival_time_offset)
            # _arrival_time_offset: int = _allocator.allocate_aeap_overlap(flow, _arrival_time_offset)
            # _arrival_time_offset: int = _allocator.allocate_aeap(flow, _arrival_time_offset)
            # TODO fix bug here
            if _arrival_time_offset == -1 or _arrival_time_offset > flow.deadline:
                # recover scene
                for _e in _E:
                    _e.time_slot_allocator.recover_scene()
                return False
        return True

    def allocate_aeap_overlap(self, flow: Flow, allocator: TimeSlotAllocator, arrival_time_offset: int) -> int:
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
