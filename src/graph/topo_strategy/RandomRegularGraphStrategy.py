import logging
from enum import Enum

import networkx as nx

from src.graph.topo_strategy.TopoStrategy import TopoStrategy

logger = logging.getLogger(__name__)


class RandomRegularGraphStrategy(TopoStrategy):
    __n: int  # number of nodes
    __d: int  # degree of each node

    def __init__(self, d: int = 0, n: int = 0):
        self.__d = d
        self.__n = n

    @property
    def d(self):
        return self.__d

    @d.setter
    def d(self, d: int):
        self.__d = d

    @property
    def n(self):
        return self.__n

    @n.setter
    def n(self, n: int):
        self.__n = n

    def generate(self) -> nx.DiGraph:
        return nx.random_regular_graph(self.__d, self.__n).to_directed()
