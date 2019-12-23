from typing import List, Dict, Set

from src.graph.Flow import Flow
from src.graph.Edge import Edge
from src.graph.Node import Node
import logging

from src.graph.reliability_strategy.MultiRoutesReliabilityStrategy import MultiRoutesReliabilityStrategy
from src.graph.reliability_strategy.ReliabilityStrategy import ReliabilityStrategy
from src.graph.routing_strategy.BackTrackingRedundantRoutingStrategy import BackTrackingRedundantRoutingStrategy
from src.graph.routing_strategy.RoutingStrategy import RoutingStrategy
from src.type import FlowId

logger = logging.getLogger(__name__)


class FlowRouter:
    nodes: List[int]
    edges: List[int]
    flows: List[int]
    node_mapper: Dict[int, Node]
    edge_mapper: Dict[int, Edge]
    flow_mapper: Dict[int, Flow]
    failure_queue: Set[int]
    overlapped: bool
    flow_walked_edges: Dict[int, Set[int]]
    flow_walked_edges_c: Dict[int, Set[int]]
    __routing_strategy: RoutingStrategy
    __reliability_strategy: ReliabilityStrategy

    def __init__(self, nodes: List[int], edges: List[int], flows: List[int], node_mapper: Dict[int, Node],
                 edge_mapper: Dict[int, Edge], flow_mapper: Dict[int, Flow]):
        self.nodes = nodes
        self.edges = edges
        self.flows = flows
        self.node_mapper = node_mapper
        self.edge_mapper = edge_mapper
        self.flow_mapper = flow_mapper
        self.failure_queue = set()
        self.overlapped = False
        self.init_flow_walked_edges()
        # default routing strategy is Long-Routes-First Redundant Routing Strategy
        self.__routing_strategy = \
            BackTrackingRedundantRoutingStrategy(nodes, edges, flows, node_mapper, edge_mapper, flow_mapper)
        self.__reliability_strategy = \
            MultiRoutesReliabilityStrategy(nodes, edges, flows, node_mapper, edge_mapper, flow_mapper)
        self.__routing_strategy.reliability_strategy = self.__reliability_strategy

    @staticmethod
    def sort_flows(flows: List[int]):
        '''
        sort flows list by priority from <reliability requirement> to <deadline requirement> [NOTED]
        :param flows: flows list to sort
        :return: sorted flows list
        '''
        #  TODO sort flows list
        return flows

    @property
    def routing_strategy(self):
        return self.routing_strategy

    @routing_strategy.setter
    def routing_strategy(self, routing_strategy: RoutingStrategy):
        self.__routing_strategy = routing_strategy
        self.__routing_strategy.reliability_strategy = self.__reliability_strategy

    @property
    def reliability_strategy(self):
        return self.__reliability_strategy

    @reliability_strategy.setter
    def reliability_strategy(self, reliability_strategy: ReliabilityStrategy):
        self.__reliability_strategy = reliability_strategy
        self.__routing_strategy.reliability_strategy = reliability_strategy

    def route(self, flow_is_list: List[FlowId]):
        self.failure_queue = self.__routing_strategy.route(flow_is_list, sorting_enabled=True)

