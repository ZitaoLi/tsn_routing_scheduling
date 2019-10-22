from typing import List, Dict

from src.graph.Graph import Graph
from src.net_elem.Channel import Channel
from src.net_elem.NetworkDevice import NetworkDevice
from src.net_elem.SwitchController import SwitchController
from src.utils import MacAddressGenerator as MAG


class Network(object):
    network_devices: List[NetworkDevice]
    channels: List[Channel]
    switch_controller: SwitchController

    def generate_network_device(self, graph: Graph):
        mac_list: List[str] = MAG.MacAddressGenerator.generate_all_multicast_mac_address(graph)
        edge_mac_dict: Dict[int, MAG.EdgeMacMapper] = \
            MAG.MacAddressGenerator.assign_mac_address_to_edge(mac_list, graph)
        node_mac_dict: Dict[int, MAG.NodeMacMapper] = \
            MAG.MacAddressGenerator.assign_mac_address_to_node(edge_mac_dict)

        # TODO distinguish host node and switch node
        node_id_list: List[int] = [node_id for node_id in node_mac_dict.keys()]



