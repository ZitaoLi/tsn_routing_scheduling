from enum import Enum
from typing import List

from src.net_elem.Mac import MAC_TYPE
from src.net_elem.NetworkConfigurator import NetworkConfigurator
from src.type import MacAddress, PortNo, NodeId, NodeName


class Port(object):
    port_id: PortNo
    mac: MacAddress
    mac_type: MAC_TYPE

    def __init__(self, port_id: PortNo, mac: MacAddress, mac_type: MAC_TYPE):
        self.port_id = port_id
        self.mac = mac
        self.mac_type = mac_type


class NetworkDevice(object):
    device_id: NodeId
    device_name: NodeName
    ports: List[Port]

    def __init__(self, device_id: NodeId, device_name: NodeName):
        self.device_id = device_id
        self.device_name = device_name
        self.ports = []

    def add_port(self, mac: MacAddress, mac_type: MAC_TYPE):
        port: Port = Port(PortNo(self.ports.__len__() + 1), mac, mac_type)
        self.ports.append(port)

    def accept_configurator(self, configurator: NetworkConfigurator):
        configurator.configure(self)  # inject network configurator
