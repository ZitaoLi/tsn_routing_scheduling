from src.net_envs.network_component.GateControlList import GateControlList
from src.net_envs.network_element.Switch import Switch
from src.type import NodeId, NodeName


class TSNSwitch(Switch):
    gate_control_list: GateControlList  # interface

    def __init__(self, switch_id: NodeId, switch_name: NodeName):
        super().__init__(switch_id, switch_name)
        # self.gate_control_list = GateControlList()  # initialize gate control list

    def forward(self):
        super().forward()

    def set_gate_control_list(self, gate_control_list: GateControlList):
        if not hasattr(self, 'gate_control_list'):
            self.gate_control_list = gate_control_list
        elif self.filtering_database is None:
            self.gate_control_list = gate_control_list
