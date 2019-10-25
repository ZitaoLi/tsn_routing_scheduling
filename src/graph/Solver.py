import copy
import logging
import os
import pickle
import random
from typing import List, Tuple, Set

from math import floor, ceil

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Graph import Graph
from src import config
from src.graph.TimeSlotAllocator import TimeSlotAllocator, AllocationBlock

logger = logging.getLogger(__name__)


class Solution:
    graph: Graph
    flows: List[Flow]
    failure_flow: List[Flow]

    def __init__(self, graph: Graph, flows: List[Flow]):
        self.graph = graph
        self.flows = flows


class Solver:
    final_solution: Solution
    solution_copy: Solution

    @staticmethod
    def objective_function(s: Solution) -> float:
        _m: int = s.graph.failure_queue.__len__()
        _t: List[Tuple[int, int]] = [
            (_e.time_slot_allocator.time_slot_used, _e.time_slot_allocator.time_slot_num) for _e in
            s.graph.edge_mapper.values()]  # Tuple(number of time slots used, number of all time slots)
        _max_t: Tuple[int, int] = max(_t, key=lambda x: x[0])
        _max_ts_used: int = _max_t[0]
        _ts_num: int = _t[_t.index(_max_t)][1]
        return _m + _max_ts_used / _ts_num

    @classmethod
    def generate_init_solution(cls, nodes: List[int], edges: List[Tuple[int]], flows: List[Flow], visual: bool = True):
        _g: Graph = Graph(nodes=nodes, edges=edges, hp=config.GRAPH_CONFIG['hyper-period'])
        _g.set_all_edges_bandwidth(config.GRAPH_CONFIG['all-bandwidth'])
        _g.flow_router.set_overlapped(config.GRAPH_CONFIG['overlapped-routing'])
        _g.add_flows(flows)
        _F: List[int] = [_flow.flow_id for _flow in flows]
        _g.flow_router.route_flows(_F)  # routing
        _F = [_fid for _fid in _F if _fid not in _g.flow_router.failure_queue]
        _g.flow_scheduler.schedule_flows(_F)  # scheduling
        _g.combine_failure_queue()
        if visual is True:
            _g.draw_gantt()
        cls.final_solution = Solution(_g, flows)
        # TODO save solution
        file = os.path.join(os.path.join(os.path.abspath('.'), 'json'), 'solution')
        with open(file, 'wb') as f:
            pickle.dump(cls.final_solution, f)
        return _g

    @classmethod
    def optimize(cls, max_iterations: int, max_no_improve: int, k: int, visual: bool = True):
        _o: float = cls.objective_function(cls.final_solution)
        for i in range(max_iterations):
            _s: Solution = cls.perturbate(k)  # perturbation to generate a new solution
            _s_hat: Solution = cls.local_search(_s, max_no_improve)
            logger.info('local search objective function value = ' + str(cls.objective_function(_s_hat)))
            cls.apply_acceptance_criterion(_s_hat)
        logger.info('initial objective function value = ' + str(_o))
        logger.info('final objective function value = ' + str(cls.objective_function(cls.final_solution)))
        if visual is True:
            cls.final_solution.graph.draw_gantt()
        # TODO save solution
        file = os.path.join(os.path.join(os.path.abspath('.'), 'json'), 'solution')
        with open(file, 'wb') as f:
            pickle.dump(cls.final_solution, f)

    @classmethod
    def local_search(cls, _s: Solution, max_no_improve: int) -> Solution:
        # TODO local search
        _sf: Solution = _s
        _o: float = 0.0
        _F: List[int] = list(_s.graph.failure_queue)  # flows need reroute and reschedule
        for _i in range(max_no_improve):
            _sc: Solution = copy.deepcopy(_s)
            random.shuffle(_F)  # shuffle the list
            logger.info('reroute and reschedule flows: ' + str(_F))
            # reset failure queue
            _sc.graph.failure_queue = set()
            _sc.graph.flow_router.failure_queue = set()
            _sc.graph.flow_scheduler.failure_queue = set()
            # rerouting
            _sc.graph.flow_router.route_flows(_F)
            _F = [_fid for _fid in _F if _fid not in _s.graph.flow_router.failure_queue]
            # rescheduling
            _sc.graph.flow_scheduler.schedule_flows(_F)
            # recombination failure queue
            _sc.graph.combine_failure_queue()
            if _o == 0:
                _o = cls.objective_function(_sc)
                _sf = copy.deepcopy(_sc)
            else:
                _oc: float = cls.objective_function(_sc)
                if _oc < _o:
                    _o = _oc
                    _sf = copy.deepcopy(_sc)
                elif _oc == _o:
                    pass  # TODO how to handle the same situation?
        return _sf

    @classmethod
    def perturbate(cls, k: float) -> Solution:
        # TODO perturbate solution
        _s: Solution = copy.deepcopy(cls.final_solution)
        _F: List[Flow] = [_flow for _flow in _s.flows if _flow.flow_id not in _s.graph.failure_queue]
        _remove_flows: List[Flow] = random.sample(_F, floor(_s.flows.__len__() * k))
        _s.graph.failure_queue = _s.graph.failure_queue.union(set([_flow.flow_id for _flow in _remove_flows]))
        logger.info('randomly remove flows: ' + str([_flow.flow_id for _flow in _remove_flows]))
        logger.info('WHOLE FAILURE QUEUE:' + str(_s.graph.failure_queue))
        for _flow in _remove_flows:
            for _eid in _flow.walked_edges:
                _e: Edge = _s.graph.edge_mapper[_eid]
                _allocator: TimeSlotAllocator = _e.time_slot_allocator
                # recover weight on edge
                _e.weight -= _flow.bandwidth / _e.bandwidth
                # recover flow time slots without merging operation mapper and time slots list without merging operation
                if _flow.flow_id in _allocator.flow_times_mapper:
                    _flow_time_slots: List[AllocationBlock] = \
                        _allocator.flow_times_mapper[_flow.flow_id].copy()  # deep copy
                    del _allocator.flow_times_mapper[_flow.flow_id]
                    for _ts in _flow_time_slots:
                        _allocator.allocation_blocks.remove(_ts)
                # recover load, time slots used and flow time slots with merging operation
                _time_slots_m: List[AllocationBlock] = _allocator.allocation_blocks_m.copy()  # deep copy
                _flow_time_slots_m: List[AllocationBlock] = []
                [_flow_time_slots_m.append(_block) for _block in _time_slots_m if _block.flow_id == _flow.flow_id]
                _load_sum: int = 0
                for _block_m in _flow_time_slots_m:
                    _load_sum += _block_m.interval.upper - _block_m.interval.lower + 1
                _allocator.time_slot_used -= _load_sum
                _allocator.load = _allocator.time_slot_used / _allocator.time_slot_num
                for _ts_m in _flow_time_slots_m:
                    _allocator.allocation_blocks_m.remove(_ts_m)
                # recover number of flow
                _allocator.flow_num -= 1
            # recover routes of flow
            _flow.routes = []  # empty routes of flow
            # recover walked edges of flow
            _flow.walked_edges = set()
        return _s

    @classmethod
    def apply_acceptance_criterion(cls, _s_hat: Solution):
        o1: float = cls.objective_function(cls.final_solution)
        o2: float = cls.objective_function(_s_hat)
        if o2 < o1:
            cls.final_solution = copy.deepcopy(_s_hat)  # deep copy here
        elif o2 == o1:
            pass  # TODO how to handle the same situation?
