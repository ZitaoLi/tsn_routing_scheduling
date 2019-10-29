import abc

from src.net_envs.network_component.FilteringDatabase import FilteringDatabase
from src.net_envs.network_element.NetworkDevice import NetworkDevice
from src.type import NodeId, NodeName


class Switch(NetworkDevice):
    filtering_database: FilteringDatabase  # interface

    def __init__(self, switch_id: NodeId, switch_name: NodeName):
        super().__init__(switch_id, switch_name)
        # self.filtering_db = FilteringDatabase()  # initialize filtering database
        # self.gate_control_list = GateControlList()  # initialize gate control list

    def forward(self):
        '''
        forward packet
        :return:
        '''
        pass

    def set_filtering_database(self, filtering_database: FilteringDatabase):
        if not hasattr(self, 'filtering_database'):
            self.filtering_database = filtering_database
        elif self.filtering_database is None:
            self.filtering_database = filtering_database
