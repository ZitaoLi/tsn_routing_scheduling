import abc
import copy
from typing import List, Dict, Set

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Node import Node
from src.graph.reliability_strategy.MultiRoutesReliabilityStrategy import MultiRoutesReliabilityStrategy
from src.graph.reliability_strategy.ReliabilityStrategy import ReliabilityStrategy
from src.type import FlowId, EdgeId, NodeId


class RoutingStrategy(metaclass=abc.ABCMeta):
    nodes: List[int]
    edges: List[int]
    flows: List[int]
    node_mapper: Dict[int, Node]
    edge_mapper: Dict[int, Edge]
    flow_mapper: Dict[int, Flow]
    failure_queue: Set[FlowId]
    _reliability_strategy: ReliabilityStrategy

    def __init__(self, nodes: List[int], edges: List[int], flows: List[int], node_mapper: Dict[int, Node],
                 edge_mapper: Dict[int, Edge], flow_mapper: Dict[int, Flow]):
        self.nodes = nodes
        self.edges = edges
        self.flows = flows
        self.node_mapper = node_mapper
        self.edge_mapper = edge_mapper
        self.flow_mapper = flow_mapper
        self.failure_queue = set()
        self._reliability_strategy = None

    @property
    def reliability_strategy(self):
        return self._reliability_strategy

    @reliability_strategy.setter
    def reliability_strategy(self, reliability_strategy: ReliabilityStrategy):
        self._reliability_strategy = reliability_strategy

    def sort_flows_id_list(self, flows: List[int]):
        '''
        sort flows list by priority from <reliability requirement> to <deadline requirement> [NOTED]
        :param flows: flows list to sort
        :return: sorted flows list
        '''
        flows: List[int] = copy.copy(flows)
        flows.sort(key=lambda fid: self.flow_mapper[fid].deadline)
        flows.sort(key=lambda fid: self.flow_mapper[fid].reliability)
        return flows

    @abc.abstractmethod
    def route(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        '''
        route flows
        :param flow_id_list: list of flow id
        :param args:
        :param kwargs:
        :return: set of failed flows
        '''
        pass

    @abc.abstractmethod
    def check(self, **kwargs) -> bool:
        '''
        check something
        :param kwargs:
        :return:
        '''
        pass

    def check_e2e_reliability(self, routes: List[List[EdgeId]], src: NodeId, dest: NodeId, *args, **kwargs) -> bool:
        '''
        check end-to-end reliability between source/destination pair
        :param routes:
        :param src:
        :param dest:
        :param args:
        :param kwargs:
        :return:
        '''
        return self._reliability_strategy.check_e2e_reliability(routes, src, dest, *args, **kwargs)
