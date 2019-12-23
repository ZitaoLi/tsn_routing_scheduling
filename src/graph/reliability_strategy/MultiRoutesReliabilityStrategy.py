from typing import List

from src import config
from src.graph.reliability_strategy.ReliabilityStrategy import ReliabilityStrategy
from src.type import EdgeId, FlowId, NodeId


class MultiRoutesReliabilityStrategy(ReliabilityStrategy):

    def check_e2e_reliability(self, routes: List[List[EdgeId]], src: NodeId, dest: NodeId, *args, **kwargs) -> bool:
        reliability_value: float = self.compute_e2e_reliability(routes, src, dest)
        if len(routes) == config.FLOW_CONFIG['redundancy_degree']:
            self.flow_mapper[kwargs['fid']].routes_reliability[dest] = reliability_value
            return True
        else:
            return False
