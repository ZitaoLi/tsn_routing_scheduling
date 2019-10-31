from typing import List

from src.net_envs.network.EthernetNetwork import EthernetNetwork
from src.net_envs.network_element.TSNHost import TSNHost
from src.net_envs.network_element.TSNSwitch import TSNSwitch


class TSNNetwork(EthernetNetwork):
    tsn_switch_list: List[TSNSwitch]
    tsn_host_list: List[TSNHost]

    def __init__(self):
        super().__init__()
        self.tsn_switch_list = []
        self.tsn_host_list = []

    def add_tsn_hosts(self, tsn_host_list: List[TSNHost]):
        if hasattr(self, 'tsn_host_list') is False:
            self.tsn_host_list = []
        [self.tsn_host_list.append(tsn_host) for tsn_host in tsn_host_list]

    def add_tsn_switches(self, tsn_switch_list: List[TSNSwitch]):
        if hasattr(self, 'tsn_switch_list') is False:
            self.tsn_switch_list = []
        [self.tsn_switch_list.append(tsn_switch) for tsn_switch in tsn_switch_list]
