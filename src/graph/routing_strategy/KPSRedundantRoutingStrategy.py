from typing import List, Set

import networkx as nx

from src.graph.routing_strategy.RedundantRoutingStrategy import RedundantRoutingStrategy
from src.type import FlowId


class KPSRedundantRoutingStrategy(RedundantRoutingStrategy):

    def route(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        # nx.all_simple_paths(G, source=0, target=0)
        pass
