from typing import List

from src.net_envs.network_component.Mac import MAC_TYPE
from src.type import PortNo, MacAddress


class FilteringDatabaseItem:
    mac: MacAddress  # destination mac address
    mac_type: MAC_TYPE  # mac address type
    ports: List[PortNo]  # outbound ports

    def __init__(self, mac: MacAddress, ports: List[PortNo], mac_type: MAC_TYPE = MAC_TYPE.MULTICAST):
        self.mac = mac
        self.mac_type = mac_type
        self.ports = ports


class FilteringDatabase:
    static: bool  # static forward
    items: List[FilteringDatabaseItem]  # filtering database item

    def __init__(self, items: List[FilteringDatabaseItem] = None, static: bool = True):
        self.static = static
        self.items = items or []

    def add_item(self, item: FilteringDatabaseItem):
        self.items.append(item)

    def product_and_add_item(self, mac: MacAddress, ports: List[PortNo], mac_type: MAC_TYPE):
        item: FilteringDatabaseItem = FilteringDatabaseItem(mac, ports, mac_type)
        self.items.append(item)
