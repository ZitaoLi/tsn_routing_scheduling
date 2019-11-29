import logging
import unittest
from typing import List, Tuple

import networkx as nx

from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver
from src.graph.TopoGenerator import TopoGenerator
from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.type import NodeId, EdgeId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyTestCase(unittest.TestCase):

    def test(self):
        # generate topology
        topo_generator: TopoGenerator = TopoGenerator()
        topo_generator.topo_strategy = ErdosRenyiStrategy(n=10, m=10)
        graph: nx.Graph = topo_generator.generate_core_topo()
        attached_edge_nodes_num: int = 4
        attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
        topo_generator.draw(graph)
        # generate flows
        flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_edge_nodes)
        # get solution
        nodes: List[NodeId] = list(graph.nodes)
        edges: List[Tuple[EdgeId]] = list(graph.edges)
        Solver.generate_init_solution(nodes, edges, flows)


if __name__ == '__main__':
    unittest.main()
