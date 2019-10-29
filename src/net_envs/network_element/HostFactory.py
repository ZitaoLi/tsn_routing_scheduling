from src import config
from src.net_envs.network_element.Host import Host
from src.net_envs.network_element.NetworkDeviceFactory import NetworkDeviceFactory


class HostFactory(NetworkDeviceFactory):
    def product(self, unique_id: int) -> Host:
        host: Host = \
            self.get_instance_from_class_name(
                'Host', 'Host', prefix_name=config.XML_CONFIG['tsn_host_pre_name'], unique_id=unique_id)
        return host
