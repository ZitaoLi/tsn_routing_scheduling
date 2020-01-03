import logging
import os
import unittest
from typing import List, Tuple

import networkx as nx

from src import config
from src.graph.Analyzer import Analyzer
from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver
from src.graph.TopoGenerator import TopoGenerator
from src.net_envs.network.TSNNetwork import TSNNetwork
from src.net_envs.network.TSNNetworkFactory import TSNNetworkFactory
from src.type import ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY, NodeId, RELIABILITY_STRATEGY
from src.utils.ConfigFileGenerator import ConfigFileGenerator

logging.basicConfig(level=logging.INFO)


class ReliabilityStrategyTestCase(unittest.TestCase):

    def setUp(self):
        edges: List[Tuple[int, int]] = [(1, 5), (2, 6), (3, 8), (4, 11), (5, 6), (5, 9),
                                        (6, 7), (7, 9), (7, 8), (8, 9), (8, 11), (9, 10), (10, 11)]
        # edges: List[Tuple[int, int]] = [(1, 2), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5), (3, 8), (5, 6), (5, 7)]
        self.graph: nx.Graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.graph = self.graph.to_directed()
        TopoGenerator.draw(self.graph)

        # fid = 1, size = 1500KB, period = 300us, source = 1, destinations = [6, 7], reliability = 0.95, deadline = 300us
        f1: Flow = Flow(1, int(1.2e4), int(3e5), 1, [3, 4], 0.95, int(1e6))
        # f1: Flow = Flow(1, int(1.2e4), int(3e5), 1, [6, 7], 0.95, int(1e6))
        self.flows: List[Flow] = [f1]

        config.FLOW_CONFIG['redundancy_degree'] = 4
        config.GRAPH_CONFIG['all-per'] = 0.01
        config.GRAPH_CONFIG['routing_strategy'] = ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY
        config.GRAPH_CONFIG['scheduling_strategy'] = SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY
        config.GRAPH_CONFIG['allocating_strategy'] = ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY
        config.GRAPH_CONFIG['reliability-strategy'] = RELIABILITY_STRATEGY.ENUMERATION_METHOD_RELIABILITY_STRATEGY

    def test_reliability_strategy(self):
        solver: Solver = Solver(nx_graph=self.graph,
                                flows=self.flows,
                                topo_strategy=None,
                                routing_strategy=config.GRAPH_CONFIG['routing_strategy'],
                                scheduling_strategy=config.GRAPH_CONFIG['scheduling_strategy'],
                                allocating_strategy=config.GRAPH_CONFIG['allocating_strategy'],
                                reliability_strategy=config.GRAPH_CONFIG['reliability-strategy'])
        self.solution = solver.generate_init_solution()
        solver.draw_gantt_chart(self.solution)  # draw gantt chart
        target_filename: str = os.path.join(config.flow_routes_repetition_degree_dir, self.solution.solution_name)
        Analyzer.analyze_flow_routes_repetition_degree(self.solution, target_filename=target_filename)


if __name__ == '__main__':
    unittest.main()
