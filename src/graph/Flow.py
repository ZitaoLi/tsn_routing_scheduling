import json
import logging
from typing import List, Set, Tuple, Dict

from src.utils.Visualizer import Visualizer

logger = logging.getLogger(__name__)


class Flow:
    flow_id: int  # flow id
    size: int  # flow size [unit: b]
    period: int  # flow period [unit: ns]
    bandwidth: float  # bandwidth requirement pf flow [unit: b/ns]
    source: int  # source of flow
    destinations: List[int]  # destinations of flow
    reliability: float  # reliability requirement of flow
    deadline: int  # end-to-end delay requirement of flow [unit: ns]
    routes: List[List[List[int]]]  # routes of flow
    routes_reliability: Dict[int, float]  # reliability of routes, e.g., [(d1, e2e_r), ...]
    # routes_delay: Dict[int, float]  # end-to-end delay of routes, e.g., [(d1, e2e_d), ...]
    walked_edges: Set[int]  # the edge flow walked
    negative_walked_edges: Set[int]  # negative walked set used for flow sorting during routing phase

    def __init__(self, fid: int, s: int, p: int, src: int, dest: list, rl: float, dl: int):
        self.flow_id = fid
        self.size = s
        self.period = p
        self.bandwidth = s / p
        self.source = src
        self.destinations = dest
        self.reliability = rl
        self.deadline = dl
        self.routes = []
        self.routes_reliability = dict()
        self.walked_edges = set()
        self.negative_walked_edges = set()
        self.color = Visualizer.random_color()

    def get_routes(self) -> List[List[List[int]]]:
        return self.routes

    def to_string(self):
        o = {
            'flow id': self.flow_id,
            'size': str(self.size) + ' b',
            'period': str(self.period) + ' ns',
            'bandwidth requirement': str(self.size / self.period) + ' b/ns',
            'source host': str(self.source),
            'destination host': self.destinations,
            'reliability': self.reliability,
            'deadline': str(self.deadline) + ' ns',
            'routes': self.routes,
            'routes_reliability': self.routes_reliability,
            'walked_edges': list(self.walked_edges)
        }
        _json = json.dumps(o)
        logger.info(_json)

    def __str__(self):
        o = {
            'flow id': self.flow_id,
            'size': str(self.size) + ' b',
            'period': str(self.period) + ' ns',
            'bandwidth requirement': str(self.size / self.period) + ' b/ns',
            'source host': str(self.source),
            'destination host': self.destinations,
            'reliability': self.reliability,
            'deadline': str(self.deadline) + ' ns',
            'routes': self.routes,
            'routes_reliability': self.routes_reliability,
            'walked_edges': list(self.walked_edges)
        }
        return json.dumps(o)
