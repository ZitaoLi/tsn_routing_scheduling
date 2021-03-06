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
        config.TESTING['draw-gantt-chart'] = True
        config.OPTIMIZATION['enable'] = True
        config.FLOW_CONFIG['redundancy_degree'] = 2  # at least 2 end-to-end routes
        config.FLOW_CONFIG['max-redundancy-degree'] = 5  # the most no. of end-to-end routes
        config.FLOW_CONFIG['un-neighbors_degree'] = 1  # avoid source and node connecting at the same node
        config.GRAPH_CONFIG['time-granularity'] = TIME_GRANULARITY.NS
        config.GRAPH_CONFIG['all-bandwidth'] = 0.1  # 100Mbps
        config.GRAPH_CONFIG['all-propagation-delay'] = 0  # 1e2 100ns
        config.GRAPH_CONFIG['all-process-delay'] = 0  # 5e3 5us
        config.GRAPH_CONFIG['all-per'] = 0.01  # 0.4%
        config.GRAPH_CONFIG['edge-nodes-distribution-degree'] = 3

        # create flows
        self.flows: List[Flow] = [
            Flow(1, int(1e3), int(1e6), 5, [7, 8], 0.5, int(2e7)),  # 125B 1000us 20ms
            Flow(2, int(1e3), int(1e6), 6, [5], 0.5, int(2e7)),  # 125B 1000us 20ms
            Flow(3, int(1e3), int(1e6), 7, [5, 6], 0.5, int(2e7)),  # 125B 1000us 20ms
            Flow(4, int(1.6e3), int(1e6), 8, [5], 0.5, int(5e7)),  # 200B 1000us 50ms
            Flow(5, int(2.4e3), int(1e6), 6, [7, 8], 0.5, int(5e7)),  # 300B 1000us 50ms
            Flow(6, int(2.4e3), int(1.5e6), 7, [5, 6], 0.5, int(5e7)),  # 300B 1500us 50ms
            Flow(7, int(5e3), int(1.5e6), 5, [8], 0.5, int(1e8)),  # 625B 1500us 100ms
            Flow(8, int(5e3), int(1.5e6), 6, [8], 0.5, int(1e8)),  # 625B 1500us 100ms
            Flow(9, int(1.2e3), int(3e6), 8, [5, 6], 0.5, int(1e8)),  # 150B 3000us 100ms
            Flow(10, int(1.2e3), int(3e6), 8, [5], 0.5, int(1e8)),  # 150B 3000us 100ms
        ]
        # create topology
        edges: List[Tuple[int, int]] = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (5, 1), (6, 2), (4, 7), (4, 8)]
        self.graph: nx.Graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.graph = self.graph.to_directed()
        TopoGenerator.draw(self.graph)

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
            solution.generate_solution_name(prefix='b_fixed_f{}_n{}_'.format(10, 8))
            Analyzer.analyze_per_flow(
                solution,
                target_filename=os.path.join(config.solutions_res_dir, solution.solution_name))
            solver.save_solution(solution=solution)  # save solution
            tsn_network_factory: TSNNetworkFactory = TSNNetworkFactory()
            tsn_network: TSNNetwork = tsn_network_factory.product(
                solution_filename=solution.solution_name,
                enhancement_enable=config.XML_CONFIG['enhancement-tsn-switch-enable'])
            node_edge_mac_info = tsn_network_factory.node_edge_mac_info
            # create test scenario
            ConfigFileGenerator.create_test_scenario(tsn_network=tsn_network,
                                                     solution=solution,
                                                     node_edge_mac_info=node_edge_mac_info)

            if config.TESTING['draw-gantt-chart'] is True:
                solver.draw_gantt_chart(solution)
            logger.info('Native Objective: ' + str(solver.objective_function(solution)))

            # optimization method
            if config.OPTIMIZATION['enable'] is False or \
                    combination['allocating_strategy'] == ALLOCATING_STRATEGY.AEAPBF_ALLOCATING_STRATEGY or \
                    combination['allocating_strategy'] == ALLOCATING_STRATEGY.AEAPWF_ALLOCATING_STRATEGY or \
                    combination['routing_strategy'] == ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY:
                continue

            solution = solver.optimize()  # optimize
            solution.generate_solution_name(prefix='o_fixed_f{}_n{}_'.format(10, 8))
            Analyzer.analyze_per_flow(
                solution,
                target_filename=os.path.join(config.solutions_res_dir, solution.solution_name))

            if config.TESTING['draw-gantt-chart'] is True:
                solver.draw_gantt_chart(solution)
            logger.info('Optimal Objective: ' + str(solver.objective_function(solution)))

            # create network
            solver.save_solution(solution=solution)  # save solution
            tsn_network = tsn_network_factory.product(
                solution_filename=solution.solution_name,
                enhancement_enable=config.XML_CONFIG['enhancement-tsn-switch-enable'])
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
