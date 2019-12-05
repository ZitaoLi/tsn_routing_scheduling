import logging
import unittest
from typing import List, Tuple

import networkx as nx

from src import config
from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver
from src.graph.TopoGenerator import TopoGenerator
from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.type import NodeId, EdgeId, TOPO_STRATEGY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyTestCase(unittest.TestCase):

    def setUp(self):
        config.FLOW_CONFIG['flow-num'] = 5
        config.GRAPH_CONFIG['all-bandwidth'] = 0.5

    def test(self):
        # generate topology
        topo_generator: TopoGenerator = TopoGenerator()
        topo_generator.topo_strategy = ErdosRenyiStrategy(n=10, m=10)
        graph: nx.Graph = topo_generator.generate_core_topo()
        attached_edge_nodes_num: int = config.GRAPH_CONFIG['edge-node-num']
        attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
        topo_generator.draw(graph)
        # generate flows
        flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_edge_nodes, graph=graph)
        # get solution
        solver: Solver = Solver(nx_graph=graph,
                                flows=flows,
                                topo_strategy=TOPO_STRATEGY.ER_STRATEGY,
                                routing_strategy=config.GRAPH_CONFIG['routing-strategy'],
                                scheduling_strategy=config.GRAPH_CONFIG['scheduling-strategy'],
                                allocating_strategy=config.GRAPH_CONFIG['allocating-strategy'])
        solver.visual = True
        solver.generate_init_solution()


if __name__ == '__main__':
    unittest.main()
