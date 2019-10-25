import abc
from typing import List, Dict

from src.graph.Graph import Graph
from src.net_elem.Host import Host
from src.net_elem.HostFactory import HostFactory
from src.net_elem.Network import Network, TSNNetwork, EthernetNetwork
from src.net_elem.NetworkDevice import NetworkDevice
from src.net_elem.NetworkDeviceFactory import NetworkDeviceFactory
from src.net_elem.Switch import Switch
from src.net_elem.SwitchFactory import SwitchFactory
from src.type import MacAddress, EdgeId, NodeId
from src.utils.Singleton import SingletonDecorator
import src.utils.MacAddressGenerator as MAG


@SingletonDecorator
class NetworkFactory(object, metaclass=abc.ABCMeta):

    @staticmethod
    def parse_node_edge_mac_info(graph: Graph):
        # get mac-list, edge-mac-dict and node-mac-dict
        mac_list: List[MacAddress] = MAG.MacAddressGenerator.generate_all_multicast_mac_address(graph)
        edge_mac_dict: Dict[EdgeId, MAG.EdgeMacMapper] = \
            MAG.MacAddressGenerator.assign_mac_address_to_edge(mac_list, graph)
        node_mac_dict: Dict[NodeId, MAG.NodeMacMapper] = \
            MAG.MacAddressGenerator.assign_mac_address_to_node(edge_mac_dict)

        # use node-edge-mac-info builder to build node-edge-mac-info
        node_edge_mac_info_builder: MAG.NodeEdgeMacInfoBuilder = MAG.NodeEdgeMacInfoBuilder()
        node_edge_mac_info_builder.add_mac_list(mac_list)
        node_edge_mac_info_builder.add_edge_mac_dict(edge_mac_dict)
        node_edge_mac_info_builder.add_node_mac_dict(node_mac_dict)
        node_edge_mac_info: MAG.NodeEdgeMacInfo = node_edge_mac_info_builder.build()

        return node_edge_mac_info

    @abc.abstractmethod
    def product(self, graph: Graph) -> Network:
        # initialize empty network
        network: Network = Network()

        # parse node-edge-mac-info
        node_edge_mac_info: MAG.NodeEdgeMacInfo = NetworkFactory.parse_node_edge_mac_info(graph)

        # get node-id-list
        node_id_list: List[NodeId] = [node_id for node_id in node_edge_mac_info.node_mac_dict.keys()]

        # product network devices and add them into network
        network_device_list: List[NetworkDevice] = []
        network_device_factory: NetworkDeviceFactory = NetworkDeviceFactory()  # factory singleton
        for network_device_id in node_id_list:
            network_device: NetworkDevice = network_device_factory.product(network_device_id)
            network_device_list.append(network_device)
        network.add_network_devices(network_device_list)

        # TODO add channels
        # product channels and add them into network

        return network


@SingletonDecorator
class EthernetNetworkFactory(NetworkFactory):

    @abc.abstractmethod
    def product(self, graph: Graph) -> EthernetNetwork:  # TODO 这个方法的逻辑需要改，先放着
        # initialize empty network
        network: Network = super().product(graph)
        network.__class__ = EthernetNetwork  # force into EthernetNetwork
        ethernet_network: EthernetNetwork = network

        # parse node-edge-mac-info
        node_edge_mac_info: MAG.NodeEdgeMacInfo = NetworkFactory.parse_node_edge_mac_info(graph)

        # the network device which only has one NIC is host, otherwise switch
        host_id_list: List[NodeId] = [node_id for node_id, node_mac_mapper in node_edge_mac_info.node_mac_dict.items()
                                      if node_mac_mapper.port_list.__len__() == 1]
        switch_id_list: List[NodeId] = [node_id for node_id in node_edge_mac_info.node_mac_dict.keys()
                                        if node_id not in host_id_list]

        # product hosts and add them into network
        host_list: List[Host] = []
        host_factory: HostFactory = HostFactory()  # factory singleton
        for host_id in host_id_list:
            host: Host = host_factory.product(host_id)
            host_list.append(host)
        ethernet_network.add_hosts(host_list)

        # product switches and add them into network
        switch_list: List[Switch] = []
        switch_factory: SwitchFactory = SwitchFactory()  # factory singleton
        for switch_id in switch_id_list:
            switch: Switch = switch_factory.product(switch_id)
            switch_list.append(switch)
        ethernet_network.add_switches(switch_list)

        # TODO configure nodes, such as port addition or filtering datebase addition

        return ethernet_network


@SingletonDecorator
class TSNNetworkFactory(EthernetNetworkFactory):

    @abc.abstractmethod
    def product(self, graph: Graph) -> TSNNetwork:
        # initialize empty network
        ethernet_network: EthernetNetwork = super().product(graph)
        ethernet_network.__class__ = TSNNetwork  # force into EthernetNetwork
        tsn_network: TSNNetwork = ethernet_network

        # parse node-edge-mac-info
        node_edge_mac_info: MAG.NodeEdgeMacInfo = NetworkFactory.parse_node_edge_mac_info(graph)

        # the network device which only has one NIC is host, otherwise switch
        host_id_list: List[NodeId] = [node_id for node_id, node_mac_mapper in node_edge_mac_info.node_mac_dict.items()
                                      if node_mac_mapper.port_list.__len__() == 1]
        switch_id_list: List[NodeId] = [node_id for node_id in node_edge_mac_info.node_mac_dict.keys()
                                        if node_id not in host_id_list]

        # product hosts and add them into network
        host_list: List[Host] = []
        host_factory: HostFactory = HostFactory()  # factory singleton
        for host_id in host_id_list:
            host: Host = host_factory.product(host_id)
            host_list.append(host)
        ethernet_network.add_hosts(host_list)

        # product switches and add them into network
        switch_list: List[Switch] = []
        switch_factory: SwitchFactory = SwitchFactory()  # factory singleton
        for switch_id in switch_id_list:
            switch: Switch = switch_factory.product(switch_id)
            switch_list.append(switch)
        ethernet_network.add_switches(switch_list)

        # TODO configure "enhancement" gate control list

        return tsn_network
