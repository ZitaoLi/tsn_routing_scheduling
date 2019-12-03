import logging
from typing import Dict, List, Set

import networkx as nx
import matplotlib.pyplot as plt

from src import config
from src.graph.topo_strategy.ErdosRenyiStrategy import ErdosRenyiStrategy
from src.graph.topo_strategy.TopoStrategy import TopoStrategy
from src.type import NodeId

logger = logging.getLogger(__name__)


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
        logger.info('topology generation strategy: ' + str(type(self.__topo_strategy)))
        return self.__topo_strategy.generate()

    def attach_edge_nodes(self, graph: nx.Graph, n: int) -> List[NodeId]:
        '''
        attach edge noeds to graph according to the degree of nodes
        :param graph: old graph
        :param n: number of edge nodes
        :return: new graph
        '''
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
        t: Set[NodeId] = set()
        # avoid all edge nodes attach at the same core node
        while t.__len__() <= config.GRAPH_CONFIG['edge-nodes-distribution-degree']:
            attached_nodes = []
            t = set()
            for i in range(nodes_num):
                selected_node: NodeId = np.random.choice(nodes, p=p)
                attached_nodes.append(selected_node)
                t.add(selected_node)
        edge_nodes: List[NodeId] = []
        for i, node in enumerate(range(nodes_num + 1, nodes_num + n + 1)):
            graph.add_edge(node, attached_nodes[i])
            graph.add_edge(attached_nodes[i], node)
            edge_nodes.append(node)
        return edge_nodes

    def attach_edge_nodes_sparse(self, graph: nx.Graph, n: int) -> List[NodeId]:
        '''
        attach edge noeds to graph according to the degree of nodes
        :param graph: old graph
        :param n: number of edge nodes
        :return: new graph
        '''
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
        t: Set[NodeId] = set()
        # avoid all edge nodes attach at the same core node
        while t.__len__() <= config.GRAPH_CONFIG['edge-nodes-distribution-degree']:
            attached_nodes = []
            t = set()
            for i in range(nodes_num):
                selected_node: NodeId = np.random.choice(nodes, p=p)
                attached_nodes.append(selected_node)
                t.add(selected_node)
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
