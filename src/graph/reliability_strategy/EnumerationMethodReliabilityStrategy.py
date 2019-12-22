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
        # walked edges
        walked_edges: Set[EdgeId] = set()
        for e2e_route in routes:
            for eid in e2e_route:
                walked_edges.add(eid)
        # enumerate all possible situations
        enum_range: range = range(2, len(walked_edges) + 1)
        candidate_edges: List[Tuple] = []
        for i in enum_range:
            [candidate_edges.append(candidate_edge) for candidate_edge in combinations(walked_edges, i)]
        # compute reliability
        available_edges: List[Tuple] = self.compute_available_edges(candidate_edges=candidate_edges, src=src, dest=dest)
        if available_edges.__len__() == 0:
            raise RuntimeError('available edges must not be empty')
        reliability_value: float = 1.0
        for available_edge in available_edges:
            other_edge: Set[EdgeId] = walked_edges - available_edge
            successful_reliability: float = 1.0
            for eid in available_edge:
                successful_reliability *= 1 - self.edge_mapper[eid].error_rate
            failed_reliability: float = 1.0
            for eid in other_edge:
                failed_reliability *= self.edge_mapper[eid].error_rate
            reliability_value += successful_reliability * failed_reliability
        # quit condition
        if len(routes) == config.FLOW_CONFIG['redundancy_degree'] and kwargs['rel'] <= reliability_value:
            return True
        else:
            return False

    def compute_available_edges(self, candidate_edges: List[Tuple] = None,
                                src: NodeId = None, dest: NodeId = None) -> List[Tuple]:
        if candidate_edges is None:
            raise RuntimeError('miss parameter "candidate_edges: List[Tuple]"')
        if src is None:
            raise RuntimeError('miss parameter "src: NodeId"')
        if dest is None:
            raise RuntimeError('miss parameter "dest: NodeId"')
        l0_candidate_edges: List[Edge] = candidate_edges
        # check source edges
        src_out_edges: List[Edge] = self.node_mapper[src].out_edge
        l1_candidate_edges: List[Tuple] = []
        for candidate_edge in l0_candidate_edges:
            flag: bool = False
            for edge_id in candidate_edge:
                if edge_id in src_out_edges:
                    flag = True
                    break
            if flag is True:
                l1_candidate_edges.append(candidate_edge)
        # check destination edges
        dest_in_edges: List[Edge] = self.node_mapper[dest].in_edge
        l2_candidate_edges: List[Tuple] = []
        for candidate_edge in l1_candidate_edges:
            flag: bool = False
            for edge_id in candidate_edge:
                if edge_id in dest_in_edges:
                    flag = True
                    break
            if flag is True:
                l2_candidate_edges.append(candidate_edge)
        # check end-to-end
        available_edges: List[Tuple] = []
        for candidate_edge in l2_candidate_edges:
            src_edge_id: EdgeId = None
            dest_edge_id: EdgeId = None
            for edge_id in candidate_edges:
                if edge_id in src_out_edges:
                    src_edge_id = edge_id
            for edge_id in candidate_edges:
                if edge_id in dest_in_edges:
                    dest_edge_id = edge_id
            if self.check_connectivity(current_edge_id=src_edge_id, dest_edge_id=dest_edge_id,
                                       candidate_edge=candidate_edge):
                available_edges.append(candidate_edge)
        return available_edges

    def check_connectivity(self, current_edge_id: EdgeId = None, dest_edge_id: EdgeId = None,
                           candidate_edge: Tuple[EdgeId] = None) -> bool:
        if current_edge_id is None:
            raise RuntimeError('miss parameter "current_edge_id: EdgeId"')
        if dest_edge_id is None:
            raise RuntimeError('miss parameter "dest_edge_id: EdgeId"')
        if candidate_edge is None:
            raise RuntimeError('miss parameter "candidate_edges: Tuple[EdgeId]"')
        candidate_edge: Tuple[EdgeId] = copy.copy(candidate_edge)
        candidate_edge.remove(current_edge_id)
        # True quit condition
        if current_edge_id == dest_edge_id:
            return True
        out_edges: List[Edge] = self.edge_mapper[current_edge_id].out_node.out_edge
        next_edges: List[Edge] = []
        flag: bool = False
        for out_edge in out_edges:
            if out_edge.edge_id in candidate_edge:
                flag = True
                next_edges.append(out_edge)
        # False quit condition
        if flag is False:
            return False  # there is no next edges in candidate edges
        for next_edge in next_edges:
            if next_edge in candidate_edge:
                self.check_connectivity(current_edge_id=next_edge, dest_edge_id=dest_edge_id,
                                        candidate_edge=candidate_edge)
