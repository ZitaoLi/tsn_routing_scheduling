from typing import List

from src.net_envs.network_element.Channel import Channel
from src.net_envs.network_element.NetworkDevice import NetworkDevice
from src.utils.ToString import ToString


class Network(ToString):
    network_device_list: List[NetworkDevice]
    channel_list: List[Channel]

    def __init__(self):
        self.network_device_list = []
        self.channel_list = []

    def add_network_devices(self, network_device_list: List[NetworkDevice]):
        [self.network_device_list.append(network_device) for network_device in network_device_list]

    def add_channels(self, channel_list: List[Channel]):
        [self.channel_list.append(channel) for channel in channel_list]
