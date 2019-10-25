import abc
from typing import List

from src.net_elem.Channel import Channel
from src.net_elem.Host import Host, TSNHost
from src.net_elem.NetworkDevice import NetworkDevice
from src.net_elem.Switch import Switch, TSNSwitch


class Network(object, metaclass=abc.ABCMeta):
    network_device_list: List[NetworkDevice]
    channel_list: List[Channel]

    def __init__(self):
        self.network_device_list = []
        self.channel_list = []

    def add_network_devices(self, network_device_list: List[NetworkDevice]):
        [self.network_device_list.append(network_device) for network_device in network_device_list]

    def add_channels(self, channel_list: List[Channel]):
        [self.channel_list.append(channel) for channel in channel_list]


class EthernetNetwork(Network):
    switch_list: List[Switch]
    host_list: List[Host]

    def __init__(self):
        super().__init__()
        self.switch_list = []
        self.host_list = []

    def add_hosts(self, host_list: List[Host]):
        [self.host_list.append(host) for host in host_list]

    def add_switches(self, switch_list: List[Switch]):
        [self.switch_list.append(switch) for switch in switch_list]


class TSNNetwork(EthernetNetwork):
    tsn_switch_list: List[Switch]
    tsn_host_list: List[Host]

    def __init__(self):
        super().__init__()
        self.tsn_switch_list = []
        self.tsn_host_list = []

    def add_tsn_hosts(self, tsn_host_list: List[TSNHost]):
        [self.tsn_host_list.append(tsn_host) for tsn_host in tsn_host_list]

    def add_tsn_switches(self, tsn_switch_list: List[TSNSwitch]):
        [self.tsn_switch_list.append(tsn_switch) for tsn_switch in tsn_switch_list]
