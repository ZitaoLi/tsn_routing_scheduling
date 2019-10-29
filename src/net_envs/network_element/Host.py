import abc

from src.net_envs.network_element.NetworkDevice import NetworkDevice
from src.type import NodeId, NodeName


class Host(NetworkDevice):
    # gate_control_list: GateControlList

    def __init__(self, switch_id: NodeId, switch_name: NodeName):
        super().__init__(switch_id, switch_name)
        # self.gate_control_list = GateControlList()  # initialize gate control list

    def send(self):
        pass
