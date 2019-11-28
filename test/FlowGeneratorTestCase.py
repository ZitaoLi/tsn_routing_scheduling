import logging
import unittest
from typing import List

import networkx as nx

from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlowGeneratorTestCase(unittest.TestCase):

    def test_generate_flow(self):
        import src.config as cf
        cf.FLOW_CONFIG = {
            'flow-num': 5,
            'dest-num-set': [1, 2, 3],
            'period-set': [int(1e5), int(2e5), int(5e5), int(1e6)],
            'size-set': [int(2e4), int(1e5), int(5e4)],
            'reliability-set': [0.97, 0.98, 0.99],
            'deadline-set': [int(1e8), int(5e7), int(2e7)]
        }
        flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=[1, 2, 3, 4])
        for flow in flows:
            logger.info(flow)


if __name__ == '__main__':
    unittest.main()
