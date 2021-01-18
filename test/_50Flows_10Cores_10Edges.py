import logging
import os
import unittest
from enum import Enum
from typing import List, Tuple, Dict

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
from src.type import NodeId, EdgeId, FlowId, TOPO_STRATEGY, ROUTING_STRATEGY, SCHEDULING_STRATEGY, ALLOCATING_STRATEGY, \
    RELIABILITY_STRATEGY, TIME_GRANULARITY
import src.config as config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# logging.disable(logging.INFO)


class _50Flows_10Cores_10Edges(unittest.TestCase):

    def setUp(self):
        config.TESTING['flow-size'] = 20
        config.TESTING['draw-gantt-chart'] = True
        config.OPTIMIZATION['enable'] = True
        config.FLOW_CONFIG['redundancy_degree'] = 2  # at least 2 end-to-end routes
        config.FLOW_CONFIG['max-redundancy-degree'] = 5  # the most no. of end-to-end routes
        config.FLOW_CONFIG['un-neighbors_degree'] = 1  # avoid source and node connecting at the same node
        config.FLOW_CONFIG['size-set'] = [int(1.6e3), int(5e3), int(1e3)]  # [200B, 625B, 125B]
        config.FLOW_CONFIG['period-set'] = [int(1e5), int(1.5e5), int(3e5)]  # [100us, 150us, 300us]
        config.FLOW_CONFIG['hyper-period'] = int(3e5)  # [300us]
        config.FLOW_CONFIG['deadline-set'] = [int(1e8), int(5e7), int(2e7)]  # [100ms, 50ms, 20ms]
        config.FLOW_CONFIG['reliability-set'] = [0.5]  # [0.98]
        config.GRAPH_CONFIG['time-granularity'] = TIME_GRANULARITY.NS
        config.GRAPH_CONFIG['all-bandwidth'] = 1  # 500Mbps
        config.GRAPH_CONFIG['all-propagation-delay'] = 0  # 1e2 100ns
        config.GRAPH_CONFIG['all-process-delay'] = 0  # 5e3 5us
        config.GRAPH_CONFIG['all-per'] = 0.01  # 0.4%
        config.GRAPH_CONFIG['core-node-num'] = 10
        config.GRAPH_CONFIG['edge-node-num'] = 10
        config.GRAPH_CONFIG['edge-nodes-distribution-degree'] = 6
        config.OPTIMIZATION['max_iterations'] = 5
        config.OPTIMIZATION['max_iterations'] = 10

    def tearDown(self):
        pass

    def run_test(self, topo_strategy_entities: List, combinations: List = None):
        for topo_strategy_entity in topo_strategy_entities:
            # set topology strategy
            self.topo_generator.topo_strategy = TopoStrategyFactory.get_instance(**topo_strategy_entity)
            # generate topology
            graph: nx.Graph = self.topo_generator.generate_core_topo()
            attached_edge_nodes_num: int = config.GRAPH_CONFIG['edge-node-num']
            attached_edge_nodes: List[NodeId] = self.topo_generator.attach_edge_nodes(graph, attached_edge_nodes_num)
            self.topo_generator.draw(graph)
            # generate flows
            flows: List[Flow] = FlowGenerator.generate_flows(edge_nodes=attached_edge_nodes,
                                                             graph=graph,
                                                             flow_num=config.TESTING['flow-size'])
            for combination in combinations:
                solver: Solver = Solver(nx_graph=graph,
                                        flows=flows[:],
                                        topo_strategy=topo_strategy_entity['strategy'],
                                        routing_strategy=combination['routing_strategy'],
                                        scheduling_strategy=combination['scheduling_strategy'],
                                        allocating_strategy=combination['allocating_strategy'],
                                        reliability_strategy=combination['reliability_strategy'])
                # origin method
                solution = solver.generate_init_solution()  # get initial solution
                solution.generate_solution_name(
                    prefix='b_sim_n{}_'.format(len(solution.graph.nodes)))
                Analyzer.analyze_per_flow(
                    solution,
                    target_filename=os.path.join(config.solutions_res_dir, solution.solution_name))
                if config.TESTING['draw-gantt-chart'] is True:
                    solver.draw_gantt_chart(solution)
                logger.info('Native Objective: ' + str(solver.objective_function(solution)))
                # optimized method
                if config.OPTIMIZATION['enable'] is False or \
                        combination['allocating_strategy'] == ALLOCATING_STRATEGY.AEAPBF_ALLOCATING_STRATEGY or \
                        combination['allocating_strategy'] == ALLOCATING_STRATEGY.AEAPWF_ALLOCATING_STRATEGY or \
                        combination['routing_strategy'] == ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY:
                    continue
                solution = solver.optimize()  # optimize
                solution.generate_solution_name(
                    prefix='o_sim_n{}_'.format(len(solution.graph.nodes)))
                Analyzer.analyze_per_flow(
                    solution,
                    target_filename=os.path.join(config.solutions_res_dir, solution.solution_name))
                if config.TESTING['draw-gantt-chart'] is True:
                    solver.draw_gantt_chart(solution)
                logger.info('Optimal Objective: ' + str(solver.objective_function(solution)))

    def test(self):
        self.topo_generator: TopoGenerator = TopoGenerator()
        self.run_test(
            [
                # {'strategy': TOPO_STRATEGY.RRG_STRATEGY, 'd': 3, 'n': 10},
                {'strategy': TOPO_STRATEGY.ER_STRATEGY, 'type': ErdosRenyiStrategy.ER_TYPE.GNP, 'n': 10, 'm': 14,
                 'p': 0.3},
                # {'strategy': TOPO_STRATEGY.BA_STRATEGY, 'n': 10, 'm': 3},
                # {'strategy': TOPO_STRATEGY.WS_STRATEGY, 'n': 10, 'k': 2, 'p': 1.0}
            ],
            [
                {
                    'routing_strategy': ROUTING_STRATEGY.DIJKSTRA_SINGLE_ROUTING_STRATEGY,
                    'reliability_strategy': RELIABILITY_STRATEGY.UNI_ROUTES_RELIABILITY_STRATEGY,
                    'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                    'allocating_strategy': ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY
                },
                {
                    'routing_strategy': ROUTING_STRATEGY.BACKTRACKING_REDUNDANT_ROUTING_STRATEGY,
                    'reliability_strategy': RELIABILITY_STRATEGY.ENUMERATION_METHOD_RELIABILITY_STRATEGY,
                    'scheduling_strategy': SCHEDULING_STRATEGY.LRF_REDUNDANT_SCHEDULING_STRATEGY,
                    'allocating_strategy': ALLOCATING_STRATEGY.AEAP_ALLOCATING_STRATEGY
                },
            ]
        )


if __name__ == '__main__':
    unittest.main()
