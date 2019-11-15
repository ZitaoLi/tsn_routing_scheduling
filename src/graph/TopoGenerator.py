from typing import Dict

import networkx as nx
import matplotlib.pyplot as plt

from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.TopoStrategy import TopoStrategy


class TopoGenerator(object):

    topo_strategy: TopoStrategy  # topology generation strategy

    def __init__(self, topo_strategy: TopoStrategy = ErdosRenyiStrategy()):
        '''
        :param topo_strategy: topology generation strategy, default strategy is Erdos-Renyi
        '''
        self.topo_strategy = topo_strategy

    def set_topo_strategy(self, topo_strategy: TopoStrategy):
        self.topo_strategy = topo_strategy

    def generate_topo(self) -> nx.Graph:
        return self.topo_strategy.generate()

    @staticmethod
    def draw(graph: nx.Graph):
        options: dict = {
            'with_labels': True,
            'font_weight': 'bold',
        }  # options for networkx to draw
        nx.draw(graph, **options)
        plt.show()
