from typing import List

from bitarray import bitarray


class GateControlListItem(object):
    time: int  # length of time
    gate_states: bitarray  # gate state bit array

    def __init__(self):
        self.time = 0
        self.gate_states = bitarray([0, 0, 0, 0, 0, 0, 0, 0])

    def reset(self, time: int = 0, gate_states: bitarray = bitarray([0, 0, 0, 0, 0, 0, 0, 0])):
        self.time = time
        self.gate_states = gate_states


class EnhancementGateControlListItem(GateControlListItem):
    flow_id: int
    phase: int

    def __init__(self):
        super().__init__()
        self.flow_id = 0  # flow id = 0 means non-flow
        self.phase = 0

    def reset(self, time: int = 0, gate_states: bitarray = bitarray([0, 0, 0, 0, 0, 0, 0, 0]),
              flow_id: int = 0, phase: int = 0):
        super().reset(time, gate_states)
        self.flow_id = flow_id
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