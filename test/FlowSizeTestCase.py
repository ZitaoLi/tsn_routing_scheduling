import logging
import unittest
from enum import Enum
from typing import List, Tuple

import networkx as nx

from src.graph.Analyzer import Analyzer
from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.FlowGenerator import FlowGenerator
from src.graph.Solver import Solver, Solution
from src.graph.TopoGenerator import TopoGenerator
from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.TopoStrategy import TopoStrategy
from src.graph.topo_strategy.TopoStrategyFactory import TopoStrategyFactory
from src.type import NodeId, EdgeId, FlowId, TOPO_STRATEGY
import src.config as config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# logging.disable(logging.INFO)


class FlowSizeTestCase(unittest.TestCase):

    def setUp(self):
        config.TESTING['round'] = [1, 1]  # [1, 5]
        config.TESTING['flow-size'] = [10, 20]
        config.TESTING['x-axis-gap'] = 5
        config.TESTING['draw-gantt-chart'] = False
        config.OPTIMIZATION['enable'] = False
        config.FLOW_CONFIG['redundancy_degree'] = 2  # at least 2 end-to-end routes
        config.FLOW_CONFIG['max-redundancy-degree'] = 5  # the most no. of end-to-end routes
        config.FLOW_CONFIG['un-neighbors_degree'] = 1  # avoid source and node connecting at the same node
        config.FLOW_CONFIG['size-set'] = [int(1.5e3), int(5e3), int(1e3)]
        config.FLOW_CONFIG['period-set'] = [int(1e5), int(1.5e5), int(3e5)]
        config.FLOW_CONFIG['hyper-period'] = int(3e5)
        config.FLOW_CONFIG['deadline-set'] = [int(1e8), int(5e7), int(2e7)]
        config.FLOW_CONFIG['reliability-set'] = [0.90, 0.91, 0.92]
        config.GRAPH_CONFIG['all-bandwidth'] = 0.5  # 500Mbps
        config.GRAPH_CONFIG['core-node-num'] = 10
        config.GRAPH_CONFIG['edge-node-num'] = 10
        config.GRAPH_CONFIG['edge-nodes-distribution-degree'] = 6
        config.GRAPH_CONFIG['topo-strategy'] = [
            # {
            #     'strategy': TOPO_STRATEGY.ER_STRATEGY,
            #     'type': ErdosRenyiStrategy.ER_TYPE.GNP,
            #     'n': 10,
            #     'm': 14,
            #     'p': 0.3,
            # },
            # {
            #     'strategy': TOPO_STRATEGY.BA_STRATEGY,
            #     'n': 10,
            #     'm': 2,
            # },
            {
                'strategy': TOPO_STRATEGY.RRG_STRATEGY,
                'd': 3,
                'n': 10,
            },
            # {
            #     'strategy': TOPO_STRATEGY.WS_STRATEGY,
            #     'n': 10,
            #     'k': 4,
            #     'p': 1.0,
            # },
        ]
        for topo_strategy_entity in config.GRAPH_CONFIG['topo-strategy']:
            topo_strategy_entity['n'] = config.GRAPH_CONFIG['core-node-num']

    def tearDown(self):
        pass

    def test_flow_size(self):
        topo_generator: TopoGenerator = TopoGenerator()
        for topo_strategy_entity in config.GRAPH_CONFIG['topo-strategy']:
            topo_strategy: TopoStrategy = TopoStrategyFactory.get_instance(**topo_strategy_entity)
            topo_generator.topo_strategy = topo_strategy
            for test_round in range(config.TESTING['round'][0], config.TESTING['round'][1] + 1):
                self.round = test_round
                # generate topology
                graph: nx.Graph = topo_generator.generate_core_topo()
                attached_edge_nodes_num: int = config.GRAPH_CONFIG['edge-node-num']
                attached_edge_nodes: List[NodeId] = topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
                topo_generator.draw(graph)
                # generate flows
                flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_edge_nodes,
                                                                 graph=graph,
                                                                 flow_num=config.TESTING['flow-size'][1])
                for i in range(config.TESTING['flow-size'][0],
                               config.TESTING['flow-size'][1] + 1,
                               config.TESTING['x-axis-gap']):
                    solver: Solver = Solver(nx_graph=graph,
                                            flows=flows[:i],
                                            topo_strategy=topo_strategy_entity['strategy'],
                                            routing_strategy=config.GRAPH_CONFIG['routing-strategy'],
                                            scheduling_strategy=config.GRAPH_CONFIG['scheduling-strategy'],
                                            allocating_strategy=config.GRAPH_CONFIG['allocating-strategy'],
                                            reliability_strategy=config.GRAPH_CONFIG['reliability-strategy'])
                    try:
                        import time
                        import os
                        # origin method
                        self.solution = solver.generate_init_solution()  # get initial solution
                        self.solution.generate_solution_name(
                            prefix='b_fz_t{}_n{}_'.format(test_round, len(self.solution.graph.nodes)))
                        solver.save_solution()
                        Analyzer.analyze_flow_size(
                            self.solution,
                            target_filename=os.path.join(config.flow_size_res_dir, self.solution.solution_name))
                        self.solution.generate_solution_name(
                            prefix='b_fz_t{}_n{}_f{}_'.format(test_round, len(self.solution.graph.nodes), i))
                        Analyzer.analyze_flow_routes_repetition_degree(
                            self.solution,
                            target_filename=os.path.join(config.flow_routes_repetition_degree_dir,
                                                         self.solution.solution_name))
                        if config.OPTIMIZATION['enable'] is True:
                            # optimized method
                            self.solution = solver.optimize()  # optimize
                            self.solution.generate_solution_name(
                                prefix='o_fz_t{}_n{}_'.format(test_round, len(self.solution.graph.nodes)))
                            solver.save_solution()
                            Analyzer.analyze_flow_size(
                                self.solution,
                                target_filename=os.path.join(config.flow_size_res_dir, self.solution.solution_name))
                            self.solution.generate_solution_name(
                                prefix='o_fz_t{}_n{}_f{}_'.format(test_round, len(self.solution.graph.nodes), i))
                            Analyzer.analyze_flow_routes_repetition_degree(
                                self.solution,
                                target_filename=os.path.join(config.flow_routes_repetition_degree_dir,
                                                             self.solution.solution_name))
                    except:
                        # save flows if error happen
                        FlowGenerator.save_flows(flows)


if __name__ == '__main__':
    unittest.main()
