import logging
from enum import Enum

import networkx as nx

from src.graph.topo_strategy.TopoStrategy import TopoStrategy

logger = logging.getLogger(__name__)


class ErdosRenyiStrategy(TopoStrategy):
    ER_TYPE = Enum('ER_TYPE', ('GNM', 'GNP'))  # Gnm or Gnp type
    __type: ER_TYPE.GNM  # type of Erdos-Renyi model
    __n: int  # number of nodes
    __m: int  # number of edges
    __p: float  # probability

    def __init__(self, t: ER_TYPE = ER_TYPE.GNM, n: int = 0, m: int = 0, p: float = 0.0):
        # TODO check
        self.__type = t
        self.__n = n
        self.__m = m
        self.__p = p

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

    @property
    def p(self):
        return self.__p

    @p.setter
    def p(self, p: float):
        self.__p = p

    def generate(self) -> nx.Graph:
        pass
