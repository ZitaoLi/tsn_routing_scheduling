import abc
from typing import Tuple

from src.net_elem.Channel import Channel, FullDuplexChannel, HalfDuplexChannel, WirelessChannel
from src.type import NodeId
from src.utils.Singleton import SingletonDecorator


@SingletonDecorator
class ChannelFactory(object):
    __metaclass__ = abc.ABCMeta  # use abstract class metaclass to control the creation behaviour of class

    @abc.abstractmethod
    def product(self, vertexes: Tuple[NodeId]) -> Channel:
        channel: Channel = Channel(vertexes)
        return channel


@SingletonDecorator
class FullDuplexChannelFactory(ChannelFactory):
    @abc.abstractmethod
    def product(self, vertexes: Tuple[NodeId]) -> FullDuplexChannel:  # TODO
        channel: Channel = super().product(vertexes)
        channel.__class__ = FullDuplexChannel
        full_duplex_channel: FullDuplexChannel = channel
        return full_duplex_channel


@SingletonDecorator
class HalfDuplexChannelFactory(ChannelFactory):  # TODO
    @abc.abstractmethod
    def product(self, vertexes: Tuple[NodeId]) -> HalfDuplexChannel:
        channel: Channel = super().product(vertexes)
        channel.__class__ = HalfDuplexChannel
        half_duplex_channel: HalfDuplexChannel = channel
        return half_duplex_channel


class WirelessChannelFactory(HalfDuplexChannelFactory):  # TODO
    @abc.abstractmethod
    def product(self, vertexes: Tuple[NodeId]) -> WirelessChannel:
        channel: Channel = super().product(vertexes)
        channel.__class__ = WirelessChannel
        wireless_channel: WirelessChannel = channel
        return wireless_channel
