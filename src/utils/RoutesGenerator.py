import os
from typing import List, Dict

import jsonpickle

from src.graph.Flow import Flow
from src.graph.Graph import Graph
from src.type import FlowId, NodeId, MacAddress, EdgeId
from src.utils.MacAddressGenerator import EdgeMacMapper


class GenTriple:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


class GenTuple:
    def __init__(self, a, b):
        self.a = a
        self.b = b


class OneToOneRoute:
    src_node: NodeId
    src_edge: EdgeId
    src_mac: MacAddress
    dest_node: NodeId
    dest_edge: EdgeId
    dest_mac: MacAddress
    node_route: List[NodeId]  # [n1, n2, ...]
    edge_route: List[EdgeId]  # [e1, e2, ...]
    mac_route: List[MacAddress]  # [mac1, mac2, ...]

    def __init__(self, src_triple: GenTriple, dest_triple: GenTriple, route_triple: GenTriple):
        self.src_node = src_triple.a
        self.src_edge = src_triple.b
        self.src_mac = src_triple.c
        self.dest_node = dest_triple.a
        self.dest_edge = dest_triple.b
        self.dest_mac = dest_triple.c
        self.node_route = route_triple.a
        self.edge_route = route_triple.b
        self.mac_route = route_triple.c


class OneToOneRedundantRoutes:
    src_node: NodeId
    dest_node: NodeId
    redundant_degree: int
    redundant_routes: List[OneToOneRoute]

    def __init__(self, src_node: NodeId, dest_node: NodeId, redundant_routes: List[OneToOneRoute]):
        self.src_node = src_node
        self.dest_node = dest_node
        self.redundant_routes = redundant_routes
        self.redundant_degree = len(self.redundant_routes)


class FlowRoutes:
    flow_id: FlowId
    src_node: NodeId
    dest_node: List[NodeId]
    flow_routes: Dict[NodeId, OneToOneRedundantRoutes]

    def __init__(self, flow_id: FlowId, src_node: NodeId, dest_nodes: List[NodeId],
                 flow_routes: Dict[NodeId, OneToOneRedundantRoutes]):
        self.flow_id = flow_id
        self.src_node = src_node
        self.dest_node = dest_nodes
        self.flow_routes = flow_routes


class RouteImmediateEntity:
    flow_routes_dict: Dict[FlowId, FlowRoutes]
    flow_id_list: List[FlowId]
    edge_mac_dict: Dict[EdgeId, EdgeMacMapper]

    def __init__(self, flow_routes_dict: Dict[FlowId, FlowRoutes], flow_id_list: List[FlowId],
                 edge_mac_dict: Dict[EdgeId, EdgeMacMapper]):
        self.flow_routes_dict = flow_routes_dict
        self.flow_id_list = flow_id_list
        self.edge_mac_dict = edge_mac_dict

    # helper function
    def get_flow_node_route(self, flow_id: FlowId) -> List[List[NodeId]]:
        assert flow_id in self.flow_routes_dict.keys(), "flow id '" + flow_id + "' is not existing"
        _R: List[List[NodeId]] = []
        flow_routes: FlowRoutes = self.flow_routes_dict[flow_id]
        for one_to_one_redundant_routes in flow_routes.flow_routes.values():
            redundant_routes: List[OneToOneRoute] = one_to_one_redundant_routes.redundant_routes
            for one_to_one_route in redundant_routes:
                node_route: List[NodeId] = one_to_one_route.node_route
                _R.append(node_route)
        return _R


class RoutesGenerator:
    @staticmethod
    def generate_routes_immediate_entity(
            graph: Graph, flow_list: List[Flow], edge_mac_dict: Dict[EdgeId, EdgeMacMapper]) -> RouteImmediateEntity:
        '''
        :param graph:
        :param flow_list:
        :param edge_mac_dict:
        :return:
        '''
        flow_routes_dict: Dict[FlowId, FlowRoutes] = {}
        flow_id_list: List[FlowId] = []
        for flow in flow_list:
            flow_id: FlowId = flow.flow_id
            flow_id_list.append(flow_id)
            src_node_id: NodeId = flow.source
            dest_node_id_list: List[NodeId] = flow.destinations
            one_to_many_redundant_routes: List[List[List[NodeId]]] = flow.routes
            flow_routes: Dict[NodeId, OneToOneRedundantRoutes] = {}
            for i, one_to_one_redundant_routes in enumerate(one_to_many_redundant_routes):
                dest_node_id: NodeId = dest_node_id_list[i]
                redundant_routes: List[OneToOneRoute] = []
                for j, one_to_one_route in enumerate(one_to_one_redundant_routes):
                    src_edge_id: EdgeId = one_to_one_route[0]
                    src_mac: MacAddress = edge_mac_dict[src_edge_id].mac_pair[0]
                    src_triple: GenTriple = GenTriple(src_node_id, src_edge_id, src_mac)
                    dest_edge_id: EdgeId = one_to_one_route[-1]
                    dest_mac: MacAddress = edge_mac_dict[dest_edge_id].mac_pair[1]
                    dest_triple: GenTriple = GenTriple(dest_node_id, dest_edge_id, dest_mac)
                    node_routes: List[NodeId] = [graph.edge_mapper[one_to_one_route[0]].in_node.node_id]
                    edge_routes: List[EdgeId] = one_to_one_route
                    mac_routes: List[MacAddress] = [edge_mac_dict[one_to_one_route[0]].mac_pair[0]]
                    for eid in one_to_one_route:
                        node2_id: NodeId = NodeId(graph.edge_mapper[eid].out_node.node_id)
                        node_routes.append(node2_id)
                        mac2: MacAddress = edge_mac_dict[eid].mac_pair[1]
                        mac_routes.append(mac2)
                    route_triple: GenTriple = GenTriple(node_routes, edge_routes, mac_routes)
                    single_route_instance: OneToOneRoute = OneToOneRoute(src_triple, dest_triple, route_triple)
                    redundant_routes.append(single_route_instance)
                redundant_route_instance: OneToOneRedundantRoutes = \
                    OneToOneRedundantRoutes(src_node_id, dest_node_id, redundant_routes)
                flow_routes[dest_node_id] = redundant_route_instance
            flow_routes_instance: FlowRoutes = FlowRoutes(flow_id, src_node_id, dest_node_id_list, flow_routes)
            flow_routes_dict[flow_id] = flow_routes_instance
        route_immediate_entity: RouteImmediateEntity = \
            RouteImmediateEntity(flow_routes_dict, flow_id_list, edge_mac_dict)
        return route_immediate_entity

    @staticmethod
    def serialize_to_json(route_immediate_entity: RouteImmediateEntity) -> str:
        json_str: str = jsonpickle.encode(route_immediate_entity)
        path: str = os.path.join(os.path.join(os.path.abspath('.'), 'json'), 'routes.json')
        with open(path, "w") as f:
            f.write(json_str)
        return json_str

    @staticmethod
    def deserialize_to_obj(json_str: str) -> RouteImmediateEntity:
        if json_str is None or json_str == '':
            path: str = os.path.join(os.path.join(os.path.abspath('.'), 'json'), 'routes.json')
            with open(path, "r") as f:
                json_str: str = f.read()
        return jsonpickle.decode(json_str)

    @staticmethod
    def serialize_to_xml():
        pass
