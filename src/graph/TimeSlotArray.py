import logging
from math import floor

logger = logging.getLogger(__name__)
MinFrameSize = 64 * 8  # minimal frame size = 64B


class TimeSlotArray:
    def __init__(self, edge_id, hp=0, b=0, s=MinFrameSize):
        self.edge_id = edge_id
        self.hyper_period = hp
        self.bandwidth = b
        self.flow_size = s
        self.time_slot_array = []
        self.load = 0  # load of edge
        self.flow_num = 0  # number of flow traversed on edge
        self.flow_segment_num = 0  # number of continuous flow traversed on edge

        self.init()

    def init(self):
        '''
        initialize time slots
        :return:
        '''
        if self.hyper_period == 0 or self.bandwidth == 0:
            logger.info('lack of some necessary properties for the initialization of time slots')
            return False
        n = floor(self.hyper_period * self.bandwidth / self.flow_size)
        logger.info('number of time slots of edge [' + str(self.edge_id) + '] = ' + str(n))
        self.time_slot_array = [0] * n

    def set_bandwidth(self, b):
        '''
        change bandwidth will change time slots at the same time
        :param b: bandwidth
        :return:
        '''
        self.bandwidth = b
        self.init()

    def set_hyper_period(self, hp):
        self.hyper_period = hp

    def allocate(self, start_offset, allocation_len, step_num, step_len):
        '''
        allocate time slots
        :param start_offset: start position of flow allocation
        :param allocation_len: time slots number needed for flow
        :param step_num: step number = hyper period / period of flow
        :param step_len: period of flow
        :return:
        '''
        if step_len < allocation_len:
            return False  # [Error] step length cannot satisfy requirement of time slots
        for i in range(step_num):
            current_offset = start_offset * (step_num - 1)
            for j in range(allocation_len):
                if self.time_slot_array[current_offset] == 1:
                    return False  # [Error] this time slot has been allocated
                self.time_slot_array[current_offset] = 1
                current_offset += 1
        return True

    def try_allocate(self):
        pass
