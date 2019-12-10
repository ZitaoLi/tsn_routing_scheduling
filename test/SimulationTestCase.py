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
from src.type import ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY, NodeId
from src.utils.ConfigFileGenerator import ConfigFileGenerator

logging.basicConfig(level=logging.INFO)


class SimulationTestCase(unittest.TestCase):

    def setUp(self):
        edges: List[Tuple[int, int]] = [(1, 2), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5), (3, 8), (5, 6), (5, 7)]
        self.graph: nx.Graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.graph = self.graph.to_directed()
        TopoGenerator.draw(self.graph)

        config.TESTING['generate-flow'] = False  # whether enable flow generation or not
        if config.TESTING['generate-flow']:
            attached_nodes: List[NodeId] = [1, 6, 7, 8]
            config.FLOW_CONFIG['dest-num-set'] = [1, 2, 3]
            config.FLOW_CONFIG['flow-num'] = 5
            self.flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_nodes, graph=self.graph)
            FlowGenerator.save_flows(self.flows)
        else:
            self.flows: List[Flow] = FlowGenerator.load_flows()

        # config.GRAPH_CONFIG['routing_strategy'] = ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY
        config.GRAPH_CONFIG['routing_strategy'] = ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY
        config.GRAPH_CONFIG['scheduling_strategy'] = SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY
        config.GRAPH_CONFIG['allocating_strategy'] = ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY
        solver: Solver = Solver(nx_graph=self.graph,
                                flows=self.flows,
                                topo_strategy=None,
                                routing_strategy=config.GRAPH_CONFIG['routing_strategy'],
                                scheduling_strategy=config.GRAPH_CONFIG['scheduling_strategy'],
                                allocating_strategy=config.GRAPH_CONFIG['allocating_strategy'])
        self.solution = solver.generate_init_solution()
        solver.draw_gantt_chart(self.solution)  # draw gantt chart
        solution_name: str = solver.generate_solution_name(solution=self.solution)
        import os
        filename: str = os.path.join(config.res_dir, solution_name)
        solver.analyze(solution=self.solution, target_filename=filename)  # analyze solution
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
