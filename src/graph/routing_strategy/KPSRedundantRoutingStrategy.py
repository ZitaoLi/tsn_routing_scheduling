from typing import List

import networkx as nx

from src.graph.routing_strategy.RedundantRoutingStrategy import RedundantRoutingStrategy
from src.type import FlowId


class KPSRedundantRoutingStrategy(RedundantRoutingStrategy):

    def route(self, flow_id_list: List[FlowId], *args, **kwargs):
        # nx.all_simple_paths(G, source=0, target=0)
        pass