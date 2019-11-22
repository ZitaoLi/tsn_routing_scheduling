from typing import Dict

import networkx as nx
import matplotlib.pyplot as plt

from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.TopoStrategy import TopoStrategy


class TopoGenerator(object):

    __topo_strategy: TopoStrategy  # topology generation strategy

    def __init__(self, topo_strategy: TopoStrategy = ErdosRenyiStrategy()):
        '''
        :param topo_strategy: topology generation strategy, default strategy is Erdos-Renyi
        '''
        self.__topo_strategy = topo_strategy

    @property
    def topo_strategy(self) -> TopoStrategy:
        return self.__topo_strategy

    @topo_strategy.setter
    def topo_strategy(self, topo_strategy: TopoStrategy):
        self.__topo_strategy = topo_strategy

    def generate_topo(self) -> nx.DiGraph:
        return self.__topo_strategy.generate()

    @staticmethod
    def draw(graph: nx.Graph):
        options: dict = {
            'with_labels': True,
            'font_weight': 'bold',
        }  # options for networkx to draw
        plt.subplot(121)
        nx.draw(graph, **options)
        plt.show()
