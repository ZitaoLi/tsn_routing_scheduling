import logging
import unittest
from typing import List

import networkx as nx

from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.TopoGenerator import TopoGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlowGeneratorTestCase(unittest.TestCase):

    def test_generate_flow(self):
        import src.config as cf
        cf.FLOW_CONFIG = {
            'flow-num': 5,
            'dest-num-set': [1, 2, 3],
            'period-set': [int(1e6), int(2e6), int(5e5), int(1e7)],
            'size-set': [int(2e4), int(1e5), int(5e4)],
            'reliability-set': [0.97, 0.98, 0.99],
            'deadline-set': [int(1e8), int(5e7), int(2e7)]
        }
        graph: nx.Graph = nx.Graph()
        graph.add_edges_from([(1, 2), (2, 3), (2, 4), (4, 5), (4, 6), (7, 1), (8, 1), (9, 6), (10, 5)])
        TopoGenerator.draw(graph)
        flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=[3, 7, 8, 9, 10], graph=graph)
        for flow in flows:
            logger.info(flow)


if __name__ == '__main__':
    unittest.main()
