import abc
from typing import Tuple

from src.net_envs.network_element.Channel import Channel, FullDuplexChannel, HalfDuplexChannel, WirelessChannel
from src.type import NodeId
from src.utils.Singleton import SingletonMetaclass


class ChannelFactory(object, metaclass=SingletonMetaclass):

    def product(self, vertexes: Tuple[NodeId]) -> Channel:
        channel: Channel = Channel(vertexes)
        return channel


class FullDuplexChannelFactory(ChannelFactory):

    def product(self, vertexes: Tuple[NodeId]) -> FullDuplexChannel:  # TODO
        channel: Channel = super().product(vertexes)
        channel.__class__ = FullDuplexChannel
        full_duplex_channel: FullDuplexChannel = channel
        return full_duplex_channel


class HalfDuplexChannelFactory(ChannelFactory):  # TODO

    def product(self, vertexes: Tuple[NodeId]) -> HalfDuplexChannel:
        channel: Channel = super().product(vertexes)
        channel.__class__ = HalfDuplexChannel
        half_duplex_channel: HalfDuplexChannel = channel
        return half_duplex_channel


class WirelessChannelFactory(HalfDuplexChannelFactory):  # TODO

    def product(self, vertexes: Tuple[NodeId]) -> WirelessChannel:
        channel: Channel = super().product(vertexes)
        channel.__class__ = WirelessChannel
        wireless_channel: WirelessChannel = channel
        return wireless_channel
