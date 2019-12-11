import copy
import logging
import os
import pickle
import random
import time
from typing import List, Tuple, Set

from math import floor, ceil

import networkx as nx

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Graph import Graph
from src import config
from src.graph.TimeSlotAllocator import TimeSlotAllocator, AllocationBlock
from src.graph.allocating_strategy.AEAPAllocatingStrategy import AEAPAllocatingStrategy
from src.graph.allocating_strategy.AllocatingStrategy import AllocatingStrategy
from src.graph.allocating_strategy.AllocatingStrategyFactory import AllocatingStrategyFactory
from src.graph.routing_strategy.BackTrackingRedundantRoutingStrategy import BackTrackingRedundantRoutingStrategy
from src.graph.routing_strategy.RoutingStrategy import RoutingStrategy
from src.graph.routing_strategy.RoutingStrategyFactory import RoutingStrategyFactory
from src.graph.scheduling_strategy.LRFRedundantScheduling import LRFRedundantSchedulingStrategy
from src.graph.scheduling_strategy.SchedulingStrategy import SchedulingStrategy
from src.graph.scheduling_strategy.SchedulingStrategyFactory import SchedulingStrategyFactory
from src.graph.topo_strategy.TopoStrategy import TopoStrategy
from src.type import FlowId, TOPO_STRATEGY, ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY
from src.utils.Singleton import SingletonDecorator

logger = logging.getLogger(__name__)


class Solution:
    solution_name: str
    graph: Graph
    flows: List[Flow]
    failure_flows: List[FlowId]
    topo_strategy: TOPO_STRATEGY
    routing_strategy: ROUTING_STRATEGY
    scheduling_strategy: SCHEDULING_STRATEGY
    allocating_strategy: ALLOCATING_STRATEGY

    def __init__(self, graph: Graph = None, flows: List[Flow] = None,
                 topo_strategy: TOPO_STRATEGY = None,
                 routing_strategy: ROUTING_STRATEGY = None,
                 scheduling_strategy: SCHEDULING_STRATEGY = None,
                 allocating_strategy: ALLOCATING_STRATEGY = None,
                 solution_name: str = 'default'):
        self.graph = graph
        self.flows = [] if flows is None else flows
        self.failure_flows = []
        self.topo_strategy = topo_strategy
        self.routing_strategy = routing_strategy
        self.scheduling_strategy = scheduling_strategy
        self.allocating_strategy = allocating_strategy
        self.solution_name = solution_name


