from typing import List, Tuple, Dict
from src import config
from src.graph.Graph import Graph
from src.net_envs.network_component.Mac import MAC_TYPE
from src.type import EdgeId, NodeId, MacAddress, PortNo
from src.utils.ToString import ToString


class EdgeMacMapper(ToString):
    edge_id: EdgeId
    node_pair: Tuple[NodeId, NodeId]  # (node1, node2)
    mac_pair: Tuple[MacAddress, MacAddress]  # (mac1, mac2)

    def __init__(self, edge_id: EdgeId, node_mac_p1: Tuple[NodeId, MacAddress], node_mac_p2: Tuple[NodeId, MacAddress]):
        self.edge_id = edge_id
        self.node_pair = (node_mac_p1[0], node_mac_p2[0])
        self.mac_pair = (node_mac_p1[1], node_mac_p2[1])


class LinkMacMapper(ToString):
    edge_pair: Tuple[EdgeId]
    node_pair: Tuple[NodeId]
    mac_pair: Tuple[MacAddress]

    def __init__(self, edge_pair: Tuple[EdgeId], node_pair: Tuple[NodeId], mac_pair: Tuple[MacAddress]):
        self.edge_pair = edge_pair
        self.node_pair = node_pair
        self.mac_pair = mac_pair


class NodeMacMapper(ToString):
    node_id: NodeId
    port_list: List[PortNo]  # [port1, port2, ...]
    mac_list: List[MacAddress]  # [mac1, mac2, ...]
    port_mac_pair_list: List[Tuple[PortNo, MacAddress]]  # [(port1, mac1), (port2, mac2), ...]

    def __init__(self, node_id: NodeId):
        self.node_id = node_id
        self.port_list = []
        self.mac_list = []
        self.port_mac_pair_list = []

    def add_port(self, port_no: PortNo, mac: MacAddress):
        self.port_list.append(port_no)
        self.mac_list.append(mac)
        self.port_mac_pair_list.append((port_no, mac))


class NodeEdgeMacInfoBuilder(object):
    mac_list: List[MacAddress]  # [mac1, ...]
    edge_mac_dict: Dict[EdgeId, EdgeMacMapper]  # {e1: EdgeMacMapper, ...}
    node_mac_dict: Dict[NodeId, NodeMacMapper]  # {n1: NodeMacMapper, ...}

    def __init__(self):
        self.mac_list = list()
        self.edge_mac_dict = dict()
        self.node_mac_dict = dict()

    def add_mac_list(self, mac_list: List[MacAddress]):
        [self.mac_list.append(mac) for mac in mac_list]

    def add_edge_mac_dict(self, edge_mac_dict: Dict[EdgeId, EdgeMacMapper]):
        # TODO list comprehension implementation
        self.edge_mac_dict = edge_mac_dict

    def add_node_mac_dict(self, node_mac_dict: Dict[NodeId, NodeMacMapper]):
        # TODO list comprehension implementation
        self.node_mac_dict = node_mac_dict

    def build(self):
        return NodeEdgeMacInfo(self)


class NodeEdgeMacInfo(object):
    mac_list: List[MacAddress]  # [mac1, ...]
    edge_mac_dict: Dict[EdgeId, EdgeMacMapper]  # {e1: EdgeMacMapper, ...}
    node_mac_dict: Dict[NodeId, NodeMacMapper]  # {n1: NodeMacMapper, ...}

    def __init__(self, builder: NodeEdgeMacInfoBuilder):
        self.mac_list = builder.mac_list
        self.edge_mac_dict = builder.edge_mac_dict
        self.node_mac_dict = builder.node_mac_dict


