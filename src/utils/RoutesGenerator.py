from typing import List, Dict

from src.graph.Flow import Flow
from src.graph.Graph import Graph
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
    src_node: int
    src_edge: int
    src_mac: str
    dest_node: int
    dest_edge: int
    dest_mac: str
    node_route: List[int]  # [n1, n2, ...]
    edge_route: List[int]  # [e1, e2, ...]
    mac_route: List[str]  # [mac1, mac2, ...]

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
    src_node: int
    dest_node: int
    redundant_degree: int
    redundant_routes: List[OneToOneRoute]

    def __init__(self, src_node: int, dest_node: int, redundant_routes: List[OneToOneRoute]):
        self.src_node = src_node
        self.dest_node = dest_node
        self.redundant_routes = redundant_routes
        self.redundant_degree = len(self.redundant_routes)


class FlowRoutes:
    flow_id: int
    src_node: int
    dest_node: List[int]
    flow_routes: Dict[int, OneToOneRedundantRoutes]

    def __init__(self, flow_id: int, src_node: int, dest_nodes: List[int], flow_routes: Dict[int, OneToOneRedundantRoutes]):
        self.flow_id = flow_id
        self.src_node = src_node
        self.dest_node = dest_nodes
        self.flow_routes = flow_routes


class RoutesGenerator:
    @staticmethod
    def generate_routes_immediate_entity(graph: Graph, flow_list: List[Flow], edge_mac_dict: Dict[int, EdgeMacMapper]):
        flow_routes_list: List[FlowRoutes] = []
        for flow in flow_list:
            flow_id: int = flow.flow_id
            src_node_id: int = flow.source
            dest_node_id_list: List[int] = flow.destinations
            one_to_many_redundant_routes: List[List[List[int]]] = flow.routes
            flow_routes: Dict[int, OneToOneRedundantRoutes] = {}
            for i, one_to_one_redundant_routes in enumerate(one_to_many_redundant_routes):
                dest_node_id: int = dest_node_id_list[i]
                redundant_routes: List[OneToOneRoute] = []
                for j, one_to_one_route in enumerate(one_to_one_redundant_routes):
                    src_edge_id: int = one_to_one_route[0]
                    src_mac: str = edge_mac_dict[src_edge_id].mac_pair[0]
                    src_triple: GenTriple = GenTriple(src_node_id, src_edge_id, src_mac)
                    dest_edge_id: int = one_to_one_route[-1]
                    dest_mac: str = edge_mac_dict[dest_edge_id].mac_pair[1]
                    dest_triple: GenTriple = GenTriple(dest_node_id, dest_edge_id, dest_mac)
                    node_routes: List[int] = [graph.edge_mapper[one_to_one_route[0]].in_node.node_id]
                    edge_routes: List[int] = one_to_one_route
                    mac_routes: List[int] = [edge_mac_dict[one_to_one_route[0]].mac_pair[0]]
                    for eid in one_to_one_route:
                        node2_id: int = graph.edge_mapper[eid].out_node.node_id
                        node_routes.append(node2_id)
                        mac2: str = edge_mac_dict[eid].mac_pair[1]
                        mac_routes.append(mac2)
                    route_triple: GenTriple = GenTriple(node_routes, edge_routes, mac_routes)
                    single_route_instance: OneToOneRoute = OneToOneRoute(src_triple, dest_triple, route_triple)
                    redundant_routes.append(single_route_instance)
                redundant_route_instance: OneToOneRedundantRoutes = \
                    OneToOneRedundantRoutes(src_node_id, dest_node_id, redundant_routes)
                flow_routes[dest_node_id] = redundant_route_instance
            flow_routes_instance: FlowRoutes = FlowRoutes(flow_id, src_node_id, dest_node_id_list, flow_routes)
            flow_routes_list.append(flow_routes_instance)
        return flow_routes_list

    @staticmethod
    def serialize_to_json():
        pass

    @staticmethod
    def serialize_to_xml():
        pass
