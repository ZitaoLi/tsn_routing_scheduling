import logging
import os
import unittest
from enum import Enum
from typing import List, Tuple, Dict

import networkx as nx

from src.graph.Analyzer import Analyzer
from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver, Solution
from src.graph.TopoGenerator import TopoGenerator
from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.TopoStrategy import TopoStrategy
from src.graph.topo_strategy.TopoStrategyFactory import TopoStrategyFactory
from src.net_envs.network.TSNNetwork import TSNNetwork
from src.net_envs.network.TSNNetworkFactory import TSNNetworkFactory
from src.type import NodeId, EdgeId, FlowId, TOPO_STRATEGY, ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY, \
    RELIABILITY_STRATEGY, TIME_GRANULARITY
import src.config as config
from src.utils.ConfigFileGenerator import ConfigFileGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# logging.disable(logging.INFO)


class FixedSimulationTestCase(unittest.TestCase):

    def setUp(self):
        config.TESTING['round'] = [1, 1]  # [1, 5]
        config.TESTING['flow-size'] = [10, 100]
        config.TESTING['x-axis-gap'] = 5
        config.TESTING['draw-gantt-chart'] = False
        config.OPTIMIZATION['enable'] = False
        config.FLOW_CONFIG['redundancy_degree'] = 2  # at least 2 end-to-end routes
        config.FLOW_CONFIG['max-redundancy-degree'] = 5  # the most no. of end-to-end routes
        config.FLOW_CONFIG['un-neighbors_degree'] = 1  # avoid source and node connecting at the same node
        config.FLOW_CONFIG['size-set'] = [int(1.6e3), int(5e3), int(1e3)]  # [200B, 625B, 125B]
        config.FLOW_CONFIG['period-set'] = [int(1e5), int(1.5e5), int(3e5)]  # [100us, 150us, 300us]
        config.FLOW_CONFIG['hyper-period'] = int(3e5)  # [300us]
        config.FLOW_CONFIG['deadline-set'] = [int(1e8), int(5e7), int(2e7)]  # [100ms, 50ms, 20ms]
        config.FLOW_CONFIG['reliability-set'] = [0.5]  # [0.98]
        config.GRAPH_CONFIG['time-granularity'] = TIME_GRANULARITY.NS
        config.GRAPH_CONFIG['all-bandwidth'] = 1  # 500Mbps
        config.GRAPH_CONFIG['all-propagation-delay'] = 0  # 1e2 100ns
        config.GRAPH_CONFIG['all-process-delay'] = 0  # 5e3 5us
        config.GRAPH_CONFIG['all-per'] = 0.004  # 0.4%
        config.GRAPH_CONFIG['core-node-num'] = 10
        config.GRAPH_CONFIG['edge-node-num'] = 10
        config.GRAPH_CONFIG['edge-nodes-distribution-degree'] = 6

        # create flows
        self.flows: List[Flow] = [
            Flow(1, int(1e3), int(1e5), 1, [9, 10], 0.5, int(1e8)),
            Flow(2, int(1e3), int(1e5), 2, [9, 10], 0.5, int(1e8)),
            Flow(3, int(1e3), int(1e5), 9, [1, 2], 0.5, int(1e8)),
            Flow(4, int(1e3), int(1e5), 9, [10, 11], 0.5, int(1e8)),
            Flow(5, int(1e3), int(1e5), 10, [2], 0.5, int(1e8))
        ]
        # create topology
        edges: List[Tuple[int, int]] = [(1, 3), (2, 4), (3, 4), (3, 5), (3, 6), (4, 5), (5, 6), (5, 7), (6, 8), (7, 8),
                                        (7, 9), (8, 10), (8, 11)]
        self.graph: nx.Graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.graph = self.graph.to_directed()
        TopoGenerator.draw(self.graph)

    def tearDown(self):
        pass

    def run_test(self, combinations: List = None):
        for combination in combinations:
            # origin method
            solver: Solver = Solver(nx_graph=self.graph,
                                    flows=self.flows[:],
                                    topo_strategy=None,
                                    routing_strategy=combination['routing_strategy'],
                                    scheduling_strategy=combination['scheduling_strategy'],
                                    allocating_strategy=combination['allocating_strategy'],
                                    reliability_strategy=combination['reliability_strategy'])
            solution = solver.generate_init_solution()
            solution.generate_solution_name(prefix='b_fixed_f{}_n{}_'.format(10, 10))
            Analyzer.analyze_per_flow(
                solution,
                target_filename=os.path.join(config.solutions_res_dir, solution.solution_name))
            if config.TESTING['draw-gantt-chart'] is True:
                solver.draw_gantt_chart(solution)
            logger.info('Native Objective: ' + str(solver.objective_function(solution)))
            # optimization method
            solution = solver.optimize()  # optimize
            solution.generate_solution_name(prefix='o_fixed_f{}_n{}_'.format(10, 10))
            Analyzer.analyze_per_flow(
                solution,
                target_filename=os.path.join(config.solutions_res_dir, solution.solution_name))
            if config.TESTING['draw-gantt-chart'] is True:
                solver.draw_gantt_chart(solution)
            logger.info('Optimal Objective: ' + str(solver.objective_function(solution)))
            # create network
            solver.save_solution(solution=solution)  # save solution
            tsn_network_factory: TSNNetworkFactory = TSNNetworkFactory()
            tsn_network: TSNNetwork = tsn_network_factory.product(
                solution_filename=solution.solution_name,
                enhancement_enable=config.XML_CONFIG['enhancement-tsn-switch-enable'])
            tsn_network = tsn_network
            node_edge_mac_info = tsn_network_factory.node_edge_mac_info
            # create test scenario
            ConfigFileGenerator.create_test_scenario(tsn_network=tsn_network,
                                                     solution=solution,
                                                     node_edge_mac_info=node_edge_mac_info)

    def test(self):
        self.run_test([
            {
                'routing_strategy': ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY,
                'reliability_strategy': RELIABILITY_STRATEGY.UNI_ROUTES_RELIABILITY_STRATEGY,
                'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                'allocating_strategy': ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY
            },
            {
                'routing_strategy': ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY,
                'reliability_strategy': RELIABILITY_STRATEGY.UNI_ROUTES_RELIABILITY_STRATEGY,
                'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                'allocating_strategy': ALLOCATING_STRATEGY.AEAPBF_ALLOCATING_STRATEGY
            },
            {
                'routing_strategy': ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY,
                'reliability_strategy': RELIABILITY_STRATEGY.UNI_ROUTES_RELIABILITY_STRATEGY,
                'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                'allocating_strategy': ALLOCATING_STRATEGY.AEAPWF_ALLOCATING_STRATEGY
            },
            {
                'routing_strategy': ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY,
                'reliability_strategy': RELIABILITY_STRATEGY.ENUMERATION_METHOD_RELIABILITY_STRATEGY,
                'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                'allocating_strategy': ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY
            },
            {
                'routing_strategy': ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY,
                'reliability_strategy': RELIABILITY_STRATEGY.ENUMERATION_METHOD_RELIABILITY_STRATEGY,
                'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                'allocating_strategy': ALLOCATING_STRATEGY.AEAPBF_ALLOCATING_STRATEGY
            },
            {
                'routing_strategy': ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY,
                'reliability_strategy': RELIABILITY_STRATEGY.ENUMERATION_METHOD_RELIABILITY_STRATEGY,
                'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                'allocating_strategy': ALLOCATING_STRATEGY.AEAPWF_ALLOCATING_STRATEGY
            },
        ])


if __name__ == '__main__':
    unittest.main()
