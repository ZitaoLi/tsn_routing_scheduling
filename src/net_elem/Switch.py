from src.net_elem.FilteringDatabase import FilteringDatabase
from src.net_elem.GateControlList import GateControlList
from src.net_elem.NetworkDevice import NetworkDevice, MAC_TYPE


class Switch(NetworkDevice):
    filtering_db: FilteringDatabase
    gate_control_list: GateControlList

    def __init__(self, switch_id: int, switch_name: str):
        super().__init__(switch_id, switch_name)
        self.filtering_db = FilteringDatabase()  # initialize filtering database
        self.gate_control_list = GateControlList()  # initialize gate control list
