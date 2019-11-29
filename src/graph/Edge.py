from enum import Enum

from .Node import Node
from .TimeSlotArray import TimeSlotArray
from .TimeSlotAllocator import TimeSlotAllocator

EdgeColor = Enum('EdgeColor', ('RED', 'WHITE'))
EdgeType = Enum('EdgeType', ('HOST_TO_SWITCH', 'SWITCH_TO_SWITCH'))


class Edge:
    edge_id: int  # id
    in_node: Node  # inbound port
    out_node: Node  # outbound port
    edge: tuple  # edge tuple
    bandwidth: int  # bandwidth or speed
    error_rate: float  # bandwidth or speed
    propagation_delay: int  # propagation delay
    process_delay: int  # process delay
    weight: int  # weight
    weight_c: int
    color: int  # color
    time_slot_array: TimeSlotArray  # time slots on edge, deprecated
    time_slot_allocator: TimeSlotAllocator  # time slot allocator
    type: int  # type, [host-to-switch or switch-to-switch]
    __hyper_period: int  # hyper period of all flows

    def __init__(self, edge_id: int, in_node: Node, out_node: Node, b: int = 0, e_rate: float = 0, prop_d: int = 0,
                 proc_d: int = 0, hp: int = 0):
        '''
        :param edge_id: edge id [required]
        :param in_node: inbound node [required]
        :param out_node: outbound node [required]
        :param b: bandwidth [default=0]
        :param e_rate: error rate [default=0]
        :param p_delay: propagation delay [default=0]
        '''
        self.edge_id = edge_id
        self.in_node = in_node
        self.out_node = out_node
        self.edge = (in_node, out_node)
        self.bandwidth = b
        self.error_rate = e_rate
        self.propagation_delay = prop_d
        self.process_delay = proc_d
        self.weight = 0
        self.weight_c = 0
        self.color = EdgeColor.RED
        self.type = EdgeType.HOST_TO_SWITCH
        self.__hyper_period = hp
        self.init_time_slot_allocator()  # initialize time slot allocator
        # self.init_time_slot_array()

    def init_time_slot_allocator(self):
        self.time_slot_allocator = TimeSlotAllocator(self.edge_id, hp=self.__hyper_period, b=self.bandwidth,
                                                     prop_d=self.propagation_delay, proc_d=self.process_delay)

    def init_time_slot_array(self):
        self.time_slot_array = TimeSlotArray(self.edge_id, hp=self.__hyper_period, b=self.bandwidth)

    def set_process_delay(self, proc_d: int):
        self.process_delay = proc_d

    def set_propagation_delay(self, prop_d: int):
        self.propagation_delay = prop_d

    def set_error_rate(self, e_rate: float):
        self.error_rate = e_rate

    def set_bandwidth(self, b: int):
        self.bandwidth = b
        self.time_slot_allocator.set_bandwidth(b)
        # self.time_slot_array.set_bandwidth(b)

    @property
    def hyper_period(self):
        return self.__hyper_period

    @hyper_period.setter
    def hyper_period(self, hyper_period: int):
        self.__hyper_period = hyper_period
        self.time_slot_allocator.hyper_period = hyper_period
