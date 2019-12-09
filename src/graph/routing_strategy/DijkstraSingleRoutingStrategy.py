import logging
from typing import List, Set, Dict

import networkx as nx

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Node import Node
from src.graph.routing_strategy.SingleRoutingStrategy import SingleRoutingStrategy
from src.type import FlowId, NodeId, EdgeId

logger = logging.getLogger(__name__)


class DijkstraSingleRoutingStrategy(SingleRoutingStrategy):
    graph: nx.Graph

    def __init__(self, nodes: List[int], edges: List[int], flows: List[int], node_mapper: Dict[int, Node],
                 edge_mapper: Dict[int, Edge], flow_mapper: Dict[int, Flow], nx_graph: nx.Graph = None):
        super().__init__(nodes, edges, flows, node_mapper, edge_mapper, flow_mapper)
        self.graph = nx_graph

    def route(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        for fid in flow_id_list:
            routes: List[List[List[int]]] = []  # routes of flow
            source: NodeId = self.flow_mapper[fid].source
            targets: List[NodeId] = self.flow_mapper[fid].destinations
            for target in targets:
                dijkstra_path_n: List[NodeId] = nx.dijkstra_path(self.graph, source=source, target=target)
                dijkstra_path_e: List[EdgeId] = self.nodes_to_edges(dijkstra_path_n)
                routes.append([dijkstra_path_e])
            self.flow_mapper[fid].routes = routes
            logger.info(self.flow_mapper[fid].to_string())
        return self.failure_queue

    def nodes_to_edges(self, node_id_list: List[NodeId]) -> List[EdgeId]:
        edge_id_list: List[EdgeId] = []
        in_node_id: NodeId = None
        out_node_id: NodeId = None
        for i, node_id in enumerate(node_id_list):
            if i == 0:
                in_node_id = node_id
                continue
            out_node_id = node_id
            edge_id: EdgeId = list(filter(
                lambda eid: self.edge_mapper[eid].in_node.node_id == in_node_id and self.edge_mapper[
                    eid].out_node.node_id == out_node_id, self.edge_mapper))[0]
            edge_id_list.append(edge_id)
            in_node_id = out_node_id
        return edge_id_list
