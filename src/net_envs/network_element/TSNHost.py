from src.net_envs.network_component.GateControlList import GateControlList
from src.net_envs.network_element.Host import Host
from src.type import NodeId, NodeName


class TSNHost(Host):
    gate_control_list: GateControlList

    def __init__(self, switch_id: NodeId, switch_name: NodeName):
        super().__init__(switch_id, switch_name)
        self.gate_control_list = GateControlList()  # initialize gate control list

    @abc.abstractmethod
    def send(self):
        pass