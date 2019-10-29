# host-configurator
from src.net_envs.network_configurator.NetworkDeviceConfigurator import NetworkDeviceConfigurator
from src.net_envs.network_element.Host import Host


class HostConfigurator(NetworkDeviceConfigurator):

    def configure(self, host: Host):
        pass