########################################################################################################################

    def set_overlapped(self, overlapped):
        self.overlapped = overlapped

    def init_flow_walked_edges(self):
        for _fid in self.flows:
            self.flow_walked_edges[_fid] = set()
            self.flow_walked_edges_c[_fid] = set()

    def save_flow_walked_edges(self):
        self.flow_walked_edges_c = self.flow_walked_edges

    def recover_flow_walked_edges(self):
        self.flow_walked_edges = self.flow_walked_edges_c

    def save_weight(self):
        for _e in self.edge_mapper.values():
            _e.weight_c = _e.weight

    def recover_weight(self):
        for _e in self.edge_mapper.values():
            _e.weight = _e.weight_c

    def route_flows(self, flows: List[int], is_sort: bool = True):
        if is_sort is True:
            flows = self.sort_flows(flows)
        for fid in flows:
            self.save_weight()
            if not self.route_single_flow(self.flow_mapper[fid]):
                self.recover_weight()
                self.failure_queue.add(fid)
                logger.info('routing failure ,and add flow [' + str(fid) + '] into failure queue')
            else:
                logger.info(self.flow_mapper[fid].to_string())
        logger.info('FAILURE QUEUE:' + str(self.failure_queue))

    def route_flows_incrementally(self, flows: List[int]):
        self.route_flows(flows)

    def route_all_flows(self):
        self.route_flows(self.flows)

    def route_single_flow(self, flow: Flow) -> bool:
        _b: float = flow.size / flow.period
        if self.route_one2many(flow.flow_id, flow.source, flow.destinations, _b):
            logger.info('routing for flow [' + str(flow.flow_id) + '] succeed')
            return True
        else:
            logger.info('routing for flow [' + str(flow.flow_id) + '] failure')
            return False

    def route_one2many(self, fid: int, src: int, dest: List[int], b: float) -> bool:
        _routes: List[List[List[int]]] = []  # routes set for one-to-many
        _walked_edges: Set[int] = set()  # walked edges set
        # if not all are successful ,then return False
        for _d in dest:
            __routes: List[List[int]] = []  # routes set for one-to-one
            while not self.check_reliability(__routes):
                _route: List[int] = self.route_one2one(fid, src, _d, b, _walked_edges)  # route for one-to-one
                if len(_route) != 0:
                    __routes.append(_route)
                    for _eid in _route:
                        self.flow_mapper[fid].negative_walked_edges.add(_eid)  # add walked edge to negative walked set
                else:
                    return False  # there is no path left
            __routes = self.find_all_e2e_routes(src, _d, __routes)  # extend routes set for one-to-one
            _routes.append(__routes)  # add one-to-one routes set to one-to-many routes set
            self.flow_mapper[fid].negative_walked_edges = set()  # recover negative walked set
            # TODO set redundancy degree for source-destination pair
        self.flow_mapper[fid].routes = _routes  # assign routes to flow
        # if all are successful, then add walked edge to walked edges set
        for _d_routes in _routes:
            for _route in _d_routes:
                for _eid in _route:
                    self.flow_mapper[fid].walked_edges.add(_eid)
        return True

    def route_one2one(self, fid: int, src: int, dest: int, b: float, walked_edges: Set[int]) -> List[int]:
        # get source edge
        src_node: Node = self.node_mapper[src]
        src_edge: Edge = src_node.out_edge[0]  # source node has only one outbound edge
        # get destination edge
        dest_node: Node = self.node_mapper[dest]
        dest_edge: Edge = dest_node.in_edge[0]  # destination node has only one inbound edge
        # weight list of all edges
        weight: List[List[int]] = []  # final weight
        # back tracing to find a end-to-end route
        route: List[List[int]] = []  # final route
        _route: List[int] = []  # back-tracing stack
        self.back_trace(fid, route, _route, src_edge.edge_id, 0, dest_edge.edge_id, b, weight, walked_edges)
        # recover node color
        for _nid in self.nodes:
            _n: Node = self.node_mapper[_nid]
            _n.color = 0
        # update edge weight
        if len(weight) != 0:
            for _i, _w in enumerate(weight[0]):
                self.edge_mapper[_i + 1].weight = _w
        if len(route) != 0:
            # update walked edges
            for _eid in route[0]:
                walked_edges.add(_eid)
            return route[0]
        else:
            return []

    def back_trace(self, fid: int, route: List[List[int]], _route: List[int], eid: int, n: int, dest_e: int, b: float,
                   weight: List[List[int]], walked_edges: Set[int]):
        _e: Edge = self.edge_mapper[eid]
        _w = b / _e.bandwidth
        if _e.weight + _w > 1:
            return False
        if eid in walked_edges:
            if self.overlapped is False:
                _e.weight += _w  # add weight on edge
        else:
            _e.weight += _w  # add weight on edge
        _in: Node = _e.in_node
        _in.color = 1  # set inbound node color to 1
        _route.append(eid)  # append edge to route

        if eid == dest_e:
            #  set final route
            route.append(_route[:])  # deep copy here!
            #  set final weight
            _weight: List[int] = [0] * len(self.edges)
            for _eid, _e in self.edge_mapper.items():
                _weight[_eid - 1] = _e.weight
            weight.append(_weight)
            return True
        else:
            _E: List[Edge] = self.get_feasible_edges(eid, b)  # get feasible edges
            _E: List[Edge] = self.sort_edges(_E, fid)  # sorting operation without side effect
            for __e in _E:
                self.back_trace(fid, route, _route, __e.edge_id, n + 1, dest_e, b, weight, walked_edges)
                if len(route) != 0:
                    break
            if eid in walked_edges:
                if self.overlapped is False:
                    _e.weight -= _w  # recover weight on edge
            else:
                _e.weight -= _w  # recover weight on edge
            _route.pop()  # recover route

    def get_feasible_edges(self, edge_id: int, b: float) -> List[Edge]:
        '''
        get feasible outbound edges
        :param edge_id: inbound edge id
        :param b: bandwidth requirement of flow
        :return: List[Edge]
        '''
        _e: Edge = self.edge_mapper[edge_id]
        _on: Node = _e.out_node
        _E: List[
            Edge] = _on.out_edge.copy()  # deep copy here! otherwise, remove operation will delete outbound edge on node
        __E: List[Edge] = []
        for _i in range(_on.out_edge_num):
            _e: Edge = _E.pop()
            _on: Node = _e.out_node
            _w: float = _e.weight
            _b: int = _e.bandwidth
            # check whether the next node's color is red or bandwidth overflow
            if _on.color != 1:  # TODO check end-to-end delay
                if self.overlapped is True:
                    if _w + b / _b > 1:
                        continue
                __E.append(_e)
                continue
        return __E

    def sort_edges(self, edges: List[Edge], fid: int) -> List[Edge]:
        '''
        sort edges list by priority from <walked-edges> to <load> to <negative-walked-edge> [NOTED]
        :param edges: edges list to sort
        :param fid: flow id
        :return: sorted edges list
        '''
        # preference: walked > load > negative walked
        _f: Flow = self.flow_mapper[fid]
        edges: List[Edge] = sorted(edges, key=(lambda _e: _e.weight), reverse=False)  # sort from smallest to biggest
        _j: int = 0  # index
        _k: int = 0  # insert position of walked edge
        for _i in range(len(edges)):
            _e: Edge = edges[_j]
            # move walked edge to head
            if _e.edge_id in _f.walked_edges and _e.edge_id not in _f.negative_walked_edges:
                edges.remove(_e)
                edges.insert(_k, _e)
                _k += 1
                _j += 1
            # move negative walked edge to tail
            elif _e.edge_id in _f.negative_walked_edges:
                edges.remove(_e)
                edges.append(_e)
            # or do nothing just add index
            else:
                _j += 1
        return edges

    def check_reliability(self, routes: List[int]) -> bool:
        # TODO map directed graph to undirected graph
        # TODO enumerate all network state
        # TODO filter feasible state
        # TODO compute reliability

        if len(routes) == 2:
            return True
        return False

    def find_all_e2e_routes(self, src: int, dest: int, routes: List[List[int]]):
        # TODO extend routes set
        _all_edges: Set[int] = set()
        for _route in routes:
            for _eid in _route:
                _all_edges.add(_eid)
        _routes: List[List[int]] = []
        _route: List[int] = [self.node_mapper[src].out_edge[0].edge_id]
        self.search_dest(_all_edges, dest, _route, _routes)
        return _routes

    def search_dest(self, edges: List[int], dest: int, _route: List[int], routes: List[List[int]]):
        if self.edge_mapper[_route[-1]].out_node.node_id == dest:
            #  set final route
            routes.append(_route[:])  # deep copy here!
        else:
            _e: Edge = self.edge_mapper[_route[-1]]
            _in: Node = _e.in_node
            _in.color = 1  # colour outbound node to red
            _on: Node = _e.out_node
            _E: List[Edge] = _on.out_edge.copy()  # deep copy here
            _E = list(filter(lambda e: e.edge_id in edges, _E))  # filter edges not included in edges set
            _E = list(filter(lambda e: e.out_node.color == 0, _E))  # filter red node
            for _e in _E:
                _route.append(_e.edge_id)
                self.search_dest(edges, dest, _route, routes)
            _in.color = 0  # recover the color of outbound node
        _route.pop()
