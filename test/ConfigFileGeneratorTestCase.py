import logging
import unittest
from typing import List, Dict

import networkx as nx

from src import config
from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver, Solution
from src.graph.TopoGenerator import TopoGenerator
from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.TopoStrategy import TopoStrategy
from src.graph.topo_strategy.TopoStrategyFactory import TopoStrategyFactory
from src.net_envs.network.TSNNetwork import TSNNetwork
from src.net_envs.network.TSNNetworkFactory import TSNNetworkFactory
from src.type import NodeId, TOPO_STRATEGY, ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY
from src.utils.ConfigFileGenerator import ConfigFileGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigFileGeneratorTestCase(unittest.TestCase):

    def setUp(self):
        topo_generator: TopoGenerator = TopoGenerator()
        topo_strategy_entity: Dict = {
            'strategy': TOPO_STRATEGY.BA_STRATEGY,
            'n': 5,
            'm': 2,
        }
        config.GRAPH_CONFIG['edge-nodes-distribution-degree'] = 2
        config.FLOW_CONFIG['dest-num-set'] = [1, 2]
        config.FLOW_CONFIG['flow-num'] = 3
        topo_generator.topo_strategy = TopoStrategyFactory.get_instance(**topo_strategy_entity)
        graph: nx.Graph = topo_generator.generate_core_topo()
        attached_edge_nodes_num: int = 3
        attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
        topo_generator.draw(graph)
        config.TESTING['generate-flow'] = False
        if config.TESTING['generate-flow']:
            flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_edge_nodes, graph=graph)
            FlowGenerator.save_flows(flows)
        else:
            flows: List[Flow] = FlowGenerator.load_flows()
        solver: Solver = Solver(nx_graph=graph,
                                flows=flows,
                                topo_strategy=topo_strategy_entity['strategy'],
                                routing_strategy=ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY,
                                scheduling_strategy=SCHEDULING_STRATEGY.LRF_RRDUNDANT_SCHEDULING_STRATEGY,
                                allocating_strategy=ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY)
        solver.visual = True
        solver.generate_init_solution()
        solver.save_solution('solution')
        tsn_network_factory: TSNNetworkFactory = TSNNetworkFactory()
        tsn_network: TSNNetwork = tsn_network_factory.product(
            solution_filename='solution',
            enhancement_enable=config.XML_CONFIG['enhancement-tsn-switch-enable'])
        logger.info(str(tsn_network.__class__) + ': ' + str(tsn_network))
        self.tsn_network = tsn_network

    def test_generate_routes_xml(self):
        ConfigFileGenerator.generate_routes_xml(self.tsn_network)

    def test_generate_switch_schedule_xml(self):
        ConfigFileGenerator.generate_switch_schedule_xml(self.tsn_network)


if __name__ == '__main__':
    unittest.main()
