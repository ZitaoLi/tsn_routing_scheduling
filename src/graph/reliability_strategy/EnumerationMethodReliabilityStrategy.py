import copy
from typing import List, Set, Tuple

from src import config
from src.graph.Edge import Edge
from src.graph.Graph import Graph
from src.graph.reliability_strategy.ReliabilityStrategy import ReliabilityStrategy
from src.type import EdgeId, NodeId
from itertools import combinations


class EnumerationMethodReliabilityStrategy(ReliabilityStrategy):

    def check_e2e_reliability(self, routes: List[List[EdgeId]], src: NodeId, dest: NodeId, *args, **kwargs) -> bool:
        if src is None:
            raise RuntimeError('miss parameter "src: NodeId"')
        if dest is None:
            raise RuntimeError('miss parameter "dest: NodeId"')
        if 'fid' not in kwargs.keys():
            raise RuntimeError('miss parameter "fid: FlowId"')
        reliability_value: float = self.compute_e2e_reliability(routes, src, dest)
        if len(routes) == config.FLOW_CONFIG['redundancy_degree'] and \
                self.flow_mapper[kwargs['fid']].reliability <= reliability_value:
            self.flow_mapper[kwargs['fid']].routes_reliability[dest] = reliability_value
            return True
        else:
            return False


