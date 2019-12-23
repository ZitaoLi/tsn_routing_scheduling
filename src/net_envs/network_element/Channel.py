from typing import List, Tuple


class Channel(object):
    vertexes: Tuple[int]  # two endpoints of channel
    data_rate: float  # bandwidth or speed of channel, whose unit is bit/ns
    propagation_delay: float  # propagation delay of channel
    error_rate: float  # error rate of channel, whose range covers [0, 1]

    # TODO Error Model

    def __init__(self,
                 vertexes: Tuple[int], data_rate: float = 0.0, error_rate: float = 0.0, propagation_delay: float = 0.0):
        self.vertexes = vertexes
        self.data_rate = data_rate
        self.error_rate = error_rate
        self.propagation_delay = propagation_delay

    def reset(self, data_rate: float = 0.0, error_rate: float = 0.0, propagation_delay: float = 0.0):
        self.data_rate = data_rate
        self.error_rate = error_rate
        self.propagation_delay = propagation_delay


class FullDuplexChannel(Channel):
    pass


class HalfDuplexChannel(Channel):
    pass


class WirelessChannel(HalfDuplexChannel):
    pass
