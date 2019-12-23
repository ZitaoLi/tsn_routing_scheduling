# network-device-configurator, derived class of network-configurator
import abc

from src.net_envs.network_configurator.NetworkConfigurator import NetworkConfigurator
from src.net_envs.network_element.NetworkDevice import NetworkDevice
import src.utils.MacAddressGenerator as MAG


class NetworkDeviceConfigurator(NetworkConfigurator):
    node_edge_mac_info: MAG.NodeEdgeMacInfo

    def __init__(self, node_edge_mac_info: MAG.NodeEdgeMacInfo):
        self.node_edge_mac_info = node_edge_mac_info

    def configure(self, network_device: NetworkDevice):
        pass
