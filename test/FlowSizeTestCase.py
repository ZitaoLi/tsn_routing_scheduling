import logging
import unittest
from enum import Enum
from typing import List, Tuple

import networkx as nx

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
                                            flows=None,
                                            topo_strategy=topo_strategy_entity['strategy'],
                                            routing_strategy=config.GRAPH_CONFIG['routing-strategy'],
                                            scheduling_strategy=config.GRAPH_CONFIG['scheduling-strategy'],
                                            allocating_strategy=config.GRAPH_CONFIG['allocating-strategy'])
                    solver.add_flows(flows[:i])
                    try:
                        import time
                        import os
                        # origin method
                        self.solution = solver.generate_init_solution()  # get initial solution
                        solution_name: str = solver.generate_solution_name(
                            solution=self.solution,
                            prefix='b_fz_t{}_n{}_'.format(test_round, len(self.solution.graph.nodes)))
                        solver.save_solution()
                        filename: str = os.path.join(config.flow_size_res_dir, solution_name)
                        solver.analyze(solution=self.solution, target_filename=filename)  # analyze solution
                        if config.OPTIMIZATION['enable'] is True:
                            # optimized method
                            self.solution = solver.optimize()  # optimize
                            solution_name: str = solver.generate_solution_name(
                                solution=self.solution,
                                prefix='o_fz_t{}_n{}_'.format(test_round, len(self.solution.graph.nodes)))
                            solver.save_solution()
                            filename: str = os.path.join(config.flow_size_res_dir, solution_name)
                            solver.analyze(solution=self.solution, target_filename=filename)
                    except:
                        # save flows if error happen
                        FlowGenerator.save_flows(flows)


if __name__ == '__main__':
    unittest.main()
