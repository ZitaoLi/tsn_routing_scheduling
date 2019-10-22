from typing import List, Tuple, Dict

import jsonpickle

from src.graph.Graph import Graph


class EdgeMacMapper:
    edge_id: int
    node_pair: Tuple[int, int]  # (node1, node2)
    mac_pair: Tuple[str, str]  # (mac1, mac2)

    def __init__(self, edge_id: int, node_mac_p1: Tuple[int, str], node_mac_p2: Tuple[int, str]):
        self.edge_id = edge_id
        self.node_pair = (node_mac_p1[0], node_mac_p2[0])
        self.mac_pair = (node_mac_p1[1], node_mac_p2[1])

    def __repr__(self):
        return jsonpickle.encode(self)


class NodeMacMapper:
    node_id: int
    port_list: List[int]  # [port1, port2, ...]
    mac_list: List[str]  # [mac1, mac2, ...]
    port_mac_pair_list: [Tuple[int, int]]  # [(port1, mac1), (port2, mac2), ...]

    def __init__(self, node_id: int):
        self.node_id = node_id
        self.port_list = []
        self.mac_list = []
        self.port_mac_pair_list = []

    def __repr__(self):
        return jsonpickle.encode(self)

    def add_port(self, port_id: int, mac: str):
        self.port_list.append(port_id)
        self.mac_list.append(mac)
        self.port_mac_pair_list.append((port_id, mac))


class MacAddressGenerator:
    mac_addr_list: List[str]  # [mac1, ...]
    edge_mac_dict: Dict[int, EdgeMacMapper]  # {e1: EdgeMacMapper, ...}
    node_mac_dict: Dict[int, NodeMacMapper]  # {n1: NodeMacMapper, ...}

    @classmethod
    def generate_all_multicast_mac_address(cls, g: Graph):
        _mac_addr_list: List[str] = list()
        _edge_num: int = g.get_edge_num()
        _mac_num: int = _edge_num * 2
        if _mac_num > 1099511627775 - 2:
            # TODO overflow error
            return
        for i in range(1, _mac_num + 1):
            _mac_addr_list.append(MacAddressGenerator.generate_multicast_mac_address(i))
        cls.mac_addr_list = _mac_addr_list.copy()
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

    @classmethod
    def assign_mac_address_to_edge(cls, macs: List[str], g: Graph) -> Dict[int, EdgeMacMapper]:
        _edge_mac_dict: Dict[int, EdgeMacMapper] = dict()
        _i = 0
        for _eid, _e in g.edge_mapper.items():
            _node1: int = _e.in_node.node_id
            _node2: int = _e.out_node.node_id
            _reversed_edge: Tuple[int, int] = (_node2, _node1)
            _d: Dict[int, EdgeMacMapper] = \
                {_k: _v for _k, _v in _edge_mac_dict.items() if _v.node_pair == _reversed_edge}
            if len(_d) != 0:
                _edge_mac_mapper: EdgeMacMapper = list(_d.values())[0]
                _mac1: str = _edge_mac_mapper.mac_pair[0]
                _mac2: str = _edge_mac_mapper.mac_pair[1]
                _edge_mac_mapper: EdgeMacMapper = EdgeMacMapper(_eid, (_node1, _mac2), (_node2, _mac1))
                _edge_mac_dict[_eid] = _edge_mac_mapper
            else:
                _mac1: str = macs[_i]
                _mac2: str = macs[_i + 1]
                _i += 2
                _edge_mac_mapper: EdgeMacMapper = EdgeMacMapper(_eid, (_node1, _mac1), (_node2, _mac2))
                _edge_mac_dict[_eid] = _edge_mac_mapper
        cls.edge_mac_dict = _edge_mac_dict.copy()
        return _edge_mac_dict

    @classmethod
    def assign_mac_address_to_node(cls, edge_mac_dict: Dict[int, EdgeMacMapper]) -> Dict[int, NodeMacMapper]:
        _node_mac_dict: Dict[int, NodeMacMapper] = dict()
        for _edge_mac_mapper in edge_mac_dict.values():
            _node1: int = _edge_mac_mapper.node_pair[0]
            _node2: int = _edge_mac_mapper.node_pair[1]
            _mac1: str = _edge_mac_mapper.mac_pair[0]
            _mac2: str = _edge_mac_mapper.mac_pair[1]
            _node_mac_pair1: Tuple[int, str] = (_node1, _mac1)
            _node_mac_pair2: Tuple[int, str] = (_node2, _mac2)
            _pairs: List[Tuple[int, str]] = [_node_mac_pair1, _node_mac_pair2]
            for _p in _pairs:
                if _p[0] not in _node_mac_dict.keys():
                    _node_mac_mapper: NodeMacMapper = NodeMacMapper(_p[0])
                    _node_mac_mapper.add_port(1, _p[1])
                    _node_mac_dict[_p[0]] = _node_mac_mapper
                elif _p[1] not in _node_mac_dict[_p[0]].mac_list:
                    _node_mac_mapper: NodeMacMapper = _node_mac_dict[_p[0]]
                    _node_mac_mapper.add_port(_node_mac_mapper.port_list.__len__() + 1, _p[1])
        return _node_mac_dict


















