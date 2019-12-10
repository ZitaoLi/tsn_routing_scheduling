import copy
import unittest
from typing import List, Tuple

import networkx as nx

from src import config
from src.graph.Flow import Flow
from src.graph.Graph import Graph
from src.graph.Solver import Solver
from src.graph.TopoGenerator import TopoGenerator
from src.graph.routing_strategy.RoutingStrategyFactory import RoutingStrategyFactory
from src.type import ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY


class RoutingTestCase(unittest.TestCase):
    def setUp(self):
        # before test, create graph
        self.nodes: List[int] = [1, 2, 3, 4, 5, 6, 7]

        self.edges: List[Tuple[int]] = [(1, 2), (2, 1), (2, 3), (3, 2), (2, 4), (4, 2), (3, 4), (4, 3), (3, 5), (5, 3),
                                        (4, 5), (5, 4), (5, 6), (6, 5), (5, 7), (7, 5)]

        self.graph: nx.Graph = nx.Graph()
        self.graph.add_edges_from(self.edges)
        self.graph = self.graph.to_directed()
        TopoGenerator.draw(self.graph)

        # fid = 1, size = 8Kb, period = 300us, source = 1, destinations = [6, 7], reliability = 0.0, deadline = 300us
        f1: Flow = Flow(1, int(8e3), int(3e5), 1, [6, 7], 0.0, int(1e6))
        # fid = 1, size = 20Kb, period = 150us, source = 1, destinations = [6], reliability = 0.0, deadline = 150us
        f2: Flow = Flow(2, int(2e4), int(1.5e5), 1, [6], 0.0, int(1e6))
        # fid = 1, size = 30Kb, period = 150us, source = 1, destinations = [6, 7], reliability = 0.0, deadline = 300us
        f3: Flow = Flow(3, int(3e4), int(3e5), 1, [6, 7], 0.0, int(1e6))
        # fid = 1, size = 2Kb, period = 150us, source = 1, destinations = [7], reliability = 0.0, deadline = 300us
        f4: Flow = Flow(4, int(2e3), int(3e5), 1, [7], 0.0, int(1e6))

        self.flows: List[Flow] = list()
        self.flows.append(f1)
        self.flows.append(f2)
        self.flows.append(f3)
        self.flows.append(f4)

    def tearDown(self):
        # after test
        pass

    # def test_something(self):
    #     self.assertEqual(True, False)

    def test_routing_strategy(self):
        solver: Solver = Solver(nx_graph=self.graph,
                                flows=self.flows,
                                topo_strategy=None,
                                routing_strategy=ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY,
                                scheduling_strategy=SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                                allocating_strategy=ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY)
        solver.visual = True
        self.solution = solver.generate_init_solution()


if __name__ == '__main__':
    unittest.main()
