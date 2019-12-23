from typing import List

from src.net_envs.network.Network import Network
from src.net_envs.network_element.Host import Host
from src.net_envs.network_element.Switch import Switch


class EthernetNetwork(Network):
    switch_list: List[Switch]
    host_list: List[Host]

    def __init__(self):
        super().__init__()
        self.switch_list = []
        self.host_list = []

    def add_hosts(self, host_list: List[Host]):
        if hasattr(self, 'host_list') is False:
            self.host_list = []
        [self.host_list.append(host) for host in host_list]

    def add_switches(self, switch_list: List[Switch]):
        if hasattr(self, 'switch_list') is False:
            self.switch_list = []
        [self.switch_list.append(switch) for switch in switch_list]
