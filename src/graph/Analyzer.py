import csv
import json
import logging
import math
import numpy as np
from typing import List, Dict, Tuple, Set

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Graph import Graph
from src.graph.Solver import Solution
from src.graph.TimeSlotAllocator import TimeSlotAllocator
from src.type import FlowId, NodeId, EdgeId

logger = logging.getLogger(__name__)


class Analyzer(object):

    @staticmethod
    def calculate_e2e_delay(graph: Graph, flow: Flow) -> int:
        destinations: List[NodeId] = flow.destinations
        edges: List[Edge] = list(graph.edge_mapper.values())
        destination_edges: List[Edge] = list(filter(lambda e: e.out_node.node_id in destinations, edges))
        delay_list: List[int] = []
        for edge in destination_edges:
            for block in edge.time_slot_allocator.flow_times_mapper[flow.flow_id]:
                delay_list.append(block.send_time_offset + math.ceil(flow.size / edge.time_slot_allocator.bandwidth))
        return int(np.mean(delay_list))

    @staticmethod
    def calculate_guard_band_on_edge(allocator: TimeSlotAllocator) -> int:
        total_guard_band: int = 0
        block_num = len(allocator.allocation_blocks_m)
        for i in range(block_num):
            if i + 1 < block_num and allocator.allocation_blocks_m[i].interval.upper + 1 != \
                    allocator.allocation_blocks_m[i + 1].interval.lower:
                total_guard_band += 1
        return total_guard_band

    @staticmethod
    def analyze_per_flow(solution: Solution, target_filename: str = None):
        flow_id_list: List[FlowId] = [flow.flow_id for flow in solution.flows]
        failed_flow_id_list: List[FlowId] = solution.failure_flows
        successful_flow_id_list: List[FlowId] = list(set(flow_id_list) - set(failed_flow_id_list))
        successful_flow: List[Flow] = list(filter(lambda flow: flow.flow_id in successful_flow_id_list, solution.flows))
        flow_reliability_list_list: List[List[float]] = [list(rel_dict.values()) for rel_dict in
                                                         [flow.routes_reliability for flow in successful_flow]]
        flow_reliability_list: List[float] = []
        for rel_list in flow_reliability_list_list:
            flow_reliability_list.append(np.mean(rel_list))
        e2e_delay_list: List[int] = []
        for flow in successful_flow:
            e2e_delay_list.append(Analyzer.calculate_e2e_delay(solution.graph, flow))
        # save file
        if target_filename is not None:
            with open(target_filename + '.csv', 'a', newline='') as file:
                writer: csv.writer = csv.writer(file)
                for i, flow in enumerate(successful_flow):
                    logger.info('actual reliability {}%'.format(flow_reliability_list[i]))
                    logger.info('avg. e2e delay {}'.format(e2e_delay_list[i]))
                    line: list = [
                        flow_reliability_list[i],  # actual reliability
                        e2e_delay_list[i],  # end-to-end delay
                    ]
                    writer.writerow(line)

    @staticmethod
    def analyze_flow_size(solution: Solution, target_filename: str = None):
        import numpy as np
        flow_id_list: List[FlowId] = [flow.flow_id for flow in solution.flows]
        edge_list: List[Edge] = list(solution.graph.edge_mapper.values())
        failed_flow_id_list: List[FlowId] = solution.failure_flows
        successful_flow_id_list: List[FlowId] = list(set(flow_id_list) - set(failed_flow_id_list))
        successful_flow: List[Flow] = list(filter(lambda flow: flow.flow_id in successful_flow_id_list, solution.flows))
        bandwidth_list: List[float] = [flow.bandwidth for flow in successful_flow]
        guard_band_list: List[int] = \
            [Analyzer.calculate_guard_band_on_edge(edge.time_slot_allocator) for edge in edge_list]
        guard_band_load_list: List[float] = []
        for i in range(len(edge_list)):
            guard_band_load_list.append(guard_band_list[i] * edge_list[i].time_slot_allocator.time_slot_len /
                                        edge_list[i].time_slot_allocator.time_slot_num)
        load_list: List[float] = [edge.time_slot_allocator.load for edge in edge_list]
        flow_reliability_list_list: List[List[float]] = [list(rel_dict.values()) for rel_dict in
                                                         [flow.routes_reliability for flow in successful_flow]]
        flow_reliability_list: List[float] = []
        for rel_list in flow_reliability_list_list:
            flow_reliability_list += rel_list
        e2e_delay_list: List[int] = []
        for flow in successful_flow:
            e2e_delay_list.append(Analyzer.calculate_e2e_delay(solution.graph, flow))
        flow_num: int = len(flow_id_list)  # number of flows
        edge_num: int = len(edge_list)  # number of edges
        node_num: int = len(solution.graph.nodes)  # number of nodes
        successful_flow_num: int = len(successful_flow_id_list)  # number of successful flows
        ideal_throughput: float = sum(bandwidth_list)  # ideal throughput
        actual_throughput: float = 0.0  # actual throughput
        max_load: float = np.max(load_list)  # maximum load
        min_load: float = np.min(load_list)  # min load
        average_load: float = np.average(load_list)  # averaged load
        median_load: float = np.median(load_list)  # median load
        actual_reliability: float = 0  # actual reliability
        if len(flow_reliability_list) != 0:
            actual_reliability = np.mean(flow_reliability_list)
        e2e_delay: int = 0  # end-to-end delay
        if len(e2e_delay_list) != 0:
            e2e_delay = int(np.mean(e2e_delay_list))
        guard_band: int = 0
        if len(guard_band_list) != 0:
            guard_band = np.sum(guard_band_list) * 64  # total guard band
        runtime: float = '{:.9f}'.format(solution.runtime)
        logging.info('number of flows: {}'.format(flow_num))
        logging.info('number of nodes: {}'.format(node_num))
        logger.info('number of available flows: ' + str(successful_flow_num))
        logger.info('ideal throughput: ' + str(ideal_throughput * 1000) + 'Mbps')
        logger.info('actual throughput: ' + str(actual_throughput * 1000) + 'Mbps')
        logger.info('runtime: {}s'.format(runtime))
        logger.info('maximum load {}%'.format(max_load * 100))
        logger.info('average load {}%'.format(average_load * 100))
        logger.info('median load {}%'.format(median_load * 100))
        logger.info('actual reliability {}%'.format(actual_reliability * 100))
        logger.info('avg. e2e delay {}'.format(e2e_delay))
        logger.info('total guard band {}B'.format(guard_band))
        # save file
        if target_filename is not None:
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
                    median_load,  # median load
                    actual_reliability,  # actual reliability
                    e2e_delay,  # end-to-end delay
                    guard_band,  # total guard band
                ]
                writer.writerow(line)

    @staticmethod
    def analyze_flow_routes_repetition_degree(solution: Solution, target_filename: str = None):
        '''
        analyze repetition degree between the same talker/listener pair
        :param solution:
        :param target_filename:
        :return:
        '''
        # {
        #   flow_id: [
        #       (
        #           src_id,
        #           dest_id,
        #           no_of_e2e_routes,
        #           no_of_repetition_edges,
        #           no_of_repetition_edges/no_of_e2e_routes,
        #           {
        #               edge_id: no_of_repetition, ...
        #           }
        #       ), ...
        #   ]
        # }
        res: Dict[FlowId, List[Tuple[NodeId, NodeId, int, int, float, Dict[EdgeId, int]]]] = {}
        for flow in solution.flows:
            if flow.flow_id in solution.failure_flows:
                continue
            res[flow.flow_id] = []
            o2m_routes: List[List[List[EdgeId]]] = flow.routes
            src_id: NodeId = NodeId(flow.source)
            for o2o_routes in o2m_routes:
                dest_id: NodeId = NodeId(solution.graph.edge_mapper[o2o_routes[0][-1]].out_node.node_id)
                no_of_e2e_routes: int = len(o2o_routes)
                edge_repetition_dict: Dict[EdgeId, int] = dict()
                walked_edges: Set[EdgeId] = set()
                for o2o_route in o2o_routes:
                    for eid in o2o_route:
                        walked_edges.add(eid)
                for eid in walked_edges:
                    edge_repetition_dict[eid] = 0
                for o2o_route in o2o_routes:
                    for eid in o2o_route:
                        edge_repetition_dict[eid] += 1
                no_of_repetition_edges: int = \
                    sum([i for i in edge_repetition_dict.values()]) - len(walked_edges) - (no_of_e2e_routes - 1) * 2
                res[flow.flow_id].append(
                    (
                        src_id,
                        dest_id,
                        no_of_e2e_routes,
                        no_of_repetition_edges,
                        no_of_repetition_edges / no_of_e2e_routes,
                        edge_repetition_dict
                    )
                )
        logger.info('analyze end-to-end routes of flow: {}'.format(res))
        # save result to json
        if target_filename is not None:
            with open(target_filename + '.json', 'w') as file:
                json.dump(res, file)

    @staticmethod
    def analyze_flow_routes_reuse_degree(solution: Solution, target_filename: str = None):
        '''
        analyze repetition degree between different talker/listener pairs
        :param solution:
        :param target_filename:
        :return:
        '''
        pass
