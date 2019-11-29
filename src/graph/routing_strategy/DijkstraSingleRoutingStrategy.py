from typing import List, Set

import networkx as nx

from src.graph.routing_strategy.SingleRoutingStrategy import SingleRoutingStrategy
from src.type import FlowId


class DijkstraSingleRoutingStrategy(SingleRoutingStrategy):

    def route(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        # nx.dijkstra_path(G, source=0, target=0)
        pass