class Solver:
    final_solution: Solution
    visual: bool
    runtime: float

    def __init__(self, nx_graph: nx.Graph = None,
                 flows: List[Flow] = None,
                 topo_strategy: TOPO_STRATEGY = None,
                 routing_strategy: ROUTING_STRATEGY = None,
                 scheduling_strategy: SCHEDULING_STRATEGY = None,
                 allocating_strategy: ALLOCATING_STRATEGY = None,
                 solution_name: str = 'BaseSolution'):
        graph: Graph = Graph(nx_graph=nx_graph,
                             nodes=list(nx_graph.nodes),
                             edges=list(nx_graph.edges),
                             hp=config.GRAPH_CONFIG['hyper-period'])
        graph.set_all_edges_bandwidth(config.GRAPH_CONFIG['all-bandwidth'])
        graph.add_flows(flows)
        self.final_solution = Solution(graph, flows,
                                       topo_strategy=topo_strategy, routing_strategy=routing_strategy,
                                       scheduling_strategy=scheduling_strategy, allocating_strategy=allocating_strategy,
                                       solution_name=solution_name)
        self.visual = False
        self.runtime = 0

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

    def add_flows(self, flows: List[Flow]):
        [self.final_solution.flows.append(flow) for flow in flows]
        self.final_solution.graph.add_flows(flows)

    def add_flow(self, flow: Flow):
        self.final_solution.flows.append(flow)
        self.final_solution.graph.add_flows([flow])

    def generate_init_solution(self) -> Solution:
        _g: Graph = self.final_solution.graph
        _F_r: List[int] = [_flow.flow_id for _flow in self.final_solution.flows]
        logger.info('route ' + str(_F_r) + '...')
        # _g.flow_router.route_flows(_F)  # routing
        # set routing strategy and route flows
        _routing_strategy: RoutingStrategy = \
            RoutingStrategyFactory.get_instance(self.final_solution.routing_strategy, _g)
        _scheduling_strategy: SchedulingStrategy = \
            SchedulingStrategyFactory.get_instance(self.final_solution.scheduling_strategy, _g)
        _allocating_strategy: AllocatingStrategy = \
            AllocatingStrategyFactory.get_instance(self.final_solution.allocating_strategy)
        _g.flow_router.routing_strategy = _routing_strategy
        _g.flow_router.overlapped = config.GRAPH_CONFIG['overlapped-routing']
        start_time: time.process_time = time.perf_counter()  # start time
        _g.flow_router.route(_F_r)
        # select successful flows after routing
        _F_s = [_fid for _fid in _F_r if _fid not in _g.flow_router.failure_queue]
        logger.info('schedule ' + str(_F_s) + '...')
        # _g.flow_scheduler.schedule_flows(_F)  # scheduling
        # set scheduling and allocating strategy and schedule flows
        _g.flow_scheduler.scheduling_strategy = _scheduling_strategy
        _g.flow_scheduler.allocating_strategy = _allocating_strategy
        _g.flow_scheduler.schedule(_F_s)
        end_time: time.process_time = time.perf_counter()
        self.runtime = end_time - start_time
        _g.combine_failure_queue()
        self.final_solution.failure_flows = list(_g.failure_queue)
        # visualize Gannt chart
        if self.visual is True:
            _g.draw_gantt()
        return self.final_solution

    def optimize(self,
                 max_iterations: int = config.OPTIMIZATION['max_iterations'],
                 max_no_improve: int = config.OPTIMIZATION['max_no_improve'],
                 k: int = config.OPTIMIZATION['k']) -> Solution:
        start_time: time.process_time = time.perf_counter()
        _o: float = self.objective_function(self.final_solution)
        for i in range(max_iterations):
            _s: Solution = self.perturbate(k)  # perturbation to generate a new solution
            _s_hat: Solution = self.local_search(_s, max_no_improve)
            logger.info('local search objective function value = ' + str(self.objective_function(_s_hat)))
            self.apply_acceptance_criterion(_s_hat)
        end_time: time.process_time = time.perf_counter()
        self.runtime = end_time - start_time
        logger.info('initial objective function value = ' + str(_o))
        logger.info('final objective function value = ' + str(self.objective_function(self.final_solution)))
        return self.final_solution

    def local_search(self, _s: Solution, max_no_improve: int) -> Solution:
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
            _sc.graph.flow_scheduler.schedule(_F)  # scheduling
            # recombination failure queue
            _sc.graph.combine_failure_queue()
            if _o == 0:
                _o = self.objective_function(_sc)
                _sf = copy.deepcopy(_sc)
            else:
                _oc: float = self.objective_function(_sc)
                if _oc < _o:
                    _o = _oc
                    _sf = copy.deepcopy(_sc)
                elif _oc == _o:
                    pass  # TODO how to handle the same situation?
        return _sf

    def perturbate(self, k: float) -> Solution:
        # TODO perturbate solution
        _s: Solution = copy.deepcopy(self.final_solution)
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

    def apply_acceptance_criterion(self, _s_hat: Solution):
        o1: float = self.objective_function(self.final_solution)
        o2: float = self.objective_function(_s_hat)
        if o2 < o1:
            self.final_solution = copy.deepcopy(_s_hat)  # deep copy here
        elif o2 == o1:
            pass  # TODO how to handle the same situation?

    def save_solution(self, solution: Solution = None, filename: str = None):
        if solution is None:
            raise RuntimeError('miss parameters')
        import os
        import pickle
        if filename is None:
            filename = os.path.join(config.solutions_res_dir, solution.solution_name)
        with open(filename, 'wb') as f:
            pickle.dump(solution, f)

    def draw_gantt_chart(self, solution: Solution):
        solution.graph.draw_gantt()

    def generate_solution_name(self, solution: Solution = None, prefix: str = '', postfix: str = '') -> str:
        if solution is None:
            raise RuntimeError('parameter "solution" is required')
        solution_name: str = str(solution.topo_strategy) + \
                        str(solution.routing_strategy) + \
                        str(solution.scheduling_strategy) + \
                        str(solution.allocating_strategy)
        solution_name = solution_name.replace('.', '_').\
            replace('ROUTING', '').replace('SCHEDULING', '').\
            replace('ALLOCATING', '').replace('TOPO', '').\
            replace('REDUNDANT', '').replace('STRATEGY', '').replace('SINGLE_', '').replace('__', '_')
        solution_name = prefix + solution_name + postfix
        solution_name = solution_name.lower()
        solution.solution_name = solution_name  # 副作用
        return solution_name

    def analyze(self, solution: Solution, target_filename: str = None):
        flow_id_list: List[FlowId] = [flow.flow_id for flow in solution.flows]
        failed_flow_id_list: List[FlowId] = solution.failure_flows
        successful_flow_id_list: List[FlowId] = list(set(flow_id_list) - set(failed_flow_id_list))
        successful_flow: List[Flow] = list(filter(lambda flow: flow.flow_id in successful_flow_id_list, solution.flows))
        bandwidth_list: List[float] = [flow.bandwidth for flow in successful_flow]
        flow_num: int = len(flow_id_list)  # number of flows
        edge_list: List[Edge] = list(solution.graph.edge_mapper.values())
        edge_num: int = len(edge_list)
        node_num: int = len(solution.graph.nodes)
        load_list: List[float] = [edge.time_slot_allocator.load for edge in edge_list]
        import numpy as np
        successful_flow_num: int = len(successful_flow_id_list)  # number of successful flows
        ideal_throughput: float = sum(bandwidth_list)  # ideal throughput
        actual_throughput: float = 0.0  # actual throughput
        max_load: float = np.max(load_list)  # maximum load
        min_load: float = np.min(load_list)  # min load
        average_load: float = np.average(load_list)  # averaged load
        median_load: float = np.median(load_list)  # median load
        runtime: float = '{:.9f}'.format(self.runtime)
        logger.info('number of successful flows: ' + str(successful_flow_num))
        logger.info('ideal throughput: ' + str(ideal_throughput * 1000) + 'Mbps')
        logger.info('runtime: {}s'.format(runtime))
        logger.info('maximun load {}%'.format(max_load * 100))
        logger.info('average load {}%'.format(average_load * 100))
        import csv
        with open(target_filename + '.csv', 'a', newline='') as file:
            writer: csv.writer = csv.writer(file)
            line: list = [
                flow_num,  # number of flows
                node_num,  # number of nodes
                edge_num,  # number of edges
                successful_flow_num,  # number of successful flows
                ideal_throughput,  # ideal throughput
                actual_throughput,  # actual throughput
                runtime,  # runtime
                max_load,  # maximum load
                min_load,  # minimum load
                average_load,  # average load
                median_load  # median load
            ]
            writer.writerow(line)
