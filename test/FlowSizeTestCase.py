import logging
import unittest
from enum import Enum
from typing import List, Tuple

import networkx as nx

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver, Solution
from src.graph.TopoGenerator import TopoGenerator
from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.TopoStrategy import TopoStrategy
from src.graph.topo_strategy.TopoStrategyFactory import TopoStrategyFactory
from src.type import NodeId, EdgeId, FlowId
import src.config as config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlowSizeTestCase(unittest.TestCase):

    def setUp(self):
        # import os
        # filename: str = str(config.GRAPH_CONFIG['routing-strategy']) + '-' + \
        #                 str(config.GRAPH_CONFIG['scheduling-strategy']) + '-' + \
        #                 str(config.GRAPH_CONFIG['allocating-strategy'])
        # filename = filename.replace('.', '_').replace('STRATEGY_', '').replace('_STRATEGY', '') \
        #     .replace('TOPO_', '').replace('ROUTING_', '').replace('SCHEDULING_', '').replace('ALLOCATING_', '')
        # filename = os.path.join(config.flow_size_res_dir, filename)
        # if os.path.exists(filename):
        #     os.removedirs(filename)
        # os.makedirs(filename)
        # self.test_dir = filename
        for topo_strategy_entity in config.GRAPH_CONFIG['topo-strategy']:
            self.core_node_num = topo_strategy_entity['n'] = config.GRAPH_CONFIG['core-node-num']

    def tearDown(self):
        pass

    def test_flow_size(self):
        topo_generator: TopoGenerator = TopoGenerator()
        for topo_strategy_entity in config.GRAPH_CONFIG['topo-strategy']:
            topo_strategy: TopoStrategy = TopoStrategyFactory.get_instance(**topo_strategy_entity)
            topo_generator.topo_strategy = topo_strategy
            for test_round in range(config.TESTING['round']):
                self.round = test_round
                # generate topology
                graph: nx.Graph = topo_generator.generate_core_topo()
                attached_edge_nodes_num: int = config.GRAPH_CONFIG['edge-node-num']
                attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
                topo_generator.draw(graph)
                flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_edge_nodes)
                for i in range(config.TESTING['flow-start'], len(flows)):
                    solver: Solver = Solver(nx_graph=graph,
                                            flows=None,
                                            topo_strategy=topo_strategy_entity['strategy'],
                                            routing_strategy=config.GRAPH_CONFIG['routing-strategy'],
                                            scheduling_strategy=config.GRAPH_CONFIG['scheduling-strategy'],
                                            allocating_strategy=config.GRAPH_CONFIG['allocating-strategy'])
                    solver.visual = config.GRAPH_CONFIG['visible']
                    solver.add_flows(flows[:i + 1])
                    import time
                    # origin method
                    start_time: time.process_time = time.perf_counter()
                    solver.generate_init_solution()  # get initial solution
                    middle_time: time.process_time = time.perf_counter()
                    self.runtime = middle_time - start_time  # basic method time
                    self.analyze(solver.final_solution, prefix='B-')
                    if config.OPTIMIZATION['enable'] is True:
                        # optimized method
                        solver.optimize()  # optimize
                        end_time: time.process_time = time.perf_counter()
                        self.runtime = end_time - start_time  # whole method time with optimized method
                        self.analyze(solver.final_solution, prefix='O-')

    def save_solution(self, solution: Solution):
        # TODO save solution
        import os
        import pickle
        file = os.path.join(os.path.join(config.src_dir, 'json'), 'solution')
        with open(file, 'wb') as f:
            pickle.dump(solution, f)

    def analyze(self, solution: Solution, prefix=''):
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
        import os.path as path
        import csv
        filename: str = str(solution.topo_strategy) + '-' + \
                        str(solution.routing_strategy) + '-' + \
                        str(solution.scheduling_strategy) + '-' + \
                        str(solution.allocating_strategy)
        filename = filename.replace('.', '_').replace('STRATEGY_', '').replace('_STRATEGY', '') \
            .replace('TOPO_', '').replace('ROUTING_', '').replace('SCHEDULING_', '').replace('ALLOCATING_', '')
        prefix += 'T{}-N{}-'.format(self.round, node_num)
        filename = path.join(config.flow_size_res_dir, prefix + filename + '.csv')
        with open(filename, 'a', newline='') as file:
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


if __name__ == '__main__':
    unittest.main()
