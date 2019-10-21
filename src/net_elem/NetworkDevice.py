from enum import Enum
from typing import List

MAC_TYPE = Enum('MAC_TYPE', ('UNICAST', 'MULTICAST', 'BROADCAST'))  # unicast multicast and broadcast


class Port(object):
    port_id: int
    mac: str
    mac_type: MAC_TYPE

    def __init__(self, port_id: int, mac: str, mac_type: MAC_TYPE):
        self.port_id = port_id
        self.mac = mac
        self.mac_type = mac_type


class NetworkDevice(object):
    device_id: int
    device_name: str
    ports: List[Port]

    def __init__(self, device_id: int, device_name: str):
        self.device_id = device_id
        self.device_name = device_name
        self.ports = []

    def add_port(self, mac: str, mac_type: MAC_TYPE):
        port: Port = Port(self.ports.__len__() + 1, mac, mac_type)
        self.ports.append(port)
