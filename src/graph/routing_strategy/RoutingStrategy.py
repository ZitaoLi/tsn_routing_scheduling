import abc
from typing import List, Dict, Set

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Node import Node
from src.type import FlowId


class RoutingStrategy(metaclass=abc.ABCMeta):
    nodes: List[int]
    edges: List[int]
    flows: List[int]
    node_mapper: Dict[int, Node]
    edge_mapper: Dict[int, Edge]
    flow_mapper: Dict[int, Flow]
    failure_queue: Set[int]

    def __init__(self, nodes: List[int], edges: List[int], flows: List[int], node_mapper: Dict[int, Node],
                 edge_mapper: Dict[int, Edge], flow_mapper: Dict[int, Flow]):
        self.nodes = nodes
        self.edges = edges
        self.flows = flows
        self.node_mapper = node_mapper
        self.edge_mapper = edge_mapper
        self.flow_mapper = flow_mapper
        self.failure_queue = set()

    @staticmethod
    def sort_flows_id_list(flows: List[int]):
        '''
        sort flows list by priority from <reliability requirement> to <deadline requirement> [NOTED]
        :param flows: flows list to sort
        :return: sorted flows list
        '''
        #  TODO sort flows list
        return flows

    @abc.abstractmethod
    def route(self, flow_id_list: List[FlowId], *args, **kwargs):
        pass