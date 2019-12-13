import copy
import logging
import os
import unittest
from typing import List, Tuple

import networkx as nx

from src import config
from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver
from src.graph.TopoGenerator import TopoGenerator
from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.TopoStrategy import TopoStrategy
from src.graph.topo_strategy.TopoStrategyFactory import TopoStrategyFactory
from src.net_envs.network.TSNNetwork import TSNNetwork
from src.net_envs.network.TSNNetworkFactory import TSNNetworkFactory
from src.type import ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY, NodeId, TOPO_STRATEGY
from src.utils.ConfigFileGenerator import ConfigFileGenerator

logging.basicConfig(level=logging.INFO)


class SimulationTestCase3(unittest.TestCase):

    def setUp(self):
        config.TESTING['round'] = [1, 5]  # [1, 5]
        config.TESTING['flow-size'] = [10, 100]
        config.TESTING['x-axis-gap'] = 5
        config.TESTING['draw-gantt-chart'] = False
        config.OPTIMIZATION['enable'] = True
        config.GRAPH_CONFIG['all-bandwidth'] = 0.5  # 500Mbps
        config.GRAPH_CONFIG['core-node-num'] = 10
        config.GRAPH_CONFIG['edge-node-num'] = 10
        config.GRAPH_CONFIG['topo-strategy'] = [
            {
                'strategy': TOPO_STRATEGY.ER_STRATEGY,
                'type': ErdosRenyiStrategy.ER_TYPE.GNP,
                'n': 10,
                'm': 14,
                'p': 0.2,
            },
            {
                'strategy': TOPO_STRATEGY.BA_STRATEGY,
                'n': 10,
                'm': 2,
            },
            {
                'strategy': TOPO_STRATEGY.RRG_STRATEGY,
                'd': 3,
                'n': 10,
            },
            {
                'strategy': TOPO_STRATEGY.WS_STRATEGY,
                'n': 10,
                'k': 4,
                'p': 1.0,
            },
        ]
        self.topo_generator = TopoGenerator()
        self.tsn_network_factory = TSNNetworkFactory()

    def test_simulation(self):
        for test_round in range(config.TESTING['round'][0], config.TESTING['round'][1] + 1):
            for topo_strategy_entity in config.GRAPH_CONFIG['topo-strategy']:
                topo_strategy: TopoStrategy = TopoStrategyFactory.get_instance(**topo_strategy_entity)
                self.topo_generator.topo_strategy = topo_strategy
                graph: nx.Graph = self.topo_generator.generate_core_topo()
                attached_edge_nodes_num: int = config.GRAPH_CONFIG['edge-node-num']
                attached_edge_nodes: List[NodeId] = self.topo_generator.attach_edge_nodes(graph,
                                                                                          attached_edge_nodes_num)
                self.topo_generator.draw(graph)
                # generate flows
                flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_edge_nodes,
                                                                 graph=graph,
                                                                 flow_num=config.TESTING['flow-size'][1])
                for i in range(config.TESTING['flow-size'][0],
                               config.TESTING['flow-size'][1] + 1,
                               config.TESTING['x-axis-gap']):
                    # create solver
                    solver: Solver = Solver(nx_graph=graph,
                                            flows=None,
                                            topo_strategy=topo_strategy_entity['strategy'],
                                            routing_strategy=config.GRAPH_CONFIG['routing-strategy'],
                                            scheduling_strategy=config.GRAPH_CONFIG['scheduling-strategy'],
                                            allocating_strategy=config.GRAPH_CONFIG['allocating-strategy'])
                    solver.add_flows(copy.deepcopy(flows[:i]))
                    # origin method
                    self.solution = solver.generate_init_solution()  # get initial solution
                    solution_name: str = solver.generate_solution_name(
                        solution=self.solution,
                        prefix='b_fz_t{}_n{}_'.format(test_round, len(self.solution.graph.nodes)))
                    filename: str = os.path.join(config.flow_size_res_dir, self.solution.solution_name)
                    solver.analyze(solution=self.solution, target_filename=filename)  # analyze solution
                    self.solution.solution_name = self.generate_solution_filename(
                        anchor='n{}_'.format(len(self.solution.graph.nodes)),
                        addition='f{}_'.format(i))
                    solver.save_solution(filename=self.solution.solution_name)
                    self.generate_test_scenario()  # generate test scenario
                    # optimized method
                    if config.OPTIMIZATION['enable'] is True:
                        self.solution = solver.optimize()  # optimize
                        solution_name: str = solver.generate_solution_name(
                            solution=self.solution,
                            prefix='o_fz_t{}_n{}_'.format(test_round, len(self.solution.graph.nodes)))
                        filename: str = os.path.join(config.flow_size_res_dir, self.solution.solution_name)
                        solver.analyze(solution=self.solution, target_filename=filename)
                        self.solution.solution_name = self.generate_solution_filename(
                            anchor='n{}_'.format(len(self.solution.graph.nodes)),
                            addition='f{}_'.format(i))
                        solver.save_solution(filename=self.solution.solution_name)
                        self.generate_test_scenario()  # generate test scenario

    def generate_solution_filename(self, anchor: str, addition: str):
        tl: List[str] = list(self.solution.solution_name)
        ti: int = self.solution.solution_name.index(anchor)
        [tl.insert(i + ti, c) for i, c in enumerate(list(addition))]
        return ''.join(tl)

    def generate_test_scenario(self):
        # create tsn network
        tsn_network: TSNNetwork = self.tsn_network_factory.product(
            solution_filename=self.solution.solution_name,
            enhancement_enable=config.XML_CONFIG['enhancement-tsn-switch-enable'])
        self.tsn_network = tsn_network
        self.node_edge_mac_info = self.tsn_network_factory.node_edge_mac_info
        # generate configuration file
        ConfigFileGenerator.create_test_scenario(tsn_network=self.tsn_network,
                                                 solution=self.solution,
                                                 node_edge_mac_info=self.node_edge_mac_info)


if __name__ == '__main__':
    unittest.main()
