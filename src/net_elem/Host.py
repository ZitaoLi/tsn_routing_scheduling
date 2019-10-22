from src.net_elem.GateControlList import GateControlList
from src.net_elem.NetworkDevice import NetworkDevice


class Host(NetworkDevice):
    gate_control_list: GateControlList

    def __init__(self, switch_id: int, switch_name: str):
        super().__init__(switch_id, switch_name)
        self.gate_control_list = GateControlList()  # initialize gate control list
