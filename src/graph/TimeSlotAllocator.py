import logging
import json
from typing import List, Dict

from math import ceil
from math import floor
from intervals import IntInterval

from src import config
from src.graph.Flow import Flow

logger = logging.getLogger(__name__)
MinFrameSize = 64 * 8  # minimal frame size = 64B, unit: Byte


class AllocationBlock:
    flow_id: int
    phase: int
    arrival_time_offset: int
    send_time_offset: int
    interval: IntInterval

    def __init__(self, flow_id, interval: IntInterval, at_offset: int, st_offset: int, phase: int = 0):
        self.flow_id = flow_id
        self.interval = interval
        self.arrival_time_offset = at_offset
        self.send_time_offset = st_offset
        self.phase = phase


class TimeSlotAllocator:
    edge_id: int
    __hyper_period: int  # hyper period of all flows, [unit: us]
    bandwidth: float  # bandwidth on edge, [unit: bps]
    propagation_delay: int
    process_delay: int
    min_flow_size: int  # minimal flow size, [unit: b]
    flow_times_mapper: Dict[int, List[AllocationBlock]]
    flow_times_mapper_c: Dict[int, List[AllocationBlock]]
    # flow_times_mapper: dict[int, list[AllocationBlock]]
    allocation_blocks: List[AllocationBlock]  # time windows without merging operation
    allocation_blocks_c: List[AllocationBlock]
    allocation_blocks_m: List[AllocationBlock]  # time windows with merging operation
    allocation_blocks_m_c: List[AllocationBlock]
    time_slot_len: int  # time slot length, [unit: us]
    time_slot_num: int  # number of time slots
    load: float  # load of edge
    load_c: float
    time_slot_used: int  # time slot that be used by flow
    time_slot_used_c: int
    flow_num: int  # number of flow traversed on edge
    flow_num_c: int
    flow_segment_num: int  # number of continuous flow traversed on edge
    flow_segment_num_c: int

    def __init__(self, edge_id: int, hp: int = 0, b: float = 0, s: int = config.GRAPH_CONFIG['min-flow-size'],
                 prop_d: int = 0, proc_d: int = 0):
        self.edge_id = edge_id
        self.__hyper_period = hp
        self.bandwidth = b
        self.min_flow_size = s
        self.propagation_delay = prop_d
        self.process_delay = proc_d
        self.reset()

    @property
    def hyper_period(self):
        return self.__hyper_period

    @hyper_period.setter
    def hyper_period(self, hyper_period: int):
        if hyper_period != self.__hyper_period:
            self.__hyper_period = hyper_period
            self.reset()
            logger.info('time slots allocation on edge [' + str(self.edge_id) + '] has been reset')
        else:
            logger.info('time slots of edge [' + str(self.edge_id) + '] has no change')

    def to_string(self):
        _B: List[List[int]] = []
        for _block in self.allocation_blocks:
            _interval: IntInterval = _block.interval
            _B.append([_interval.lower, _interval.upper])
        _B_m: List[List[int]] = []
        for _block_m in self.allocation_blocks_m:
            _interval: IntInterval = _block_m.interval
            _B_m.append([_interval.lower, _interval.upper])
        o = {
            'edge id': self.edge_id,
            'hyper_period': str(self.__hyper_period) + ' ns',
            'bandwidth': str(self.bandwidth) + ' b/ns',
            'min_flow_size': str(self.min_flow_size) + ' b',
            'time_slot_len': str(self.time_slot_len) + ' ns',
            'time_slot_num': self.time_slot_num,
            'load': str(self.load * 100) + '%',
            'time_slots_used': self.time_slot_used,
            'flow_num': self.flow_num,
            'flow_segment_num': self.flow_segment_num,
            'raw allocation blocks num': len(self.allocation_blocks),
            'raw_allocation_blocks': _B,
            'merged allocation blocks num': len(self.allocation_blocks_m),
            'merged_allocation_blocks': _B_m,
        }
        _json = json.dumps(o)
        logger.info(_json)

    def save_scene(self):
        self.allocation_blocks_c = self.allocation_blocks.copy()
        self.allocation_blocks_m_c = self.allocation_blocks_m.copy()
        self.flow_times_mapper_c = self.flow_times_mapper.copy()
        self.flow_num_c = self.flow_num
        self.flow_segment_num_c = self.flow_segment_num
        self.load_c = self.load
        self.time_slot_used_c = self.time_slot_used

    def recover_scene(self):
        self.allocation_blocks = self.allocation_blocks_c.copy()
        self.allocation_blocks_m = self.allocation_blocks_m_c.copy()
        self.flow_times_mapper = self.flow_times_mapper_c.copy()
        self.flow_num = self.flow_num_c
        self.flow_segment_num = self.flow_segment_num_c
        self.load = self.load_c
        self.time_slot_used = self.time_slot_used_c

    def reset(self):
        self.flow_times_mapper = {}  # clear flow-time-slots mapper when hyper period changes
        self.allocation_blocks = []  # clear time slot allocation
        self.allocation_blocks_m = []  # clear merged time slot allocation
        self.allocation_blocks_c = []
        self.allocation_blocks_m_c = []
        self.load = 0
        self.load_c = 0
        self.time_slot_used = 0
        self.time_slot_used_c = 0
        self.flow_num = 0
        self.flow_num_c = 0
        self.flow_segment_num = 0
        if self.bandwidth != 0 and self.min_flow_size != 0 and self.__hyper_period:
            self.time_slot_len = ceil(self.min_flow_size / self.bandwidth)
            # self.time_slot_num = floor(self.__hyper_period / self.time_slot_len)
            self.time_slot_len = ceil(self.min_flow_size / config.GRAPH_CONFIG['max-bandwidth'])  # TODO fix bug here
            self.time_slot_num = floor(self.__hyper_period / self.time_slot_len)
        else:
            self.time_slot_len = 0
            self.time_slot_num = 0
        self.to_string()

    def set_bandwidth(self, b: float) -> bool:
        '''
        change bandwidth will affect time slots at the same time
        :param b: bandwidth
        :return: None
        '''
        if b != self.bandwidth:
            self.bandwidth = b
            self.reset()
            logger.info('time slots allocation on edge [' + str(self.edge_id) + '] has been reset')
        else:
            logger.info('time slots of edge [' + str(self.edge_id) + '] has no change')

    def set_hyper_period(self, hp: int):
        '''
        change hyper period will affect time slot map at the same time
        :param hp: hyper period
        :return:
        '''
        if hp != self.__hyper_period:
            self.__hyper_period = hp
            self.reset()
            logger.info('time slots allocation on edge [' + str(self.edge_id) + '] has been reset')
        else:
            logger.info('time slots of edge [' + str(self.edge_id) + '] has no change')

    def allocate(self, flow: Flow, arrival_time_offset, send_time_offset: int, phase_num: int, allocation_num: int):
        for _phase in range(phase_num):
            _block_num: int = len(self.allocation_blocks)
            _block_m_num: int = len(self.allocation_blocks_m)
            _lower: int = floor(send_time_offset % self.hyper_period / self.time_slot_len)
            # _lower: int = floor(send_time_offset % (self.time_slot_num * self.time_slot_len) / self.time_slot_len)
            _upper: int = _lower + allocation_num - 1
            _blocks: List[AllocationBlock] = []
            # create time slots allocation blocks
            if _lower < self.time_slot_num:
                if _upper < self.time_slot_num:
                    _interval: IntInterval = IntInterval.closed(_lower, _upper)
                    _block = AllocationBlock(
                        flow.flow_id, _interval,
                        at_offset=arrival_time_offset, st_offset=send_time_offset, phase=_phase)
                    _blocks = [_block]
                else:
                    _lower_0 = _lower
                    _upper_0 = self.time_slot_num - 1
                    _interval_0 = IntInterval.closed(_lower_0, _upper_0)
                    _block_0 = AllocationBlock(
                        flow.flow_id, _interval_0,
                        at_offset=arrival_time_offset, st_offset=send_time_offset, phase=_phase)
                    _lower_1 = 0
                    _upper_1 = _upper % self.time_slot_num
                    _interval_1 = IntInterval.closed(_lower_1, _upper_1)
                    _block_1 = AllocationBlock(
                        flow.flow_id, _interval_1,
                        at_offset=arrival_time_offset, st_offset=send_time_offset, phase=_phase)
                    _blocks = [_block_0, _block_1]
            else:
                logger.error('fuck damn!')
            # insert directly without merge operation
            for __block in _blocks:
                if len(self.allocation_blocks) == 0:
                    self.allocation_blocks.append(__block)
                else:
                    for _i, block in enumerate(self.allocation_blocks):
                        if __block.interval.lower <= block.interval.lower:
                            self.allocation_blocks.insert(_i, __block)
                            break
                        else:
                            if _i >= _block_num - 1:
                                self.allocation_blocks.insert(_i + 1, __block)
                                break
            if _phase == 0:
                _next_arrival_time_offset = \
                    send_time_offset + flow.period + self.propagation_delay + self.process_delay
            # add blocks to flow-time-slots mapper
            if flow.flow_id in self.flow_times_mapper:
                for __block in _blocks:
                    self.flow_times_mapper[flow.flow_id].append(__block)
            else:
                __blocks: List[AllocationBlock] = _blocks.copy()
                self.flow_times_mapper[flow.flow_id] = __blocks
            # insert with merging operation
            for __block in _blocks:
                if len(self.allocation_blocks_m) == 0:
                    self.allocation_blocks_m.append(__block)
                else:
                    for _i, block_m in enumerate(self.allocation_blocks_m):
                        if __block.interval.lower <= block_m.interval.lower:
                            self.allocation_blocks_m.insert(_i, __block)
                            if __block.interval.upper in block_m.interval and __block.flow_id == block_m.flow_id:
                                __block.interval.upper = block_m.interval.upper
                                del self.allocation_blocks_m[_i + 1]
                            if _i != 0:
                                _pre_block_m: AllocationBlock = self.allocation_blocks_m[_i - 1]
                                if __block.interval.lower in _pre_block_m.interval and __block.flow_id == block_m.flow_id:
                                    __block.interval.lower = _pre_block_m.interval.lower
                                    del self.allocation_blocks_m[_i - 1]
                            break
                        else:
                            if _i >= _block_m_num - 1:
                                self.allocation_blocks_m.insert(_i + 1, __block)
                                _pre_block_m: AllocationBlock = self.allocation_blocks_m[_i]
                                if __block.interval.lower in _pre_block_m.interval and __block.flow_id == block_m.flow_id:
                                    __block.interval.lower = _pre_block_m.interval.lower
                                    del self.allocation_blocks_m[_i]
                                break
            # compute edge load and time slot that used by flow
            _sum: int = 0
            for _block_m in self.allocation_blocks_m:
                _sum += _block_m.interval.upper - _block_m.interval.lower + 1
            self.time_slot_used = _sum
            self.load = self.time_slot_used / self.time_slot_num
            # if flow not exit, then the number of flow add 1
            if flow.flow_id not in self.flow_times_mapper:
                self.flow_num += 1
            # add to next phase
            send_time_offset += flow.period

    def allocate_aeap_overlap(self, flow: Flow, arrival_time_offset: int) -> int:
        allocation_num: int = ceil(flow.size / self.bandwidth / self.time_slot_len)  # needed time slots
        phase_num: int = ceil(self.hyper_period / flow.period)  # number of repetitions
        _send_time_offset: int = 0
        _next_arrival_time_offset: int = 0
        _B: List[AllocationBlock] = self.flow_times_mapper.get(flow.flow_id)
        _flag: bool = False
        if _B is not None:
            _b: AllocationBlock = list(filter(lambda b: b.phase == 0, _B))[0]
            # if arrival time offset dost not exceed send time offset, then we can delay it and make it overlapped fully
            # otherwise, we can just allocate it as early as possible
            if arrival_time_offset <= _b.send_time_offset:
                _send_time_offset = _b.send_time_offset
                if self.try_allocate(_send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period,
                                     overlaped=True):
                    self.allocate(flow, arrival_time_offset, _send_time_offset, phase_num, allocation_num)
                    _flag = True
                else:
                    logger.error('allocate time slots error on edge [' + str(self.edge_id) + ']')
                    logger.error('send time offset: ' + str(_send_time_offset))
                    logger.error('error interval: ' + str([_b.interval.lower, _b.interval.upper]))
                    # self.to_string()
                    return -1
        if _flag is False:
            _send_time_offset = arrival_time_offset
            # flow cannot be delayed more than (number of time slots on edge - number of needed time slots)
            for _i in range(self.time_slot_num - allocation_num):
                if self.try_allocate(_send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period):
                    self.allocate(flow, arrival_time_offset, _send_time_offset, phase_num, allocation_num)
                    _flag = True
                    break
                _send_time_offset += self.time_slot_len
        # allocation failure
        if _flag is False:
            logger.info('allocate time slots for flow [' + str(flow.flow_id) + '] failure')
            return -1
        else:
            _next_arrival_time_offset = \
                _send_time_offset + (allocation_num * self.time_slot_len) + self.propagation_delay + self.process_delay
            self.to_string()
            return _next_arrival_time_offset

    def allocate_aeap(self, flow: Flow, arrival_time_offset: int) -> int:
        allocation_num: int = ceil(flow.size / self.bandwidth / self.time_slot_len)  # needed time slots
        phase_num: int = ceil(self.hyper_period / flow.period)  # number of repetitions
        _send_time_offset: int = arrival_time_offset
        _next_arrival_time_offset: int = 0
        _flag: bool = False
        # flow cannot be delayed more than (number of time slots on edge - number of needed time slots)
        for _i in range(self.time_slot_num - allocation_num):
            if self.try_allocate(_send_time_offset, flow.flow_id, allocation_num, phase_num, flow.period,
                                 overlaped=True):
                self.allocate(flow, arrival_time_offset, _send_time_offset, phase_num, allocation_num)
                _flag = True
                break
            _send_time_offset += self.time_slot_len
        # allocation failure
        if _flag is False:
            logger.info('allocate time slots for flow [' + str(flow.flow_id) + '] failure')
            return -1
        else:
            _next_arrival_time_offset = \
                _send_time_offset + (allocation_num * self.time_slot_len) + self.propagation_delay + self.process_delay
            self.to_string()
            return _next_arrival_time_offset

    @staticmethod
    def _is_same_flow(id1: int, id2: int, offset1: int, offset2: int, allocation_num: int) -> bool:
        if id1 == id2:
            if abs(offset1 - offset2) >= allocation_num:
                return False
            else:
                return True
        else:
            return False

    def try_allocate(self, time_offset: int, flow_id: int, allocation_num: int, phase_num: int, bp: int,
                     overlaped=False) -> bool:
        '''
        brute force method to check whether flow can be allocated or not
        :param time_offset:
        :param flow_id:
        :param allocation_num:
        :param phase_num:
        :param bp:
        :return:
        '''
        if self.time_slot_num == 0:
            logger.error('time slots on edge [' + str(self.edge_id) + '] does not initialize')
            return False
        if bp < allocation_num:
            logger.error('required time slots exceed base period')
            return False
        for phase in range(phase_num):
            # _lower: int = floor(time_offset % self.hyper_period / self.time_slot_len)
            _lower: int = floor(time_offset % (self.time_slot_num * self.time_slot_len) / self.time_slot_len)
            _upper: int = _lower + allocation_num - 1
            _intervals: List[IntInterval] = []
            if _lower < self.time_slot_num:
                if _upper < self.time_slot_num:
                    _interval: IntInterval = IntInterval.closed(_lower, _upper)
                    _intervals: List[IntInterval] = [_interval]
                else:
                    _lower_0 = _lower
                    _upper_0 = self.time_slot_num - 1
                    _interval_0 = IntInterval.closed(_lower_0, _upper_0)
                    _lower_1 = 0
                    _upper_1 = _upper % self.time_slot_num
                    _intervals = []
                    _interval_1 = IntInterval.closed(_lower_1, _upper_1)
                    _intervals = [_interval_0, _interval_1]
            else:
                logger.error('lower bound exceed number of time slots')
                return False
            if overlaped is True:
                for __interval in _intervals:
                    for block in self.allocation_blocks:
                        fid = block.flow_id
                        if __interval.lower in block.interval and __interval.upper in block.interval:
                            if not self._is_same_flow(fid, flow_id, time_offset, block.send_time_offset,
                                                      allocation_num):
                                return False
                        elif __interval.lower in block.interval and __interval.upper > block.interval.upper:
                            if not self._is_same_flow(fid, flow_id, time_offset, block.send_time_offset,
                                                      allocation_num):
                                return False
                        elif __interval.upper in block.interval and __interval.lower < block.interval.lower:
                            if not self._is_same_flow(fid, flow_id, time_offset, block.send_time_offset,
                                                      allocation_num):
                                return False
                        elif block.interval.lower in __interval and block.interval.upper in __interval:
                            if not self._is_same_flow(fid, flow_id, time_offset, block.send_time_offset,
                                                      allocation_num):
                                return False
            else:
                for __interval in _intervals:
                    for block in self.allocation_blocks:
                        if __interval.lower in block.interval and __interval.upper in block.interval:
                            return False
                        elif __interval.lower in block.interval and __interval.upper > block.interval.upper:
                            return False
                        elif __interval.upper in block.interval and __interval.lower < block.interval.lower:
                            return False
                        elif block.interval.lower in __interval and block.interval.upper in __interval:
                            return False
            time_offset += bp
        return True

    def try_allocate_smart(self, time_offset: int, flow_id: int, allocation_num: int, phase_num: int, bp: int) -> bool:
        '''
        smart method to check whether flow can be allocated or not
        :param time_offset:
        :param flow_id:
        :param allocation_num:
        :param phase_num:
        :param bp:
        :return:
        '''
        pass
