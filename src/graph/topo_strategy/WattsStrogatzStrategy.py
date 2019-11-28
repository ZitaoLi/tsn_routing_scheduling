import logging
from enum import Enum

import networkx as nx

from src import config
from src.graph.topo_strategy.TopoStrategy import TopoStrategy

logger = logging.getLogger(__name__)


class WattsStrogatzStrategy(TopoStrategy):
    __n: int  # number of nodes
    __k: int  # kth nearest neighbors
    __p: float  # relink probability of each edge

    def __init__(self, n: int = 0, k: int = 0, p: float = 1.0):
        self.__n = n
        self.__k = k
        self.__p = p

    @property
    def n(self):
        return self.__n

    @n.setter
    def n(self, n: int):
        self.__n = n

    @property
    def k(self):
        return self.__k

    @k.setter
    def k(self, k: int):
        self.__k = k

    @property
    def p(self):
        return self.__p

    @p.setter
    def p(self, p: float):
        self.__p = p

    def generate(self) -> nx.DiGraph:
        g: nx.Graph = None
        for i in range(config.GRAPH_CONFIG['max-try-times']):
            g = nx.watts_strogatz_graph(self.__n, self.k, self.__p)
            if len(list(nx.connected_components(g))) == 1:
                return g.to_directed()
        raise RuntimeError('fail to generate ErdosRenyi Graph')
