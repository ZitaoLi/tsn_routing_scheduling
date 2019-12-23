from typing import List

from bitarray import bitarray

from src.type import SimTime, FlowId

ALL_CLOSED_GATE_STATES: bitarray = bitarray([0, 0, 0, 0, 0, 0, 0, 0])  # all closed
ALL_OPEN_GATE_STATES: bitarray = bitarray([1, 1, 1, 1, 1, 1, 1, 1])  # all open
# EXCLUSIVE_TSN_GATE_STATES: bitarray = bitarray([1, 0, 0, 0, 0, 0, 0, 0])  # exclusive tsn open
EXCLUSIVE_TSN_GATE_STATES: bitarray = bitarray([0, 0, 0, 0, 0, 0, 0, 1])  # exclusive tsn open
EXCLUSIVE_NON_TSN_GATE_STATES: bitarray = bitarray([0, 1, 1, 1, 1, 1, 1, 1])  # exclusive non-tsn open


class GateControlListItem(object):
    time: SimTime  # length of time
    gate_states: bitarray  # gate state bit array

    def __init__(self, time: SimTime = 0.0, gate_states: bitarray = ALL_OPEN_GATE_STATES):
        self.time = time
        self.gate_states = gate_states


class EnhancementGateControlListItem(GateControlListItem):
    flow_id: FlowId
    phase: int

    def __init__(self, time: SimTime = 0.0, gate_states: bitarray = ALL_OPEN_GATE_STATES,
                 flow_id: FlowId = 0, phase: int = 0):
        super().__init__(time, gate_states)
        self.flow_id = flow_id  # flow id = 0 means non-flow
        self.phase = phase


class GateControlList(object):
    items: List[GateControlListItem]

    def __init__(self):
        self.items = []

    def add_item(self, item: GateControlListItem):
        self.items.append(item)

    def product_and_add_item(self, time: SimTime = 0.0, gate_states: bitarray = ALL_OPEN_GATE_STATES):
        self.items.append(GateControlListItem(time, gate_states))


class EnhancementGateControlList(GateControlList):
    def __init__(self):
        super().__init__()

    def product_and_add_item(self, time: SimTime = 0.0, gate_states: bitarray = ALL_OPEN_GATE_STATES,
                             flow_id: FlowId = FlowId(0), phase: int = 0):
        self.items.append(EnhancementGateControlListItem(time, gate_states, flow_id, phase))
