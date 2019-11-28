from typing import Dict, List

import networkx as nx
import matplotlib.pyplot as plt

from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.TopoStrategy import TopoStrategy
from src.type import NodeId


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

    def generate_core_topo(self) -> nx.Graph:
        '''
        generate topology for core nodes
        :return: core nodes topology
        '''
        return self.__topo_strategy.generate()

    def attach_edge_nodes(self, graph: nx.Graph, n: int) -> List[NodeId]:
        '''
        attach edge noeds to graph according to the degree of nodes
        :param graph: old graph
        :param n: number of edge nodes
        :return: new graph
        '''
        # TODO link edge node to core topology
        w: List[float] = []
        nodes: List[NodeId] = list(graph.nodes)
        nodes_num: int = nodes.__len__()
        for node in nodes:
            d: int = graph.degree(node)
            w.append(-d)
        from src.utils.computing import softmax
        p: List[float] = softmax(w)
        import numpy as np
        p: np.array = np.array(p).ravel()
        attached_nodes: List[NodeId] = []
        for i in range(nodes_num):
            selected_node: NodeId = np.random.choice(nodes, p=p)
            attached_nodes.append(selected_node)
        edge_nodes: List[NodeId] = []
        for i, node in enumerate(range(nodes_num + 1, nodes_num + n + 1)):
            graph.add_edge(node, attached_nodes[i])
            graph.add_edge(attached_nodes[i], node)
            edge_nodes.append(node)
        return edge_nodes

    @staticmethod
    def draw(graph: nx.Graph):
        options: dict = {
            'with_labels': True,
            'font_weight': 'bold',
        }  # options for networkx to draw
        plt.subplot(121)
        nx.draw(graph, **options)
        plt.show()
