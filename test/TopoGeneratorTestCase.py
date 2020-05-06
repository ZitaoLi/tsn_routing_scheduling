import logging
import unittest
from typing import List, Tuple

import networkx as nx

from src import config
from src.graph.TopoGenerator import TopoGenerator
from src.graph.topo_strategy.BarabasiAlbertStrategy import BarabasiAlbertStrategy
from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.RandomRegularGraphStrategy import RandomRegularGraphStrategy
from src.graph.topo_strategy.WattsStrogatzStrategy import WattsStrogatzStrategy
from src.type import NodeId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TopoGeneratorTestCase(unittest.TestCase):

    def setUp(self):
        config.GRAPH_CONFIG['edge-nodes-distribution-degree'] = 3

    def tearDown(self):
        pass

    # def test_something(self):
    #     self.assertEqual(True, False)

    def test_er_strategy_gnm(self):
        topo_generator: TopoGenerator = TopoGenerator()
        topo_generator.topo_strategy = ErdosRenyiStrategy()
        topo_generator.topo_strategy.n = 10
        topo_generator.topo_strategy.m = 10
        graph: nx.Graph = topo_generator.generate_core_topo()
        attached_edge_nodes_num: int = 4
        attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
        logger.info(attached_edge_nodes)
        topo_generator.draw(graph)

    def test_er_strategy_gnp(self):
        topo_generator: TopoGenerator = TopoGenerator()
        topo_generator.topo_strategy = ErdosRenyiStrategy(t=ErdosRenyiStrategy.ER_TYPE.GNP)
        topo_generator.topo_strategy.n = 20
        topo_generator.topo_strategy.p = 0.2
        graph: nx.Graph = topo_generator.generate_core_topo()
        attached_edge_nodes_num: int = 4
        attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
        logger.info(attached_edge_nodes)
        topo_generator.draw(graph)

    def test_ba_strategy(self):
        topo_generator: TopoGenerator = TopoGenerator()
        topo_generator.topo_strategy = BarabasiAlbertStrategy(20, 2)
        graph: nx.Graph = topo_generator.generate_core_topo()
        attached_edge_nodes_num: int = 4
        attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
        logger.info(attached_edge_nodes)
        topo_generator.draw(graph)

    def test_rrg_strategy(self):
        topo_generator: TopoGenerator = TopoGenerator()
        topo_generator.topo_strategy = RandomRegularGraphStrategy(4, 5)
        graph: nx.Graph = topo_generator.generate_core_topo()
        attached_edge_nodes_num: int = 10
        attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
        logger.info(attached_edge_nodes)
        topo_generator.draw(graph)

    def test_ws_strategy(self):
        topo_generator: TopoGenerator = TopoGenerator()
        topo_generator.topo_strategy = WattsStrogatzStrategy(n=20, k=2, p=1.0)
        graph: nx.Graph = topo_generator.generate_core_topo()
        attached_edge_nodes_num: int = 4
        attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
        logger.info(attached_edge_nodes)
        topo_generator.draw(graph)

    def test_attach_edge_nodes(self):
        graph: nx.Graph = nx.Graph()
        graph.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4), (2, 3)])
        graph = graph.to_directed()
        topo_generator: TopoGenerator = TopoGenerator()
        attached_edge_nodes_num: int = 3
        attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
        logger.info(attached_edge_nodes)
        self.assertEqual(attached_edge_nodes.__len__(), attached_edge_nodes_num)
        topo_generator.draw(graph)

    def test_my_topology(self):
        edges: List[Tuple[int, int]] = [(1, 3), (2, 4), (3, 4), (3.5), (3, 6), (4, 5), (5, 6), (5, 7), (6, 8), (7, 8),
                                        (7, 9), (8, 10), (8, 11)]
        self.graph: nx.Graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.graph = self.graph.to_directed()
        TopoGenerator.draw(self.graph)


if __name__ == '__main__':
    suites: unittest.TestSuite = unittest.TestSuite()
    suites.addTest(TopoGeneratorTestCase("test_er_strategy"))
    suites.addTest(TopoGeneratorTestCase("test_ba_strategy"))
    suites.addTest(TopoGeneratorTestCase("test_attach_edge_nodes"))
    runner = unittest.TextTestRunner()
    runner.run(suites)
    # unittest.main()

