from typing import Dict, List

from src.net_envs.network_component.GateControlList import GateControlList
from src.net_envs.network_element.Host import Host
from src.type import NodeId, NodeName, PortNo, FlowId, SimTime, QueueId, MacAddress


class TSNFlowInfo(object):
    flow_id: FlowId
    start_time: SimTime
    cycle_time: SimTime
    size: int
    queue: QueueId
    dest_mac: MacAddress
    group_mac: MacAddress

    def __init__(self, flow_id: FlowId = 0,
                 start_time: SimTime = SimTime(0),
                 size: int = 0,
                 cycle_time: SimTime = SimTime(0),
                 queue: QueueId = QueueId(7),
                 dest_mac: MacAddress = MacAddress(''),
                 group_mac: MacAddress = MacAddress('')):
        self.flow_id = flow_id
        self.start_time = start_time
        self.size = size
        self.cycle_time = cycle_time
        self.queue = queue
        self.dest_mac = dest_mac
        self.group_mac = group_mac


class TSNHost(Host):
    port_gate_control_list: Dict[PortNo, GateControlList]
    tsn_flow_info_list: List[TSNFlowInfo]

    def __init__(self, switch_id: NodeId, switch_name: NodeName):
        super().__init__(switch_id, switch_name)
        self.port_gate_control_list = {}
        self.tsn_flow_info_list = []

    def send(self):
        pass

    # # TODO extract common behavior
    # def set_gate_control_list(self, gate_control_list: GateControlList):
    #     if not hasattr(self, 'gate_control_list'):
    #         self.gate_control_list = gate_control_list
    #     elif self.gate_control_list is None:
    #         self.gate_control_list = gate_control_list
