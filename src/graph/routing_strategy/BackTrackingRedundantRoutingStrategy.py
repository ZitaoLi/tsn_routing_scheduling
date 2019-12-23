import logging
from typing import List, Dict, Set

from src import config
from src.graph.Edge import Edge
from src.graph.Flow import Flow
from src.graph.Node import Node
from src.graph.routing_strategy.RedundantRoutingStrategy import RedundantRoutingStrategy
from src.graph.routing_strategy.RoutingStrategy import RoutingStrategy
from src.type import FlowId, EdgeId

logger = logging.getLogger(__name__)


class BackTrackingRedundantRoutingStrategy(RedundantRoutingStrategy):
    __overlapped: bool
    __flow_walked_edges: Dict[int, Set[int]]

    def __init__(self, nodes: List[int], edges: List[int], flows: List[int], node_mapper: Dict[int, Node],
                 edge_mapper: Dict[int, Edge], flow_mapper: Dict[int, Flow]):
        super().__init__(nodes, edges, flows, node_mapper, edge_mapper, flow_mapper)
        self.__overlapped = False
        self.__flow_walked_edges = dict()
        for _fid in self.flows:
            self.__flow_walked_edges[_fid] = set()

    def route(self, flow_id_list: List[FlowId], *args, **kwargs) -> Set[FlowId]:
        sorting_enabled: bool = True
        if 'sorting_enabled' in kwargs.keys():
            sorting_enabled = kwargs['sorting_enabled']
            assert type(sorting_enabled) is bool, 'parameter "sorting_enabled" type must be bool'
        if sorting_enabled:
            flow_id_list = self.sort_flows_id_list(flow_id_list)
        for fid in flow_id_list:
            self.save_weight()
            if not self.route_single_flow(self.flow_mapper[fid]):
                self.recover_weight()
                self.failure_queue.add(fid)
                logger.info('routing failure ,and add flow [' + str(fid) + '] into failure queue')
            else:
                logger.info(self.flow_mapper[fid].to_string())
        logger.info('FAILURE QUEUE:' + str(self.failure_queue))
        return self.failure_queue

    @property
    def overlapped(self):
        return self.__overlapped

    @overlapped.setter
    def overlapped(self, overlapped: bool):
        self.__overlapped = overlapped

    def save_weight(self):
        for _e in self.edge_mapper.values():
            _e.weight_c = _e.weight

    def recover_weight(self):
        for _e in self.edge_mapper.values():
            _e.weight = _e.weight_c

    def route_single_flow(self, flow: Flow) -> bool:
        _b: float = flow.size / flow.period
        if self.route_one2many(flow.flow_id, flow.source, flow.destinations, _b,
                               size=flow.size, deadline=flow.deadline):
            logger.info('routing for flow [' + str(flow.flow_id) + '] succeed')
            return True
        else:
            logger.info('routing for flow [' + str(flow.flow_id) + '] failure')
            return False

    def route_one2many(self, fid: int, src: int, dest: List[int], b: float,
                       size: int = 0, deadline: int = 0) -> bool:
        _routes: List[List[List[int]]] = []  # routes set for one-to-many
        _walked_edges: Set[int] = set()  # walked edges set
        # if not all are successful ,then return False
        for _d in dest:
            __routes: List[List[int]] = []  # routes set for one-to-one
            while not self.check_e2e_reliability(__routes, src, _d, fid=fid):
                _route: List[int] = self.route_one2one(fid, src, _d, b, _walked_edges,
                                                       size=size, deadline=deadline)  # route for one-to-one
                if len(_route) != 0 and _route is not None:
                    __routes.append(_route)
                    for _eid in _route:
                        self.flow_mapper[fid].negative_walked_edges.add(_eid)  # add walked edge to negative walked set
                else:
                    self.flow_mapper[fid].routes_reliability = dict()  # recover routes_reliability
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

    def route_one2one(self, fid: int, src: int, dest: int, b: float, walked_edges: Set[int],
                      size: int = 0, deadline: int = 0) -> List[int]:
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
        _hops: int = self.compute_hops(link_bandwidth=config.GRAPH_CONFIG['all-bandwidth'],
                                       flow_size=size, flow_deadline=deadline)  # hops of routes
        self.back_trace(
            fid, route, _route, src_edge.edge_id, 0, dest_edge.edge_id, b, weight, walked_edges, hops=_hops, hop=1)
        # recover node color
        for _nid in self.nodes:
            _n: Node = self.node_mapper[_nid]
            _n.color = 0
        # update edge weight
        if len(weight) != 0:
            for _i, _w in enumerate(weight[0]):
                self.edge_mapper[_i + 1].weight = _w
        if len(route) != 0:
            # check walked edges
            flag: bool = False
            for eid in route[0]:
                if eid not in self.flow_mapper[fid].negative_walked_edges:
                    flag = True
                    break
            if flag is False:
                logging.info('there is no more end-to-end to search')
                return []
            # update walked edges
            for _eid in route[0]:
                walked_edges.add(_eid)
            return route[0]
        else:
            return []

    def compute_hops(self, link_bandwidth: float = 0, flow_size: int = 0, flow_deadline: int = 0) -> int:
        import math
        if link_bandwidth is not None or link_bandwidth != 0:
            if flow_size is not Node or flow_size != 0:
                if flow_deadline is not None or flow_deadline != 0:
                    hops: int = math.ceil(flow_deadline / (flow_size / link_bandwidth))
                    if hops < config.FLOW_CONFIG['max-hops']:
                        return hops
        return config.FLOW_CONFIG['max-hops']  # max hops

    def back_trace(self, fid: int, route: List[List[int]], _route: List[int], eid: int, n: int, dest_e: int, b: float,
                   weight: List[List[int]], walked_edges: Set[int], hops: int = 0, hop: int = 0):
        _e: Edge = self.edge_mapper[eid]
        _w = b / _e.bandwidth
        # if _e.weight + _w > 1:  # check bandwidth
        #     return False
        # # check bandwidth
        # if eid in walked_edges:
        #     if config.GRAPH_CONFIG['overlapped-routing'] is False:
        #         if _e.weight + _w > 1:  # check bandwidth
        #             logger.info('walked edge [{}] out of bandwidth'.format(_e.edge_id))
        #             return False
        #         _e.weight += _w  # add weight on edge
        # else:
        #     if _e.weight + _w > 1:  # check bandwidth
        #         logger.info('non-walked edge [{}] out of bandwidth'.format(_e.edge_id))
        #         return False
        #     _e.weight += _w  # add weight on edge

        _in: Node = _e.in_node
        _in.color = 1  # set inbound node color to 1
        _route.append(eid)  # append edge to route

        # # check walked edges
        # flag: bool = False
        # for eid in _route:
        #     if eid not in self.flow_mapper[fid].negative_walked_edges:
        #         flag = True
        #         break
        # if flag is False:
        #     logging.info('"backtracking" there is no more end-to-end routes to search')

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
            _E: List[Edge] = \
                self.get_feasible_edges(eid, b, hop=hop, hops=hops, walked_edges=walked_edges)  # get feasible edges
            _E: List[Edge] = self.sort_edges(_E, fid)  # sorting operation without side effect
            for __e in _E:
                self.back_trace(
                    fid, route, _route, __e.edge_id, n + 1, dest_e, b, weight, walked_edges, hops=hops, hop=hop+1)
                if len(route) != 0:
                    break
            if eid in walked_edges:
                if config.GRAPH_CONFIG['overlapped-routing'] is False:
                    _e.weight -= _w  # recover weight on edge
            else:
                _e.weight -= _w  # recover weight on edge
            _route.pop()  # recover route

    def get_feasible_edges(
            self, edge_id: int, b: float, hop: int = 0, hops: int = 0, walked_edges: Set[int] = None) -> List[Edge]:
        '''
        get feasible outbound edges
        :param walked_edges:
        :param hops:
        :param hop:
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
            _b: float = _e.bandwidth
            # check whether the next node's color is red or bandwidth overflow
            # if _on.color != 1:  # TODO check end-to-end delay
            if self.check(edge=_e, bandwidth=b, hop=hop, hops=hops, walked_edges=walked_edges):
                if self.__overlapped is True:
                    if _w + b / _b > 1:
                        continue
                __E.append(_e)
                continue
        return __E

    def check(self, **kwargs) -> bool:
        '''
        check next edge
        :param kwargs:
        :return:
        '''
        if 'edge' not in kwargs.keys():
            raise RuntimeError('miss parameter "edge: Edge"')
        if 'bandwidth' not in kwargs.keys():
            raise RuntimeError('miss parameter "bandwidth: float"')
        if 'hop' not in kwargs.keys():
            raise RuntimeError('miss parameter "hop: int"')
        if 'hops' not in kwargs.keys():
            raise RuntimeError('miss parameter "hops: int"')
        if 'walked_edges' not in kwargs.keys():
            raise RuntimeError('miss parameter "walked_edges: Set(EdgeId)"')
        edge: Edge = kwargs['edge']
        if edge.out_node.color == 1:
            # logger.info('unavailable node [{}]'.format(edge.out_node.node_id))
            return False  # unavailable node
        hops: int = kwargs['hops']
        hop: int = kwargs['hop']
        if hops < hop + 1 or hops == 0:
            logger.info('edge [{}] out of hops "{}"'.format(edge.edge_id, hops))
            return False  # out of hops constraint
        walked_edge: Set[EdgeId] = kwargs['walked_edges']
        bandwidth: float = kwargs['bandwidth']
        appending_weight: float = bandwidth / edge.bandwidth
        appended_weight: float = edge.weight + appending_weight
        if edge.edge_id in walked_edge:
            if self.__overlapped is False:
                if appended_weight > 1:
                    logger.info('edge [{}] out of bandwidth'.format(edge.edge_id))
                    return False  # out of bandwidth
        else:
            if appended_weight > 1:
                logger.info('edge [{}] out of bandwidth'.format(edge.edge_id))
                return False  # out of bandwidth
        return True

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

        if len(routes) == config.FLOW_CONFIG['redundancy_degree']:
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
