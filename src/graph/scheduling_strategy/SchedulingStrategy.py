import abc
import copy
from typing import List, Dict, Set

from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Node import Node
from src.graph.TimeSlotAllocator import TimeSlotAllocator
from src.graph.allocating_strategy.AEAPAllocatingStrategy import AEAPAllocatingStrategy
from src.graph.allocating_strategy.AllocatingStrategy import AllocatingStrategy
from src.type import FlowId


class SchedulingStrategy(metaclass=abc.ABCMeta):
    nodes: List[int]
    edges: List[int]
    flows: List[int]
    node_mapper: Dict[int, Node]
    edge_mapper: Dict[int, Edge]
    flow_mapper: Dict[int, Flow]
    failure_queue: Set[int]
    __allocating_strategy: AllocatingStrategy  # allocating strategy

    def __init__(self, nodes: List[int], edges: List[int], flows: List[int], node_mapper: Dict[int, Node],
                 edge_mapper: Dict[int, Edge], flow_mapper: Dict[int, Flow]):
        self.nodes = nodes
        self.edges = edges
        self.flows = flows
        self.node_mapper = node_mapper
        self.edge_mapper = edge_mapper
        self.flow_mapper = flow_mapper
        self.failure_queue = set()
        self.__allocating_strategy = AEAPAllocatingStrategy()  # default allocating strategy

    @abc.abstractmethod
    def schedule(self, flow_id_list: List[FlowId], *args, **kwargs):
        pass

    def allocate(self, flow: Flow, allocator: TimeSlotAllocator, arrival_time_offset: int) -> int:
        return self.__allocating_strategy.allocate(flow, allocator, arrival_time_offset)

    @staticmethod
    def sort_flows_id_list(flows: List[int]) -> List[int]:
        '''
        sort flows list by priority from <deadline requirement>tp <period> to <hops> [NOTED]
        :param flows: flows list to sort
        :return: sorted flows list
        '''
        # TODO sort flows list
        return flows

    @property
    def allocating_strategy(self):
        return self.__allocating_strategy

    @allocating_strategy.setter
    def allocating_strategy(self, allocating_strategy: AllocatingStrategy):
        self.__allocating_strategy = allocating_strategy
