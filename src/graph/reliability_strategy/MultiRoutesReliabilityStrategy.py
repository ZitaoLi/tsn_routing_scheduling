from typing import List

from src import config
from src.graph.reliability_strategy.ReliabilityStrategy import ReliabilityStrategy
from src.type import EdgeId, FlowId, NodeId


class MultiRoutesReliabilityStrategy(ReliabilityStrategy):

    def check_e2e_reliability(self, routes: List[List[EdgeId]], src: NodeId, dest: NodeId, *args, **kwargs) -> bool:
        if len(routes) == config.FLOW_CONFIG['redundancy_degree']:
            return True
        return False
