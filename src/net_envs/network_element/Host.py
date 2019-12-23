import abc

from src.net_envs.network_element.HostInterface import HostInterface
from src.net_envs.network_element.NetworkDevice import NetworkDevice
from src.type import NodeId, NodeName


class Host(NetworkDevice, HostInterface):

    def __init__(self, host_id: NodeId, host_name: NodeName):
        super().__init__(host_id, host_name)
        # self.gate_control_list = GateControlList()  # initialize gate control list

    def send(self):
        pass