class MacAddressGenerator:

    @staticmethod
    def generate_all_multicast_mac_address(g: Graph):
        _mac_addr_list: List[str] = list()
        _edge_num: int = g.get_edge_num()
        _mac_num: int = _edge_num * 2
        if _mac_num > 1099511627775 - 2:
            # TODO overflow error
            return
        for i in range(1, _mac_num + 1):
            _mac_addr_list.append(MacAddressGenerator.generate_multicast_mac_address(i))
        return _mac_addr_list

    @staticmethod
    def generate_multicast_mac_address(n: int):
        _s: str = hex(n)[2:].upper()  # get hex
        _s: str = _s.zfill(len(_s) + 1 if (len(_s) % 2 == 1) else len(_s))  # fill up 0
        _p: List[str] = list([_s[i:i + 2] for i in range(0, len(_s), 2)])
        if len(_p) > 5:
            # TODO overflow error
            return
        _mac: str = ''
        for i in range(len(_p)):
            _mac = '-' + _p[-1 - i]
        for i in range(5 - len(_p)):
            _mac = '-00' + _mac
        _mac = '01' + _mac  # multicast prefix
        return _mac

    @staticmethod
    def assign_mac_address_to_edge(macs: List[MacAddress], g: Graph) -> Dict[EdgeId, EdgeMacMapper]:
        _edge_mac_dict: Dict[EdgeId, EdgeMacMapper] = dict()
        _i = 0
        for _eid, _e in g.edge_mapper.items():
            _node1: NodeId = _e.in_node.node_id
            _node2: NodeId = _e.out_node.node_id
            _reversed_edge: Tuple[NodeId, NodeId] = (_node2, _node1)
            _d: Dict[NodeId, EdgeMacMapper] = \
                {_k: _v for _k, _v in _edge_mac_dict.items() if _v.node_pair == _reversed_edge}
            if len(_d) != 0:
                _edge_mac_mapper: EdgeMacMapper = list(_d.values())[0]
                _mac1: MacAddress = _edge_mac_mapper.mac_pair[0]
                _mac2: MacAddress = _edge_mac_mapper.mac_pair[1]
                _edge_mac_mapper: EdgeMacMapper = EdgeMacMapper(_eid, (_node1, _mac2), (_node2, _mac1))
                _edge_mac_dict[_eid] = _edge_mac_mapper
            else:
                _mac1: MacAddress = macs[_i]
                _mac2: MacAddress = macs[_i + 1]
                _i += 2
                _edge_mac_mapper: EdgeMacMapper = EdgeMacMapper(_eid, (_node1, _mac1), (_node2, _mac2))
                _edge_mac_dict[_eid] = _edge_mac_mapper
        return _edge_mac_dict

    @staticmethod
    def assign_mac_address_to_node(edge_mac_dict: Dict[EdgeId, EdgeMacMapper]) -> Dict[NodeId, NodeMacMapper]:
        _node_mac_dict: Dict[NodeId, NodeMacMapper] = dict()
        for _edge_mac_mapper in edge_mac_dict.values():
            _node1: NodeId = _edge_mac_mapper.node_pair[0]
            _node2: NodeId = _edge_mac_mapper.node_pair[1]
            _mac1: MacAddress = _edge_mac_mapper.mac_pair[0]
            _mac2: MacAddress = _edge_mac_mapper.mac_pair[1]
            _node_mac_pair1: Tuple[NodeId, MacAddress] = (_node1, _mac1)
            _node_mac_pair2: Tuple[NodeId, MacAddress] = (_node2, _mac2)
            _pairs: List[Tuple[NodeId, MacAddress]] = [_node_mac_pair1, _node_mac_pair2]
            for _p in _pairs:
                if _p[0] not in _node_mac_dict.keys():
                    _node_mac_mapper: NodeMacMapper = NodeMacMapper(_p[0])
                    _node_mac_mapper.add_port(1, _p[1])
                    _node_mac_dict[_p[0]] = _node_mac_mapper
                elif _p[1] not in _node_mac_dict[_p[0]].mac_list:
                    _node_mac_mapper: NodeMacMapper = _node_mac_dict[_p[0]]
                    _node_mac_mapper.add_port(PortNo(_node_mac_mapper.port_list.__len__() + 1), _p[1])
        return _node_mac_dict

    @staticmethod
    def assign_mac_address_to_link(edge_mac_dict: Dict[EdgeId, EdgeMacMapper]) -> List[LinkMacMapper]:
        # TODO
        pass

    @staticmethod
    def parse_mac_type(mac: MacAddress):
        # TODO
        return MAC_TYPE.MULTICAST if config.XML_CONFIG['multicast-model'] is True else MAC_TYPE.UNICAST
