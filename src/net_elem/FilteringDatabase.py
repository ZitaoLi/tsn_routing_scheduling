from typing import List

from src.net_elem.NetworkDevice import MAC_TYPE


class FilteringDatabaseItem:
    mac: str  # destination mac address
    mac_type: MAC_TYPE  # mac address type
    ports: List[int]  # outbound ports

    def __init__(self, mac: str, ports: List[int], mac_type: MAC_TYPE = MAC_TYPE.MULTICAST):
        self.mac = mac
        self.mac_type = mac_type
        self.ports = ports


class FilteringDatabase:
    static: bool  # static forward
    items: List[FilteringDatabaseItem]  # filtering database item

    def __init__(self, items: List[FilteringDatabaseItem] = None, static: bool = True):
        self.static = static
        self.items = items

    def add_item(self, mac: str, ports: List[int], mac_type: MAC_TYPE):
        item: FilteringDatabaseItem = FilteringDatabaseItem(mac, ports, mac_type)
        self.items.append(item)