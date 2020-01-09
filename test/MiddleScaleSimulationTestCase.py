import logging
import os
import unittest
from typing import List, Tuple

import networkx as nx

from src import config
from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver
from src.graph.TopoGenerator import TopoGenerator
from src.net_envs.network.TSNNetwork import TSNNetwork
from src.net_envs.network.TSNNetworkFactory import TSNNetworkFactory
from src.type import ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY, NodeId, RELIABILITY_STRATEGY, \
    TIME_GRANULARITY
from src.utils.ConfigFileGenerator import ConfigFileGenerator

logging.basicConfig(level=logging.INFO)


class SimulationTestCase2(unittest.TestCase):

    def setUp(self):
        # configuration
        config.FLOW_CONFIG['size-set'] = [int(1.5e3), int(5e3), int(1e3)]  # [200B, 625B, 125B]
        config.FLOW_CONFIG['period-set'] = [int(1e5), int(1.5e5), int(3e5)]  # [100us, 150us, 300us]
        config.FLOW_CONFIG['hyper-period'] = int(3e5)  # [300us]
        config.FLOW_CONFIG['deadline-set'] = [int(1e8), int(5e7), int(2e7)]  # [100ms, 50ms, 20ms]
        config.FLOW_CONFIG['redundancy_degree'] = 3
        config.FLOW_CONFIG['reliability-set'] = [0.5]
        config.FLOW_CONFIG['dest-num-set'] = [1, 2, 3]
        config.FLOW_CONFIG['max-hops'] = 8
        config.FLOW_CONFIG['flow-num'] = 10
        config.GRAPH_CONFIG['time-granularity'] = TIME_GRANULARITY.NS
        config.GRAPH_CONFIG['all-bandwidth'] = 1e0  # 500Mbps
        config.GRAPH_CONFIG['all-propagation-delay'] = 1e2
        config.GRAPH_CONFIG['all-process-delay'] = 5e3
        config.GRAPH_CONFIG['all-per'] = 0.004  # 0.4%
        config.XML_CONFIG['enhancement-tsn-switch-enable'] = True

        # create graph
        edges: List[Tuple[int, int]] = [(1, 5), (2, 6), (3, 8), (4, 11), (5, 6), (5, 9),
                                        (6, 7), (7, 9), (7, 8), (8, 9), (8, 11), (9, 10), (10, 11)]
        self.graph: nx.Graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.graph = self.graph.to_directed()
        TopoGenerator.draw(self.graph)



    def run_test(self, combinations: List = None):
        for combination in combinations:
            # create flows
            if combination['enable_flow_gen']:
                attached_nodes: List[NodeId] = [1, 2, 3, 4]
                self.flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_nodes, graph=self.graph)
                FlowGenerator.save_flows(self.flows)
            else:
                self.flows: List[Flow] = FlowGenerator.load_flows()
            # origin method
            solver: Solver = Solver(nx_graph=self.graph,
                                    flows=self.flows[:],
                                    topo_strategy=None,
                                    routing_strategy=combination['routing_strategy'],
                                    scheduling_strategy=combination['scheduling_strategy'],
                                    allocating_strategy=combination['allocating_strategy'],
                                    reliability_strategy=combination['reliability_strategy'])
            self.solution = solver.generate_init_solution()
            solver.draw_gantt_chart(self.solution)  # draw gantt chart
            solution_name: str = self.solution.generate_solution_name(prefix='b_n7_f10_')

            if combination['enable_op']:
                # optimized method
                self.solution = solver.optimize()  # optimize
                solver.draw_gantt_chart(self.solution)  # draw gantt chart
                solution_name: str = self.solution.generate_solution_name(prefix='o_n7_f10_')
            solver.save_solution(solution=self.solution)  # save solution
            # create network
            tsn_network_factory: TSNNetworkFactory = TSNNetworkFactory()
            tsn_network: TSNNetwork = tsn_network_factory.product(
                solution_filename=solution_name,
                enhancement_enable=config.XML_CONFIG['enhancement-tsn-switch-enable'])
            self.tsn_network = tsn_network
            self.node_edge_mac_info = tsn_network_factory.node_edge_mac_info
            # create test scenario
            ConfigFileGenerator.create_test_scenario(tsn_network=self.tsn_network,
                                                     solution=self.solution,
                                                     node_edge_mac_info=self.node_edge_mac_info)

    def test(self):
        self.run_test([
            {
                'routing_strategy': ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY,
                'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                'allocating_strategy': ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY,
                'reliability_strategy': RELIABILITY_STRATEGY.ENUMERATION_METHOD_RELIABILITY_STRATEGY,
                'enable_flow_gen': True,
                'enable_op': False
            },
            {
                'routing_strategy': ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY,
                'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                'allocating_strategy': ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY,
                'reliability_strategy': RELIABILITY_STRATEGY.ENUMERATION_METHOD_RELIABILITY_STRATEGY,
                'enable_flow_gen': False,
                'enable_op': True
            },
            {
                'routing_strategy': ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY,
                'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                'allocating_strategy': ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY,
                'reliability_strategy': RELIABILITY_STRATEGY.UNI_ROUTES_RELIABILITY_STRATEGY,
                'enable_flow_gen': False,
                'enable_op': False
            }
        ])


    def test_simulation(self):
        ConfigFileGenerator.create_test_scenario(tsn_network=self.tsn_network,
                                                 solution=self.solution,
                                                 node_edge_mac_info=self.node_edge_mac_info)


if __name__ == '__main__':
    unittest.main()
