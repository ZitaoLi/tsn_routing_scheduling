import json
from typing import List, Dict, Set

from src.graph import TimeSlotAllocator
from src.graph.Node import Node
from src.graph.Edge import Edge
from src.graph.Flow import Flow
import logging

logger = logging.getLogger(__name__)


class FlowScheduler:
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

    def sort_flows(self, flows: List[int]) -> List[int]:
        '''
        sort flows list by priority from <deadline requirement>tp <period> to <hops> [NOTED]
        :param flows: flows list to sort
        :return: sorted flows list
        '''
        # TODO sort flows list
        return flows

    @staticmethod
    def sort_route(routes: List[List[int]]) -> List[List[int]]:
        """
        sort flows list by priority from <sum of edge delay> to <period> to <hops> [NOTED]
        :param routes: flow routes to sort
        :return: sorted flow routes
        """
        # TODO sort routes of flow
        _routes = sorted(routes, key=lambda r: len(r), reverse=True)
        logger.info('sorted routes: ' + str(json.dumps(_routes)))
        return _routes

    def schedule_flows(self, flows: List[int], is_sort: bool = True):
        if is_sort is True:
            flows = self.sort_flows(flows)
        for _fid in flows:
            if not self.schedule_single_flow(self.flow_mapper[_fid]):
                self.failure_queue.add(_fid)
                logger.info('add flow [' + str(_fid) + '] into failure queue')
        logger.info('FAILURE QUEUE:' + str(self.failure_queue))

    def schedule_all_flows(self):
        self.schedule_flows(self.flows)

    def route_flows_incrementally(self, flows: List[int]):
        self.schedule_flows(flows)

    def schedule_single_flow(self, flow: Flow) -> bool:
        logger.info('schedule flow [' + str(flow.flow_id) + ']...')
        _all_routes: List[List[List[int]]] = flow.get_routes()
        _union_routes: List[List[int]] = []
        for _e2e_routes in _all_routes:
            for _e2e_route in _e2e_routes:
                _union_routes.append(_e2e_route)
        _union_routes = self.sort_route(_union_routes)
        _ER: List[int] = []  # recover list
        for _e2e_route in _union_routes:
            if not self.schedule_end2end(flow, _e2e_route):
                logger.info('scheduling flow [' + str(flow.flow_id) + '] failure')
                # TODO recover time slots allocation on edge
                for __e2e_route in _ER:
                    for _eid in __e2e_route:
                        self.edge_mapper[_eid].time_slot_allocator.recover_scene()
                return False
            else:
                _ER.append(_e2e_route)
        logger.info('scheduling flow [' + str(flow.flow_id) + '] successful')
        return True

    def schedule_end2end(self, flow: Flow, route: List[int]) -> bool:
        _arrival_time_offset: int = 0
        _E: List[Edge] = []
        for _eid in route:
            _e: Edge = self.edge_mapper[_eid]  # get edge
            _E.append(_e)
            _allocator: TimeSlotAllocator = _e.time_slot_allocator  # get time slot allocator
            _allocator.save_scene()  # save scene
            _arrival_time_offset: int = _allocator.allocate_aeap_overlap(flow, _arrival_time_offset)
            # _arrival_time_offset: int = _allocator.allocate_aeap(flow, _arrival_time_offset)
            # TODO fix bug here
            if _arrival_time_offset == -1:
                # recover scene
                for _e in _E:
                    _e.time_slot_allocator.recover_scene()
                return False
        return True
