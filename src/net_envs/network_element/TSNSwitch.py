from typing import Dict, Tuple, List

from src.net_envs.network_component.GateControlList import GateControlList
from src.net_envs.network_element.Switch import Switch
from src.type import NodeId, NodeName, PortNo, EdgeId


class TSNSwitch(Switch):
    port_gate_control_list: Dict[PortNo, GateControlList]

    def __init__(self, switch_id: NodeId, switch_name: NodeName):
        super().__init__(switch_id, switch_name)
        self.port_gate_control_list = {}

    def forward(self):
        super().forward()

    # # TODO extract common behavior
    # def set_gate_control_list(self, gate_control_list: GateControlList):
    #     if not hasattr(self, 'gate_control_list'):
    #         self.gate_control_list = gate_control_list
    #     elif self.gate_control_list is None:
    #         self.gate_control_list = gate_control_list
