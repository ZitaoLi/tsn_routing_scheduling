import json
import logging
from typing import List

logger = logging.getLogger(__name__)


class Node:
    node_id: int
    in_edge_num: int
    out_edge_num: int
    in_edge: List
    out_edge: List
    color: int

    def __init__(self, node_id):
        self.node_id = node_id
        self.in_edge_num = 0
        self.out_edge_num = 0
        self.in_edge = []
        self.out_edge = []
        self.color = 0  # RED = 1, WHITE = 0

    def to_string(self):
        _in_edges: List[int] = []
        _out_edges: List[int] = []
        for _e in self.in_edge:
            _in_edges.append(_e.edge_id)
        for _e in self.out_edge:
            _out_edges.append(_e.edge_id)
        o = {
            'node id': self.node_id,
            'inbound edge': _in_edges,
            'outbound edge': _out_edges
        }
        _json: str = json.dumps(o)
        logger.info(_json)

    def append_in_edge(self, edge):
        self.in_edge_num += 1
        self.in_edge.append(edge)

    def append_out_edge(self, edge):
        self.out_edge_num += 1
        self.out_edge.append(edge)
