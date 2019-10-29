from typing import List

from src.net_envs.network.Network import Network
from src.net_envs.network_element.Host import Host
from src.net_envs.network_element.Switch import Switch


class EthernetNetwork(Network):
    switch_list: List[Switch] = []
    host_list: List[Host] = []

    def __init__(self):
        super().__init__()
        self.switch_list = []
        self.host_list = []

    def add_hosts(self, host_list: List[Host]):
        [self.host_list.append(host) for host in host_list]

    def add_switches(self, switch_list: List[Switch]):
        [self.switch_list.append(switch) for switch in switch_list]
