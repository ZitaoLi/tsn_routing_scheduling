import logging
from enum import Enum

import networkx as nx

from src.graph.topo_strategy.TopoStrategy import TopoStrategy

logger = logging.getLogger(__name__)


class BarabasiAlbertStrategy(TopoStrategy):
    __n: int  # number of nodes
    __m: int  # number of edges attached to origin nodes

    def __init__(self, n: int = 0, m: int = 0):
        self.__n = n
        self.__m = m

    @property
    def n(self):
        return self.__n

    @n.setter
    def n(self, n: int):
        self.__n = n

    @property
    def m(self):
        return self.__m

    @m.setter
    def m(self, m: int):
        self.__m = m

    def generate(self) -> nx.DiGraph:
        return nx.barabasi_albert_graph(self.__n, self.__m).to_directed()
