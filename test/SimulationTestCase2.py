import logging
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
from src.type import ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY, NodeId, RELIABILITY_STRATEGY
from src.utils.ConfigFileGenerator import ConfigFileGenerator

logging.basicConfig(level=logging.INFO)


class SimulationTestCase2(unittest.TestCase):

    def setUp(self):
        edges: List[Tuple[int, int]] = [(1, 5), (2, 6), (3, 8), (4, 11), (5, 6), (5, 9),
                                        (6, 7), (7, 9), (7, 8), (8, 9), (8, 11), (9, 10), (10, 11)]
        self.graph: nx.Graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.graph = self.graph.to_directed()
        TopoGenerator.draw(self.graph)

        config.TESTING['generate-flow'] = True  # whether enable flow generation or not
        config.FLOW_CONFIG['reliability-set'] = [0.5]
        config.FLOW_CONFIG['redundancy_degree'] = 2
        if config.TESTING['generate-flow']:
            attached_nodes: List[NodeId] = [1, 2, 3, 4]
            config.FLOW_CONFIG['dest-num-set'] = [1, 2, 3]
            config.FLOW_CONFIG['flow-num'] = 10
            self.flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_nodes, graph=self.graph)
            FlowGenerator.save_flows(self.flows)
        else:
            self.flows: List[Flow] = FlowGenerator.load_flows()

        config.FLOW_CONFIG['redundancy_degree'] = 5
        config.GRAPH_CONFIG['routing_strategy'] = ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY
        # config.GRAPH_CONFIG['routing_strategy'] = ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY
        config.GRAPH_CONFIG['scheduling_strategy'] = SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY
        config.GRAPH_CONFIG['allocating_strategy'] = ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY
        config.GRAPH_CONFIG['reliability-strategy'] = RELIABILITY_STRATEGY.ENUMERATION_METHOD_RELIABILITY_STRATEGY
        solver: Solver = Solver(nx_graph=self.graph,
                                flows=self.flows,
                                topo_strategy=None,
                                routing_strategy=config.GRAPH_CONFIG['routing_strategy'],
                                scheduling_strategy=config.GRAPH_CONFIG['scheduling_strategy'],
                                allocating_strategy=config.GRAPH_CONFIG['allocating_strategy'],
                                reliability_strategy=config.GRAPH_CONFIG['reliability-strategy'])
        self.solution = solver.generate_init_solution()
        solver.draw_gantt_chart(self.solution)  # draw gantt chart
        solution_name: str = solver.generate_solution_name(solution=self.solution, prefix='n7_f10_r6_')
        import os
        filename: str = os.path.join(config.res_dir, solution_name)
        solver.analyze(solution=self.solution, target_filename=filename)  # analyze solution
        config.OPTIMIZATION['enable'] = False
        if config.OPTIMIZATION['enable'] is True:
            # optimized method
            self.solution = solver.optimize()  # optimize
            solver.draw_gantt_chart(self.solution)  # draw gantt chart
            solution_name: str = solver.generate_solution_name(
                solution=self.solution,
                prefix='o_n7_f10_r5_')
            filename: str = os.path.join(config.res_dir, solution_name)
            solver.analyze(solution=self.solution, target_filename=filename)
        solver.save_solution(solution=self.solution)  # save solution

        tsn_network_factory: TSNNetworkFactory = TSNNetworkFactory()
        tsn_network: TSNNetwork = tsn_network_factory.product(
            solution_filename=solution_name,
            enhancement_enable=config.XML_CONFIG['enhancement-tsn-switch-enable'])
        self.tsn_network = tsn_network
        self.node_edge_mac_info = tsn_network_factory.node_edge_mac_info

    def test_simulation(self):
        ConfigFileGenerator.create_test_scenario(tsn_network=self.tsn_network,
                                                 solution=self.solution,
                                                 node_edge_mac_info=self.node_edge_mac_info)


if __name__ == '__main__':
    unittest.main()
