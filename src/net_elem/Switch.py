import abc

from src.net_elem.FilteringDatabase import FilteringDatabase
from src.net_elem.GateControlList import GateControlList
from src.net_elem.NetworkDevice import NetworkDevice
from src.type import NodeId, NodeName


class Switch(NetworkDevice):
    __metaclass__ = abc.ABCMeta

    filtering_db: FilteringDatabase  # interface
    # gate_control_list: GateControlList

    def __init__(self, switch_id: NodeId, switch_name: NodeName):
        super().__init__(switch_id, switch_name)
        # self.filtering_db = FilteringDatabase()  # initialize filtering database
        # self.gate_control_list = GateControlList()  # initialize gate control list

    @abc.abstractmethod
    def forward(self):
        '''
        forward packet
        :return:
        '''
        pass


class TSNSwitch(Switch):
    gate_control_list: GateControlList  # interface

    def __init__(self, switch_id: NodeId, switch_name: NodeName):
        super().__init__(switch_id, switch_name)
        # self.gate_control_list = GateControlList()  # initialize gate control list

    @abc.abstractmethod
    def forward(self):
        super().forward()
