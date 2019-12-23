# channel-configurator, derived class of network-configurator
import abc

from src.net_envs.network_configurator.NetworkConfigurator import NetworkConfigurator
from src.net_envs.network_element.Channel import Channel


class ChannelConfigurator(NetworkConfigurator):

    @abc.abstractmethod
    def configure(self, channel: Channel):
        pass
