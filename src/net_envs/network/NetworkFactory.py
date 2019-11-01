import abc
import os
import pickle
from typing import List, Dict

from src.graph.Graph import Graph
from src.graph.Solver import Solution
from src.net_envs.network.Network import Network
from src.net_envs.network.NetworkFactoryInterface import NetworkFactoryInterface
from src.net_envs.network_element.NetworkDevice import NetworkDevice
from src.net_envs.network_element.NetworkDeviceFactory import NetworkDeviceFactory
from src.type import MacAddress, EdgeId, NodeId, FlowId
import src.utils.MacAddressGenerator as MAG
from src.utils.Singleton import SingletonABC


class NetworkFactory(NetworkFactoryInterface, metaclass=SingletonABC):
    solution: Solution
    node_edge_mac_info: MAG.NodeEdgeMacInfo

    def get_solution(self):
        file = os.path.join(os.path.join(os.path.abspath('.'), 'json'), 'solution')  # TODO fix hard code
        with open(file, 'rb') as f:
            self.solution: Solution = pickle.load(f)

    def parse_node_edge_mac_info(self, solution: Solution):
        # get mac-list, edge-mac-dict and node-mac-dict
        mac_list: List[MacAddress] = MAG.MacAddressGenerator.generate_all_multicast_mac_address(solution.graph)
        group_mac_list: List[MacAddress] = MAG.MacAddressGenerator.generate_flow_group_mac_address(solution.flows)
        edge_mac_dict: Dict[EdgeId, MAG.EdgeMacMapper] = \
            MAG.MacAddressGenerator.assign_mac_address_to_edge(mac_list, solution.graph)
        node_mac_dict: Dict[NodeId, MAG.NodeMacMapper] = \
            MAG.MacAddressGenerator.assign_mac_address_to_node(edge_mac_dict)
        flow_mac_dict: Dict[FlowId, MAG.FlowMacMapper] = \
            MAG.MacAddressGenerator.assign_mac_address_to_flow(group_mac_list, solution.flows)

        # use node-edge-mac-info builder to build node-edge-mac-info
        node_edge_mac_info_builder: MAG.NodeEdgeMacInfoBuilder = MAG.NodeEdgeMacInfoBuilder()
        node_edge_mac_info_builder.add_mac_list(mac_list)
        node_edge_mac_info_builder.add_group_mac_list(group_mac_list)
        node_edge_mac_info_builder.add_edge_mac_dict(edge_mac_dict)
        node_edge_mac_info_builder.add_node_mac_dict(node_mac_dict)
        node_edge_mac_info_builder.add_flow_mac_dict(flow_mac_dict)
        self.node_edge_mac_info: MAG.NodeEdgeMacInfo = node_edge_mac_info_builder.build()

    def product(self, *args, **kwargs) -> Network:
        # initialize empty network
        network: Network = Network()

        # get solution which contains graph and flows
        self.get_solution()

        # parse node-edge-mac-info
        self.parse_node_edge_mac_info(self.solution)

        # get node-id-list
        node_id_list: List[NodeId] = [node_id for node_id in self.node_edge_mac_info.node_mac_dict.keys()]

        # product network devices and add them into network
        network_device_list: List[NetworkDevice] = []
        network_device_factory: NetworkDeviceFactory = NetworkDeviceFactory()  # factory singleton
        for network_device_id in node_id_list:
            network_device: NetworkDevice = network_device_factory.product(network_device_id)
            network_device_list.append(network_device)
        network.add_network_devices(network_device_list)

        # TODO add channels
        # p