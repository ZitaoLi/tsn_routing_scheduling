from typing import List

from src import config
from src.graph.reliability_strategy.ReliabilityStrategy import ReliabilityStrategy
from src.type import EdgeId, FlowId, NodeId


class UniRoutesReliabilityStrategy(ReliabilityStrategy):

    def check_e2e_reliability(self, routes: List[List[EdgeId]], src: NodeId, dest: NodeId, *args, **kwargs) -> bool:
        reliability_value: float = self.compute_e2e_reliability(routes, src, dest)
        self.flow_mapper[kwargs['fid']].routes_reliability[dest] = reliability_value
        # if self.flow_mapper[kwargs['fid']].reliability > reliability_value:
        #     return False
        return True
