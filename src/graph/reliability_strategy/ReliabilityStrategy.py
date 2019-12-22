import abc
import copy
from typing import List, Dict, Set

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Node import Node
from src.type import FlowId, EdgeId, NodeId


class ReliabilityStrategy(metaclass=abc.ABCMeta):
    nodes: List[int]
    edges: List[int]
    flows: List[int]
    node_mapper: Dict[int, Node]
    edge_mapper: Dict[int, Edge]
    flow_mapper: Dict[int, Flow]
    failure_queue: Set[FlowId]

    def __init__(self, nodes: List[int], edges: List[int], flows: List[int], node_mapper: Dict[int, Node],
                 edge_mapper: Dict[int, Edge], flow_mapper: Dict[int, Flow]):
        self.nodes = nodes
        self.edges = edges
        self.flows = flows
        self.node_mapper = node_mapper
        self.edge_mapper = edge_mapper
        self.flow_mapper = flow_mapper
        self.failure_queue = set()

    @abc.abstractmethod
    def check_e2e_reliability(self, routes: List[List[EdgeId]], src: NodeId, dest: NodeId, *args, **kwargs) -> bool:
        '''
        check end to end reliability
        :param dest:
        :param src:
        :param routes:
        :param args:
        :param kwargs:
        :return:
        '''
        pass

