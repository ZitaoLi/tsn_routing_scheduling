from typing import List

from bitarray import bitarray

ALL_CLOSED_GATE_STATES: bitarray = bitarray([0, 0, 0, 0, 0, 0, 0, 0])  # all closed
ALL_OPEN_GATE_STATES: bitarray = bitarray([1, 1, 1, 1, 1, 1, 1, 1])  # all open
EXCLUSIVE_TSN_GATE_STATES: bitarray = bitarray([1, 0, 0, 0, 0, 0, 0, 0])  # exclusive tsn open
EXCLUSIVE_NON_TSN_GATE_STATES: bitarray = bitarray([0, 1, 1, 1, 1, 1, 1, 1])  # exclusive non-tsn open


class GateControlListItem(object):
    time: int  # length of time
    gate_states: bitarray  # gate state bit array

    def __init__(self, time: int = 0, gate_states: bitarray = ALL_OPEN_GATE_STATES):
        self.time = time
        self.gate_states = gate_states


class EnhancementGateControlListItem(GateControlListItem):
    flow_id: int
    phase: int

    def __init__(self, time: int = 0, gate_states: bitarray = ALL_OPEN_GATE_STATES,
                 flow_id: int = 0, phase: int = 0):
        super().__init__(time, gate_states)
        self.flow_id = flow_id  # flow id = 0 means non-flow
        self.phase = phase


class GateControlList(object):
    items: List[GateControlListItem]

    def __init__(self):
        self.items = []

    def add_item(self, item: GateControlListItem):
        self.items.append(item)


class EnhancementGateControlList(GateControlList):
    def __init__(self):
        super().__init__()